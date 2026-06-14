from datetime import date, datetime

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy import Date, MetaData, Table, and_, cast, func, insert, select, update
from sqlalchemy.orm import Session

from ...database import engine, get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.LugaresModel import LugaresModel
from ...schemas import MovimientosCreate
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])


_metadata = MetaData()
_movimientos = Table("invMovimientos", _metadata, autoload_with=engine)
_usuarios = Table("invUsuarios", _metadata, autoload_with=engine)
_tipomoves = Table("invTipoMoves", _metadata, autoload_with=engine)
_roles = Table("invRoles", _metadata, autoload_with=engine)
_status_usuarios = Table("invStatusUsuarios", _metadata, autoload_with=engine)
_status_devices = Table("invStatusDevices", _metadata, autoload_with=engine)


def _json_safe_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    return value


def _usuario_exists(db: Session, usuario_id: int) -> bool:
    stmt = select(_usuarios.c.id).where(_usuarios.c.id == usuario_id).limit(1)
    return db.execute(stmt).scalar_one_or_none() is not None


def _tipo_mov_exists(db: Session, tipo_mov_id: int) -> bool:
    stmt = select(_tipomoves.c.id).where(_tipomoves.c.id == tipo_mov_id).limit(1)
    return db.execute(stmt).scalar_one_or_none() is not None


def _base_movimiento_join_stmt():
    device_tbl = DispositivosModel.__table__
    lugar_tbl = LugaresModel.__table__

    device_lugar = lugar_tbl.alias("device_lugar")
    mov_lugar = lugar_tbl.alias("mov_lugar")

    stmt = (
        select(
            _movimientos.c.id.label("movimiento_id"),
            _movimientos.c.idMovimiento.label("movimiento_idMovimiento"),
            _movimientos.c.dispositivoId.label("movimiento_dispositivoId"),
            _movimientos.c.usuarioId.label("movimiento_usuarioId"),
            _movimientos.c.tipoMovId.label("movimiento_tipoMovId"),
            _movimientos.c.LugarId.label("movimiento_LugarId"),
            _movimientos.c.comentarios.label("movimiento_comentarios"),
            _movimientos.c.foto.label("movimiento_foto"),
            _movimientos.c.foto2.label("movimiento_foto2"),
            _movimientos.c.fechaAlta.label("movimiento_fechaAlta"),
            _movimientos.c.fechaUltimaModificacion.label("movimiento_fechaUltimaModificacion"),
            _movimientos.c.cantidad_Actual.label("movimiento_cantidad_Actual"),
            device_tbl.c.id.label("dispositivo_id"),
            device_tbl.c.codigo.label("dispositivo_codigo"),
            device_tbl.c.producto.label("dispositivo_producto"),
            device_tbl.c.marca.label("dispositivo_marca"),
            device_tbl.c.modelo.label("dispositivo_modelo"),
            device_tbl.c.origen.label("dispositivo_origen"),
            device_tbl.c.foto.label("dispositivo_foto"),
            device_tbl.c.cantidad.label("dispositivo_cantidad"),
            device_tbl.c.observaciones.label("dispositivo_observaciones"),
            device_tbl.c.lugarId.label("dispositivo_lugarId"),
            device_tbl.c.pertenece.label("dispositivo_pertenece"),
            device_tbl.c.descompostura.label("dispositivo_descompostura"),
            device_tbl.c.costo.label("dispositivo_costo"),
            device_tbl.c.compra.label("dispositivo_compra"),
            device_tbl.c.proveedor.label("dispositivo_proveedor"),
            device_tbl.c.idMov.label("dispositivo_idMov"),
            device_tbl.c.statusId.label("dispositivo_statusId"),
            device_tbl.c.serie.label("dispositivo_serie"),
            device_tbl.c.accesorios.label("dispositivo_accesorios"),
            device_lugar.c.id.label("dispositivo_lugar_id"),
            device_lugar.c.lugar.label("dispositivo_lugar_lugar"),
            device_lugar.c.activo.label("dispositivo_lugar_activo"),
            device_lugar.c.fechaAlta.label("dispositivo_lugar_fechaAlta"),
            device_lugar.c.fechaUltimaModificacion.label("dispositivo_lugar_fechaUltimaModificacion"),
            _status_devices.c.id.label("dispositivo_status_id"),
            _status_devices.c.descripcion.label("dispositivo_status_descripcion"),
            _status_devices.c.fechaAlta.label("dispositivo_status_fechaAlta"),
            _status_devices.c.fechaUltimaModificacion.label("dispositivo_status_fechaUltimaModificacion"),
            mov_lugar.c.id.label("lugar_id"),
            mov_lugar.c.lugar.label("lugar_lugar"),
            mov_lugar.c.activo.label("lugar_activo"),
            mov_lugar.c.fechaAlta.label("lugar_fechaAlta"),
            mov_lugar.c.fechaUltimaModificacion.label("lugar_fechaUltimaModificacion"),
            _tipomoves.c.id.label("tipoMovimiento_id"),
            _tipomoves.c.tipo.label("tipoMovimiento_tipo"),
            _tipomoves.c.fechaAlta.label("tipoMovimiento_fechaAlta"),
            _tipomoves.c.fechaUltimaModificacion.label("tipoMovimiento_fechaUltimaModificacion"),
            _usuarios.c.id.label("usuario_id"),
            _usuarios.c.nombre.label("usuario_nombre"),
            _usuarios.c.username.label("usuario_username"),
            _usuarios.c.apellidoPaterno.label("usuario_apellidoPaterno"),
            _usuarios.c.apellidoMaterno.label("usuario_apellidoMaterno"),
            _usuarios.c.password.label("usuario_password"),
            _usuarios.c.telefono.label("usuario_telefono"),
            _usuarios.c.correo.label("usuario_correo"),
            _usuarios.c.foto.label("usuario_foto"),
            _usuarios.c.rolId.label("usuario_rolId"),
            _usuarios.c.statusId.label("usuario_statusId"),
            _usuarios.c.fechaAlta.label("usuario_fechaAlta"),
            _usuarios.c.fechaUltimaModificacion.label("usuario_fechaUltimaModificacion"),
            _roles.c.id.label("usuario_rol_id"),
            _roles.c.nombre.label("usuario_rol_nombre"),
            _roles.c.fechaAlta.label("usuario_rol_fechaAlta"),
            _roles.c.fechaUltimaModificacion.label("usuario_rol_fechaUltimaModificacion"),
            _status_usuarios.c.id.label("usuario_status_obj_id"),
            _status_usuarios.c.descripcion.label("usuario_status_obj_descripcion"),
            _status_usuarios.c.fechaAlta.label("usuario_status_obj_fechaAlta"),
            _status_usuarios.c.fechaUltimaModificacion.label("usuario_status_obj_fechaUltimaModificacion"),
        )
        .select_from(
            _movimientos.join(device_tbl, device_tbl.c.id == _movimientos.c.dispositivoId)
            .outerjoin(device_lugar, device_lugar.c.id == device_tbl.c.lugarId)
            .outerjoin(_status_devices, _status_devices.c.id == device_tbl.c.statusId)
            .outerjoin(mov_lugar, mov_lugar.c.id == _movimientos.c.LugarId)
            .outerjoin(_tipomoves, _tipomoves.c.id == _movimientos.c.tipoMovId)
            .outerjoin(_usuarios, _usuarios.c.id == _movimientos.c.usuarioId)
            .outerjoin(_roles, _roles.c.id == _usuarios.c.rolId)
            .outerjoin(_status_usuarios, _status_usuarios.c.id == _usuarios.c.statusId)
        )
    )
    return stmt


def _build_movimiento_from_joined_row(row: dict) -> dict:
    movimiento = {
        "id": row.get("movimiento_id"),
        "idMovimiento": row.get("movimiento_idMovimiento"),
        "dispositivoId": row.get("movimiento_dispositivoId"),
        "usuarioId": row.get("movimiento_usuarioId"),
        "tipoMovId": row.get("movimiento_tipoMovId"),
        "LugarId": row.get("movimiento_LugarId"),
        "comentarios": row.get("movimiento_comentarios"),
        "foto": row.get("movimiento_foto"),
        "foto2": row.get("movimiento_foto2"),
        "fechaAlta": row.get("movimiento_fechaAlta"),
        "fechaUltimaModificacion": row.get("movimiento_fechaUltimaModificacion"),
        "cantidad_Actual": row.get("movimiento_cantidad_Actual"),
    }

    dispositivo = {
        "id": row.get("dispositivo_id"),
        "codigo": row.get("dispositivo_codigo"),
        "producto": row.get("dispositivo_producto"),
        "marca": row.get("dispositivo_marca"),
        "modelo": row.get("dispositivo_modelo"),
        "origen": row.get("dispositivo_origen"),
        "foto": row.get("dispositivo_foto"),
        "cantidad": row.get("dispositivo_cantidad"),
        "observaciones": row.get("dispositivo_observaciones"),
        "lugarId": row.get("dispositivo_lugarId"),
        "pertenece": row.get("dispositivo_pertenece"),
        "descompostura": row.get("dispositivo_descompostura"),
        "costo": row.get("dispositivo_costo"),
        "compra": row.get("dispositivo_compra"),
        "proveedor": row.get("dispositivo_proveedor"),
        "idMov": row.get("dispositivo_idMov"),
        "statusId": row.get("dispositivo_statusId"),
        "serie": row.get("dispositivo_serie"),
        "accesorios": row.get("dispositivo_accesorios"),
    }
    dispositivo_lugar = {
        "id": row.get("dispositivo_lugar_id"),
        "lugar": row.get("dispositivo_lugar_lugar"),
        "activo": row.get("dispositivo_lugar_activo"),
        "fechaAlta": row.get("dispositivo_lugar_fechaAlta"),
        "fechaUltimaModificacion": row.get("dispositivo_lugar_fechaUltimaModificacion"),
    }
    dispositivo_status = {
        "id": row.get("dispositivo_status_id"),
        "descripcion": row.get("dispositivo_status_descripcion"),
        "fechaAlta": row.get("dispositivo_status_fechaAlta"),
        "fechaUltimaModificacion": row.get("dispositivo_status_fechaUltimaModificacion"),
    }
    dispositivo["lugar"] = dispositivo_lugar if any(v is not None for v in dispositivo_lugar.values()) else None
    dispositivo["status"] = dispositivo_status if any(v is not None for v in dispositivo_status.values()) else None

    lugar = {
        "id": row.get("lugar_id"),
        "lugar": row.get("lugar_lugar"),
        "activo": row.get("lugar_activo"),
        "fechaAlta": row.get("lugar_fechaAlta"),
        "fechaUltimaModificacion": row.get("lugar_fechaUltimaModificacion"),
    }

    tipo_movimiento = {
        "id": row.get("tipoMovimiento_id"),
        "tipo": row.get("tipoMovimiento_tipo"),
        "fechaAlta": row.get("tipoMovimiento_fechaAlta"),
        "fechaUltimaModificacion": row.get("tipoMovimiento_fechaUltimaModificacion"),
    }

    usuario = {
        "id": row.get("usuario_id"),
        "nombre": row.get("usuario_nombre"),
        "username": row.get("usuario_username"),
        "apellidoPaterno": row.get("usuario_apellidoPaterno"),
        "apellidoMaterno": row.get("usuario_apellidoMaterno"),
        "password": row.get("usuario_password"),
        "telefono": row.get("usuario_telefono"),
        "correo": row.get("usuario_correo"),
        "foto": row.get("usuario_foto"),
        "rolId": row.get("usuario_rolId"),
        "statusId": row.get("usuario_statusId"),
        "fechaAlta": row.get("usuario_fechaAlta"),
        "fechaUltimaModificacion": row.get("usuario_fechaUltimaModificacion"),
    }
    usuario_rol = {
        "id": row.get("usuario_rol_id"),
        "nombre": row.get("usuario_rol_nombre"),
        "fechaAlta": row.get("usuario_rol_fechaAlta"),
        "fechaUltimaModificacion": row.get("usuario_rol_fechaUltimaModificacion"),
    }
    usuario_status = {
        "id": row.get("usuario_status_obj_id"),
        "descripcion": row.get("usuario_status_obj_descripcion"),
        "fechaAlta": row.get("usuario_status_obj_fechaAlta"),
        "fechaUltimaModificacion": row.get("usuario_status_obj_fechaUltimaModificacion"),
    }
    usuario["rol"] = usuario_rol if any(v is not None for v in usuario_rol.values()) else None
    usuario["status"] = usuario_status if any(v is not None for v in usuario_status.values()) else None

    movimiento["lugar"] = lugar if any(v is not None for v in lugar.values()) else None
    movimiento["dispositivo"] = dispositivo if any(v is not None for v in dispositivo.values()) else None
    movimiento["tipoMovimiento"] = tipo_movimiento if any(v is not None for v in tipo_movimiento.values()) else None
    movimiento["usuario"] = usuario if any(v is not None for v in usuario.values()) else None
    return _json_safe_value(movimiento)


def _fetch_movimiento_by_id(db: Session, movimiento_id: int) -> dict | None:
    stmt = _base_movimiento_join_stmt().where(_movimientos.c.id == movimiento_id).limit(1)
    row = db.execute(stmt).mappings().first()
    if not row:
        return None
    return _build_movimiento_from_joined_row(dict(row))


def _fetch_movimientos_some_fields(
    db: Session,
    offset: int,
    limit: int,
    search_value: str | None = None,
) -> tuple[list[dict], int]:
    base_stmt = (
        select(
            _movimientos.c.id,
            DispositivosModel.codigo,
            DispositivosModel.producto,
            _movimientos.c.fechaAlta,
            _movimientos.c.idMovimiento,
            LugaresModel.lugar,
            _tipomoves.c.tipo,
            _usuarios.c.nombre,
            _usuarios.c.username,
        )
        .select_from(
            _movimientos.join(DispositivosModel, DispositivosModel.id == _movimientos.c.dispositivoId)
            .outerjoin(LugaresModel, LugaresModel.id == _movimientos.c.LugarId)
            .outerjoin(_tipomoves, _tipomoves.c.id == _movimientos.c.tipoMovId)
            .outerjoin(_usuarios, _usuarios.c.id == _movimientos.c.usuarioId)
        )
    )

    filters = []
    if search_value:
        pattern = f"%{search_value}%"
        filters.append(
            (
                DispositivosModel.codigo.ilike(pattern)
                | DispositivosModel.producto.ilike(pattern)
                | _movimientos.c.idMovimiento.ilike(pattern)
                | LugaresModel.lugar.ilike(pattern)
                | _tipomoves.c.tipo.ilike(pattern)
                | _usuarios.c.nombre.ilike(pattern)
                | _usuarios.c.username.ilike(pattern)
            )
        )

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    if filters:
        count_stmt = select(func.count()).select_from(base_stmt.where(*filters).subquery())
    total_rows = int(db.execute(count_stmt).scalar() or 0)

    data_stmt = (
        base_stmt.where(*filters)
        .order_by(_movimientos.c.fechaAlta.desc())
        .offset(int(offset))
        .limit(int(limit))
    )

    rows = db.execute(data_stmt).mappings().all()
    serialized = [_json_safe_value(dict(row)) for row in rows]
    return serialized, total_rows


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
        movimientos = [MovimientosCreate.model_validate(item).model_dump(exclude_none=True) for item in movimientos_raw]
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
            stmt = (
                insert(_movimientos)
                .values(
                    idMovimiento=item.get("idMovimiento"),
                    dispositivoId=item.get("dispositivoId"),
                    usuarioId=item.get("usuarioId"),
                    tipoMovId=item.get("tipoMovId"),
                    LugarId=item.get("LugarId"),
                    comentarios=item.get("comentarios"),
                    foto=item.get("foto"),
                    foto2=item.get("foto2"),
                    fechaAlta=now,
                    fechaUltimaModificacion=now,
                    cantidad_Actual=cantidad_actual,
                )
                .returning(_movimientos.c.id)
            )
            created_id = int(db.execute(stmt).scalar_one())

            # Keep movement insert and device stock/location update in the same transaction.
            update_stmt = (
                update(DispositivosModel)
                .where(DispositivosModel.id == int(item.get("dispositivoId")))
                .values(
                    cantidad=int(diferencia),
                    lugarId=int(item.get("LugarId")),
                    fechaUltimaModificacion=now,
                )
            )
            updated_rows = db.execute(update_stmt).rowcount or 0
            if int(updated_rows) == 0:
                raise ValueError(f"No se pudo actualizar invDispositivos id={item.get('dispositivoId')}")

            db.commit()

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


@router.put("", summary="Actualizar movimiento")
async def movimientos_update(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")
    if payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    movimiento_id = int(payload.get("id"))
    exists = db.execute(select(_movimientos.c.id).where(_movimientos.c.id == movimiento_id).limit(1)).scalar_one_or_none()
    if not exists:
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
        stmt = update(_movimientos).where(_movimientos.c.id == movimiento_id).values(**update_values)
        db.execute(stmt)
        db.commit()

        movimiento_completo = _fetch_movimiento_by_id(db, movimiento_id)
        return fastapi_response(movimiento_completo, status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/LastOne/{id}", summary="Obtener ultimo movimiento por dispositivo")
async def movimientos_last_one(id: int, db: Session = Depends(get_db)) -> dict:
    stmt = (
        select(_movimientos.c.id)
        .where(and_(_movimientos.c.dispositivoId == id, _movimientos.c.tipoMovId == 1))
        .order_by(_movimientos.c.fechaAlta.desc())
        .limit(1)
    )
    last_mov_id = db.execute(stmt).scalar_one_or_none()
    if not last_mov_id:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    movimiento = _fetch_movimiento_by_id(db, int(last_mov_id))
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

    filters = []
    if "id" in payload and payload.get("id") is not None:
        filters.append(_movimientos.c.id == payload.get("id"))
    if "dispositivoId" in payload and payload.get("dispositivoId") is not None:
        filters.append(_movimientos.c.dispositivoId == payload.get("dispositivoId"))
    if "LugarId" in payload and payload.get("LugarId") is not None:
        filters.append(_movimientos.c.LugarId == payload.get("LugarId"))
    if "tipoMovId" in payload and payload.get("tipoMovId") is not None:
        filters.append(_movimientos.c.tipoMovId == payload.get("tipoMovId"))
    if "usuarioId" in payload and payload.get("usuarioId") is not None:
        filters.append(_movimientos.c.usuarioId == payload.get("usuarioId"))
    if "idMovimiento" in payload and payload.get("idMovimiento"):
        filters.append(_movimientos.c.idMovimiento.ilike(f"%{str(payload.get('idMovimiento')).strip()}%"))
    if "fechaAltaRangoInicio" in payload and payload.get("fechaAltaRangoInicio"):
        filters.append(cast(_movimientos.c.fechaAlta, Date) >= payload.get("fechaAltaRangoInicio"))
    if "fechaAltaRangoFin" in payload and payload.get("fechaAltaRangoFin"):
        filters.append(cast(_movimientos.c.fechaAlta, Date) <= payload.get("fechaAltaRangoFin"))

    if not filters:
        return fastapi_response([], status.HTTP_200_OK, "TPM-3")

    try:
        count_stmt = select(func.count()).select_from(_movimientos).where(*filters)
        total_rows = int(db.execute(count_stmt).scalar() or 0)

        id_stmt = (
            select(_movimientos.c.id)
            .where(*filters)
            .order_by(_movimientos.c.fechaAlta.desc())
            .offset(int(offset))
            .limit(int(limit))
        )
        ids = db.execute(id_stmt).scalars().all()

        if not ids:
            return fastapi_response([], status.HTTP_200_OK, "TPM-3")

        # Keep response order according to the paginated id list.
        index_by_id = {int(mov_id): idx for idx, mov_id in enumerate(ids)}
        rows_stmt = _base_movimiento_join_stmt().where(_movimientos.c.id.in_(list(index_by_id.keys())))
        rows = db.execute(rows_stmt).mappings().all()

        movimientos_unsorted = [_build_movimiento_from_joined_row(dict(row)) for row in rows]
        movimientos = sorted(
            movimientos_unsorted,
            key=lambda item: index_by_id.get(int(item.get("id")), 0),
        )

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
