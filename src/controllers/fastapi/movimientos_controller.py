from datetime import datetime
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...database import SessionLocal, get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.LugaresModel import LugaresModel
from ...models.MovimientosModelSchema import MovimientosModel, MovimientosSchemaCreate, MovimientosSchemaProcessRequest
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])
logger = logging.getLogger("uvicorn.error")


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


def _process_movements_job(payload: dict) -> None:
    logger.debug("[MOV-BG] Iniciando proceso de movimientos masivo")
    db = SessionLocal()
    try:
        dispositivo_ids = payload.get("dispositivoId") or []
        usuario_id = int(payload.get("usuarioId"))
        comentarios = payload.get("comentarios")
        lugar_id = int(payload.get("LugarId"))
        id_movimiento = payload.get("idMovimiento")
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
                continue

            cantidad_actual = 1
            diferencia = dispositivo.cantidad or 0
            if tipo_mov_id == 1:
                diferencia = (dispositivo.cantidad or 0) - cantidad_actual
            elif tipo_mov_id == 2:
                diferencia = (dispositivo.cantidad or 0) + cantidad_actual

            if diferencia < 0:
                continue

            if tipo_mov_id == 2 and lugar_id == 1 and int(dispositivo.lugarId or 0) == 1:
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

            try:
                movimiento_obj = MovimientosModel(movimiento_data)
                db.add(movimiento_obj)

                dispositivo.cantidad = int(diferencia)
                dispositivo.lugarId = lugar_id
                dispositivo.fechaUltimaModificacion = now
                db.add(dispositivo)

                db.commit()
                logger.info(
                    "[MOV-BG] Movimiento procesado con exito: dispositivoId=%s usuarioId=%s lugarId=%s tipoMovId=%s",
                    dispositivo_id,
                    usuario_id,
                    lugar_id,
                    tipo_mov_id,
                )
            except Exception as err:
                db.rollback()
                logger.exception(
                    "Error procesando movimiento masivo para dispositivoId=%s, usuarioId=%s, lugarId=%s, tipoMovId=%s",
                    dispositivo_id,
                    usuario_id,
                    lugar_id,
                    tipo_mov_id,
                )
                continue
    finally:
        db.close()
        logger.debug("[MOV-BG] Proceso de movimientos masivo finalizado")


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
    data = payload.model_dump(exclude_none=True)
    dispositivo_ids = data.get("dispositivoId") or []

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

    logger.info("[MOV-API] Encolando background task _process_movements_job")
    background_tasks.add_task(_process_movements_job, data)
    return fastapi_response(
        {"requested_devices": len(dispositivo_ids)},
        status.HTTP_201_CREATED,
        "TPM-8",
        message="Proceso de movimientos generado correctamente",
    )


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
