from datetime import datetime, timedelta
import logging
import os
from threading import Lock

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...database import SessionLocal, get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.JobMovimientosModelSchema import JobMovimientosModel
from ...models.LugaresModel import LugaresModel
from ...models.MovimientosModelSchema import MovimientosModel, MovimientosSchemaCreate, MovimientosSchemaProcessRequest
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])
logger = logging.getLogger("uvicorn.error")
_active_movement_devices: set[int] = set()
_active_movement_devices_lock = Lock()
_movement_jobs_status: dict[str, dict] = {}
_movement_jobs_status_lock = Lock()
_MOVEMENT_JOB_STATUS_TTL = timedelta(days=1)
_MOVEMENT_JOB_STATUS_MAX_ENTRIES = int(os.getenv("MOVEMENT_JOB_STATUS_MAX_ENTRIES", "500"))


def _usuario_exists(db: Session, usuario_id: int) -> bool:
    return MovimientosModel.usuario_exists(db, usuario_id)


def _tipo_mov_exists(db: Session, tipo_mov_id: int) -> bool:
    return MovimientosModel.tipo_mov_exists(db, tipo_mov_id)


def _fetch_movimiento_by_id(db: Session, movimiento_id: int) -> dict | None:
    return MovimientosModel.fetch_by_id(db, movimiento_id)


def _fetch_movimientos_some_fields(
    db: Session,
    offset: int,
    limit: int,
    search_value: str | None = None,
) -> tuple[list[dict], int]:
    return MovimientosModel.fetch_some_fields(db, offset, limit, search_value)


def _claim_movement_devices(dispositivo_ids: list[int]) -> list[int]:
    with _active_movement_devices_lock:
        overlapping_ids = sorted(device_id for device_id in set(dispositivo_ids) if device_id in _active_movement_devices)
        if overlapping_ids:
            return overlapping_ids

        _active_movement_devices.update(dispositivo_ids)
        return []


def _release_movement_devices(dispositivo_ids: list[int]) -> None:
    with _active_movement_devices_lock:
        for device_id in set(dispositivo_ids):
            _active_movement_devices.discard(device_id)


def _create_job_status(id_movimiento: str, dispositivo_ids: list[int]) -> None:
    _cleanup_expired_job_statuses()
    with _movement_jobs_status_lock:
        # Keep a bounded in-memory cache to avoid unbounded growth in long-lived workers.
        while len(_movement_jobs_status) >= _MOVEMENT_JOB_STATUS_MAX_ENTRIES:
            oldest_job_id = min(
                _movement_jobs_status,
                key=lambda job_id: _movement_jobs_status[job_id].get("started_at", ""),
            )
            _movement_jobs_status.pop(oldest_job_id, None)

        _movement_jobs_status[id_movimiento] = {
            "idMovimiento": id_movimiento,
            "status": "queued",
            "requested_devices": len(dispositivo_ids),
            "processed_devices": [],
            "failed_devices": [],
            "skipped_devices": [],
            "started_at": datetime.utcnow().isoformat(),
            "finished_at": None,
            "expires_at": None,
            "last_error": None,
        }


def _cleanup_expired_job_statuses() -> None:
    now = datetime.utcnow()
    with _movement_jobs_status_lock:
        expired_job_ids = [
            job_id
            for job_id, job_status in _movement_jobs_status.items()
            if job_status.get("expires_at") and datetime.fromisoformat(job_status["expires_at"]) <= now
        ]

        for job_id in expired_job_ids:
            _movement_jobs_status.pop(job_id, None)


def _update_job_status(id_movimiento: str, **updates) -> None:
    with _movement_jobs_status_lock:
        job_status = _movement_jobs_status.get(id_movimiento)
        if not job_status:
            return
        job_status.update(updates)


def _append_job_status_device(id_movimiento: str, key: str, dispositivo_id: int) -> None:
    with _movement_jobs_status_lock:
        job_status = _movement_jobs_status.get(id_movimiento)
        if not job_status:
            return
        bucket = job_status.setdefault(key, [])
        if dispositivo_id not in bucket:
            bucket.append(dispositivo_id)


def _get_job_status(id_movimiento: str) -> dict | None:
    _cleanup_expired_job_statuses()
    with _movement_jobs_status_lock:
        job_status = _movement_jobs_status.get(id_movimiento)
        if not job_status:
            return None

        return {
            "idMovimiento": job_status.get("idMovimiento"),
            "status": job_status.get("status"),
            "requested_devices": job_status.get("requested_devices"),
            "processed_devices": list(job_status.get("processed_devices", [])),
            "failed_devices": list(job_status.get("failed_devices", [])),
            "skipped_devices": list(job_status.get("skipped_devices", [])),
            "started_at": job_status.get("started_at"),
            "finished_at": job_status.get("finished_at"),
            "expires_at": job_status.get("expires_at"),
            "last_error": job_status.get("last_error"),
        }


def _finalize_job_status(id_movimiento: str, status_value: str, last_error: str | None = None) -> None:
    finished_at = datetime.utcnow()
    _update_job_status(
        id_movimiento,
        status=status_value,
        finished_at=finished_at.isoformat(),
        expires_at=(finished_at + _MOVEMENT_JOB_STATUS_TTL).isoformat(),
        last_error=last_error,
    )


def _create_job_db_record(payload: dict) -> None:
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        JobMovimientosModel.create_job(
            db,
            {
                "idMovimiento": str(payload.get("idMovimiento")),
                "usuarioId": int(payload.get("usuarioId")),
                "tipoMovId": int(payload.get("tipoMovId")),
                "LugarId": int(payload.get("LugarId")),
                "comentarios": payload.get("comentarios"),
                "estado": "job iniciado y en proceso",
                "status": 1,
                "fechaAlta": now,
                "fechaUltimaModificacion": now,
            },
        )
    except Exception:
        logger.exception("[MOV-API] No se pudo crear registro en invJobMovimientos para idMovimiento=%s", payload.get("idMovimiento"))
    finally:
        db.close()


def _set_job_db_status(id_movimiento: str, status_code: int, estado: str, error_message: str | None = None) -> None:
    db = SessionLocal()
    try:
        row = JobMovimientosModel.get_latest_by_id_movimiento(db, id_movimiento)
        if not row:
            return

        update_data = {
            "status": int(status_code),
            "estado": estado,
            "fechaUltimaModificacion": datetime.utcnow(),
        }
        if error_message:
            update_data["comentarios"] = f"{row.comentarios or ''} | error: {error_message}".strip(" |")

        row.update(db, update_data)
    except Exception:
        logger.exception("[MOV-BG] No se pudo actualizar invJobMovimientos para idMovimiento=%s", id_movimiento)
    finally:
        db.close()


def _process_movements_job(payload: dict) -> None:
    logger.debug("[MOV-BG] Iniciando proceso de movimientos masivo")
    db = SessionLocal()
    dispositivo_ids = [int(dispositivo_id) for dispositivo_id in (payload.get("dispositivoId") or [])]
    id_movimiento = str(payload.get("idMovimiento"))
    try:
        _update_job_status(id_movimiento, status="processing")
        _set_job_db_status(id_movimiento, 1, "job en proceso")
        usuario_id = int(payload.get("usuarioId"))
        comentarios = payload.get("comentarios")
        lugar_id = int(payload.get("LugarId"))
        tipo_mov_id = int(payload.get("tipoMovId"))

        logger.info(
            "[MOV-BG] payload valido: total_dispositivos=%s usuarioId=%s lugarId=%s tipoMovId=%s",
            len(dispositivo_ids),
            usuario_id,
            lugar_id,
            tipo_mov_id,
        )

        for dispositivo_id in dispositivo_ids:
            dispositivo = DispositivosModel.get_one_device(db, int(dispositivo_id))
            if not dispositivo:
                _append_job_status_device(id_movimiento, "skipped_devices", int(dispositivo_id))
                continue

            cantidad_actual = 1
            diferencia = dispositivo.cantidad or 0
            if tipo_mov_id == 1:
                diferencia = (dispositivo.cantidad or 0) - cantidad_actual
            elif tipo_mov_id == 2:
                diferencia = (dispositivo.cantidad or 0) + cantidad_actual

            if diferencia < 0:
                _append_job_status_device(id_movimiento, "failed_devices", int(dispositivo_id))
                continue

            if tipo_mov_id == 2 and lugar_id == 1 and int(dispositivo.lugarId or 0) == 1:
                _append_job_status_device(id_movimiento, "skipped_devices", int(dispositivo_id))
                continue

            now = datetime.utcnow()
            movimiento_data = {
                "idMovimiento": id_movimiento,
                "dispositivoId": int(dispositivo_id),
                "usuarioId": usuario_id,
                "tipoMovId": tipo_mov_id,
                "LugarId": lugar_id,
                "comentarios": comentarios,
                "fechaAlta": now,
                "fechaUltimaModificacion": now,
                "cantidad_Actual": cantidad_actual,
            }

            max_reintentos = 3
            procesado = False
            for intento in range(1, max_reintentos + 1):
                try:
                    movimiento_obj = MovimientosModel(movimiento_data)
                    db.add(movimiento_obj)

                    dispositivo.cantidad = int(diferencia)
                    dispositivo.lugarId = lugar_id
                    dispositivo.fechaUltimaModificacion = now
                    db.add(dispositivo)

                    db.commit()
                    procesado = True
                    logger.info(
                        "[MOV-BG] Movimiento procesado con exito: dispositivoId=%s usuarioId=%s lugarId=%s tipoMovId=%s intento=%s",
                        dispositivo_id,
                        usuario_id,
                        lugar_id,
                        tipo_mov_id,
                        intento,
                    )
                    _append_job_status_device(id_movimiento, "processed_devices", int(dispositivo_id))
                    break
                except Exception as err:
                    db.rollback()
                    _update_job_status(id_movimiento, last_error=str(err))
                    logger.exception(
                        "Error procesando movimiento masivo para dispositivoId=%s, usuarioId=%s, lugarId=%s, tipoMovId=%s intento=%s/%s",
                        dispositivo_id,
                        usuario_id,
                        lugar_id,
                        tipo_mov_id,
                        intento,
                        max_reintentos,
                    )
                    if intento < max_reintentos:
                        db.expire_all()

            if not procesado:
                _append_job_status_device(id_movimiento, "failed_devices", int(dispositivo_id))
                continue
    except Exception as err:
        _finalize_job_status(id_movimiento, "failed", str(err))
        _set_job_db_status(id_movimiento, 2, "job con fallo", str(err))
        logger.exception("[MOV-BG] Error general procesando job idMovimiento=%s", id_movimiento)
    finally:
        job_status = _get_job_status(id_movimiento)
        if job_status and job_status.get("status") != "failed":
            final_status = "completed"
            final_status_code = 3
            final_status_message = "job terminado exitosamente"
            if job_status.get("failed_devices") or job_status.get("skipped_devices"):
                final_status = "completed_with_errors"
                final_status_code = 2
                final_status_message = "job terminado con errores"
            _finalize_job_status(id_movimiento, final_status, job_status.get("last_error"))
            _set_job_db_status(id_movimiento, final_status_code, final_status_message, job_status.get("last_error"))

        _release_movement_devices(dispositivo_ids)
        db.close()
        logger.info("[MOV-BG] Proceso de movimientos masivo finalizado, Conexion a DB cerrada")

    logger.info("[MOV-BG] Proceso de movimientos masivo finalizado")


@router.get("", summary="Listar movimientos")
async def movimientos_list(
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> dict:
    try:
        movimientos, total_rows = _fetch_movimientos_some_fields(db, offset, limit)
        return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.post("", summary="Crear movimiento")
async def movimientos_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    try:
        movimientos_raw = payload.get("movimientosList", payload)
        if isinstance(movimientos_raw, dict):
            movimientos_raw = [movimientos_raw]
        if not isinstance(movimientos_raw, list):
            raise ValueError("movimientosList debe ser una lista")
        movimientos = [MovimientosSchemaCreate.model_validate(item).model_dump(exclude_none=True) for item in movimientos_raw]
    except Exception as err:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message=str(err))

    lista_objetos_creados = []
    lista_errores = []

    for item in movimientos:
        dispositivo = DispositivosModel.get_one_device(db, item.get("dispositivoId"))
        if not dispositivo:
            lista_errores.append(partial_response("TPM-5", "el dispositivo no existe", item.get("dispositivoId"), item.get("id", 0)))
            continue

        lugar = LugaresModel.get_one_lugar(db, item.get("LugarId"))
        if not lugar:
            lista_errores.append(partial_response("TPM-4", "el lugar no existe", item.get("LugarId"), item.get("id", 0)))
            continue

        if not _usuario_exists(db, int(item.get("usuarioId"))):
            lista_errores.append(partial_response("TPM-5", "el usuario no existe", item.get("usuarioId"), item.get("id", 0)))
            continue

        if not _tipo_mov_exists(db, int(item.get("tipoMovId"))):
            lista_errores.append(partial_response("TPM-5", "el tipo de movimiento no existe", item.get("tipoMovId"), item.get("id", 0)))
            continue

        # Business rule: entrada (tipoMovId=2) to almacen (LugarId=1) is invalid
        # when the device is already located in almacen.
        if int(item.get("tipoMovId") or 0) == 2 and int(item.get("LugarId") or 0) == 1 and int(dispositivo.lugarId or 0) == 1:
            return fastapi_response(
                None,
                status.HTTP_409_CONFLICT,
                "TPM-20",
                items=[partial_response("TPM-20", name=str(item.get("dispositivoId")), id=item.get("id", 0))],
            )

        cantidad_actual = int(item.get("cantidad_Actual") or 1)
        if cantidad_actual <= 0:
            cantidad_actual = 1

        diferencia = dispositivo.cantidad or 0
        if item.get("tipoMovId") == 1:
            diferencia = (dispositivo.cantidad or 0) - cantidad_actual
        elif item.get("tipoMovId") == 2:
            diferencia = (dispositivo.cantidad or 0) + cantidad_actual

        if diferencia < 0:
            lista_errores.append(partial_response("TPM-17", "", item.get("dispositivoId"), item.get("id", 0)))
            continue

        now = datetime.utcnow()
        try:
            movimiento_data = dict(item)
            movimiento_data["fechaAlta"] = now
            movimiento_data["fechaUltimaModificacion"] = now
            movimiento_data["cantidad_Actual"] = cantidad_actual

            movimiento_obj = MovimientosModel(movimiento_data)
            db.add(movimiento_obj)

            # Keep movement insert and device stock/location update in the same transaction.
            dispositivo.cantidad = int(diferencia)
            dispositivo.lugarId = int(item.get("LugarId"))
            dispositivo.fechaUltimaModificacion = now
            db.add(dispositivo)

            db.commit()
            db.refresh(movimiento_obj)
            created_id = int(movimiento_obj.id)

            movimiento_completo = _fetch_movimiento_by_id(db, created_id)
            if movimiento_completo:
                lista_objetos_creados.append(movimiento_completo)
            else:
                lista_objetos_creados.append(
                    {
                        "id": created_id,
                        "dispositivoId": item.get("dispositivoId"),
                        "usuarioId": item.get("usuarioId"),
                        "idMovimiento": item.get("idMovimiento"),
                        "tipoMovId": item.get("tipoMovId"),
                        "LugarId": item.get("LugarId"),
                        "comentarios": item.get("comentarios"),
                        "foto": item.get("foto"),
                        "foto2": item.get("foto2"),
                        "cantidad_Actual": cantidad_actual,
                        "fechaAlta": now.isoformat(),
                        "fechaUltimaModificacion": now.isoformat(),
                    }
                )
        except Exception as err:
            db.rollback()
            lista_errores.append(partial_response("TPM-7", "", str(err), item.get("id", 0)))

    if len(lista_objetos_creados) > 0:
        if len(lista_errores) == 0:
            return fastapi_response(lista_objetos_creados, status.HTTP_201_CREATED, "TPM-8")
        return fastapi_response(lista_objetos_creados, status.HTTP_201_CREATED, "TPM-16", items=lista_errores)

    return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-16", items=lista_errores)


@router.post("/processMovements", summary="Procesar multiples movimientos")
async def process_movements(
    payload: MovimientosSchemaProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    _cleanup_expired_job_statuses()

    data = payload.model_dump(exclude_none=True)
    dispositivo_ids = [int(dispositivo_id) for dispositivo_id in (data.get("dispositivoId") or [])]
    id_movimiento = str(data.get("idMovimiento"))
    data["dispositivoId"] = dispositivo_ids

    logger.info("[MOV-API] Solicitud processMovements recibida: total_dispositivos=%s", len(dispositivo_ids))

    if len(dispositivo_ids) == 0:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-21")

    if not _usuario_exists(db, int(data.get("usuarioId"))):
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4", message="el usuario no existe")

    lugar = LugaresModel.get_one_lugar(db, int(data.get("LugarId")))
    if not lugar:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4", message="el lugar no existe")

    if not _tipo_mov_exists(db, int(data.get("tipoMovId"))):
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4", message="el tipo de movimiento no existe")

    tipo_mov_id = int(data.get("tipoMovId"))
    lugar_id = int(data.get("LugarId"))

    # Regla: salida (1) no puede tener almacen (LugarId=1).
    if tipo_mov_id == 1 and lugar_id == 1:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-22")

    # Regla: entrada (2) solo puede entrar a almacen (LugarId=1).
    if tipo_mov_id == 2 and lugar_id != 1:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-23")

    overlapping_ids = _claim_movement_devices(dispositivo_ids)
    if overlapping_ids:
        logger.warning(
            "[MOV-API] Conflicto processMovements: dispositivos en proceso=%s",
            overlapping_ids,
        )
        return fastapi_response(
            None,
            status.HTTP_409_CONFLICT,
            "TPM-24",
            message="al menos un dispositivo del job pasado esta en proceso y aun no ha terminado",
            items=[partial_response("TPM-24", name=",".join(str(device_id) for device_id in overlapping_ids))],
        )

    _create_job_status(id_movimiento, dispositivo_ids)
    _create_job_db_record(data)
    logger.info("[MOV-API] Encolando background task _process_movements_job")
    try:
        background_tasks.add_task(_process_movements_job, data)
    except Exception as err:
        _release_movement_devices(dispositivo_ids)
        _finalize_job_status(id_movimiento, "enqueue_failed", str(err))
        _set_job_db_status(id_movimiento, 2, "no se pudo encolar el job", str(err))
        logger.exception("[MOV-API] No se pudo agregar el nuevo job task: idMovimiento=%s", data.get("idMovimiento"))
        return fastapi_response(
            None,
            status.HTTP_409_CONFLICT,
            "TPM-25",
            message="No se pudo agregar el nuevo job task",
            items=[partial_response("TPM-25", message=str(err), name=str(data.get("idMovimiento") or ""))],
        )

    return fastapi_response(
        {"requested_devices": len(dispositivo_ids),"idMovimiento": data.get("idMovimiento")},
        status.HTTP_201_CREATED,
        "TPM-8",
        message="Proceso de movimientos generado correctamente",
    )


@router.get("/processMovements/status/{id_movimiento}", summary="Consultar estado de job processMovements")
async def process_movements_status(id_movimiento: str, db: Session = Depends(get_db)) -> dict:
    job_status = _get_job_status(id_movimiento)
    db_job_status = JobMovimientosModel.get_latest_by_id_movimiento(db, id_movimiento)

    if not job_status and not db_job_status:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4", message="job no encontrado")

    if not job_status and db_job_status:
        return fastapi_response(JobMovimientosModel.to_dict(db_job_status), status.HTTP_200_OK, "TPM-3")

    if db_job_status:
        job_status["jobDb"] = JobMovimientosModel.to_dict(db_job_status)

    return fastapi_response(job_status, status.HTTP_200_OK, "TPM-3")


@router.put("", summary="Actualizar movimiento")
async def movimientos_update(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")
    if payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    movimiento_id = int(payload.get("id"))
    movimiento_db = MovimientosModel.get_one_movimiento(db, movimiento_id)
    if not movimiento_db:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    dispositivo_id = payload.get("dispositivoId")
    if dispositivo_id is not None:
        exists_dispositivo = DispositivosModel.get_one_device(db, int(dispositivo_id))
        if not exists_dispositivo:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(dispositivo_id))])

    lugar_id = payload.get("LugarId")
    if lugar_id is not None:
        exists_lugar = LugaresModel.get_one_lugar(db, int(lugar_id))
        if not exists_lugar:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(lugar_id))])

    tipo_mov_id = payload.get("tipoMovId")
    if tipo_mov_id is not None and not _tipo_mov_exists(db, int(tipo_mov_id)):
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(tipo_mov_id))])

    usuario_id = payload.get("usuarioId")
    if usuario_id is not None and not _usuario_exists(db, int(usuario_id)):
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(usuario_id))])

    allowed_updates = {
        "dispositivoId": payload.get("dispositivoId"),
        "LugarId": payload.get("LugarId"),
        "tipoMovId": payload.get("tipoMovId"),
        "cantidad_Actual": payload.get("cantidad_Actual"),
        "usuarioId": payload.get("usuarioId"),
        "comentarios": payload.get("comentarios"),
        "idMovimiento": payload.get("idMovimiento"),
        "foto": payload.get("foto"),
        "foto2": payload.get("foto2"),
    }

    update_values = {k: v for k, v in allowed_updates.items() if v is not None}
    update_values["fechaUltimaModificacion"] = datetime.utcnow()

    try:
        for key, value in update_values.items():
            setattr(movimiento_db, key, value)
        db.add(movimiento_db)
        db.commit()

        movimiento_completo = _fetch_movimiento_by_id(db, movimiento_id)
        return fastapi_response(movimiento_completo, status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/LastOne/{id}", summary="Obtener ultimo movimiento por dispositivo")
async def movimientos_last_one(id: int, db: Session = Depends(get_db)) -> dict:
    last_mov = MovimientosModel.get_lastone_movimiento(db, id)
    if not last_mov:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    movimiento = _fetch_movimiento_by_id(db, int(last_mov.id))
    if not movimiento:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(movimiento, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar movimientos")
async def movimientos_query(
    payload: dict,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict:
    if payload is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    try:
        movimientos, total_rows = MovimientosModel.query_full(db, payload, offset, limit)
        if total_rows == 0:
            return fastapi_response([], status.HTTP_200_OK, "TPM-3")

        return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/filter", summary="Filtrar movimientos")
async def movimientos_filter(
    offset: int = 0,
    limit: int = 100,
    value: str = "",
    header_value: str | None = Header(default=None, alias="value"),
    db: Session = Depends(get_db),
) -> dict:
    search_value = (header_value or value or "").strip()

    try:
        movimientos, total_rows = _fetch_movimientos_some_fields(db, offset, limit, search_value)
        if not movimientos:
            return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
        return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/filtermovementFields", summary="Filtrar movimientos campos minimos")
async def movimientos_filter_fields(
    offset: int = 0,
    limit: int = 100,
    value: str = "",
    header_value: str | None = Header(default=None, alias="value"),
    db: Session = Depends(get_db),
) -> dict:
    search_value = (header_value or value or "").strip()

    try:
        movimientos, _ = _fetch_movimientos_some_fields(db, offset, limit, search_value)
        return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3")
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener movimiento por ID")
async def movimientos_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    movimiento = _fetch_movimiento_by_id(db, id)
    if not movimiento:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(movimiento, status.HTTP_200_OK, "TPM-3")
