from datetime import date, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.orm import Session

from ...database import engine, get_db
from ...models.DispositivosModel import DispositivosModel
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


_metadata = MetaData()
_reportes = Table("invReportes", _metadata, autoload_with=engine)
_dispositivos = DispositivosModel.__table__
_lugares = Table("invLugares", _metadata, autoload_with=engine)
_status_devices = Table("invStatusDevices", _metadata, autoload_with=engine)
_usuarios = Table("invUsuarios", _metadata, autoload_with=engine)
_roles = Table("invRoles", _metadata, autoload_with=engine)
_status_usuarios = Table("invStatusUsuarios", _metadata, autoload_with=engine)


def _json_safe_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    return value


def _base_reporte_join_stmt():
    device_lugar = _lugares.alias("device_lugar")

    return (
        select(
            _reportes.c.id.label("reporte_id"),
            _reportes.c.dispositivoId.label("reporte_dispositivoId"),
            _reportes.c.usuarioId.label("reporte_usuarioId"),
            _reportes.c.comentarios.label("reporte_comentarios"),
            _reportes.c.foto.label("reporte_foto"),
            _reportes.c.fechaAlta.label("reporte_fechaAlta"),
            _reportes.c.fechaUltimaModificacion.label("reporte_fechaUltimaModificacion"),
            _dispositivos.c.id.label("dispositivo_id"),
            _dispositivos.c.codigo.label("dispositivo_codigo"),
            _dispositivos.c.producto.label("dispositivo_producto"),
            _dispositivos.c.marca.label("dispositivo_marca"),
            _dispositivos.c.modelo.label("dispositivo_modelo"),
            _dispositivos.c.origen.label("dispositivo_origen"),
            _dispositivos.c.foto.label("dispositivo_foto"),
            _dispositivos.c.cantidad.label("dispositivo_cantidad"),
            _dispositivos.c.observaciones.label("dispositivo_observaciones"),
            _dispositivos.c.lugarId.label("dispositivo_lugarId"),
            _dispositivos.c.pertenece.label("dispositivo_pertenece"),
            _dispositivos.c.descompostura.label("dispositivo_descompostura"),
            _dispositivos.c.costo.label("dispositivo_costo"),
            _dispositivos.c.compra.label("dispositivo_compra"),
            _dispositivos.c.proveedor.label("dispositivo_proveedor"),
            _dispositivos.c.idMov.label("dispositivo_idMov"),
            _dispositivos.c.statusId.label("dispositivo_statusId"),
            _dispositivos.c.fechaAlta.label("dispositivo_fechaAlta"),
            _dispositivos.c.fechaUltimaModificacion.label("dispositivo_fechaUltimaModificacion"),
            _dispositivos.c.serie.label("dispositivo_serie"),
            _dispositivos.c.accesorios.label("dispositivo_accesorios"),
            device_lugar.c.id.label("dispositivo_lugar_id"),
            device_lugar.c.lugar.label("dispositivo_lugar_lugar"),
            device_lugar.c.activo.label("dispositivo_lugar_activo"),
            device_lugar.c.fechaAlta.label("dispositivo_lugar_fechaAlta"),
            device_lugar.c.fechaUltimaModificacion.label("dispositivo_lugar_fechaUltimaModificacion"),
            _status_devices.c.id.label("dispositivo_status_id"),
            _status_devices.c.descripcion.label("dispositivo_status_descripcion"),
            _status_devices.c.fechaAlta.label("dispositivo_status_fechaAlta"),
            _status_devices.c.fechaUltimaModificacion.label("dispositivo_status_fechaUltimaModificacion"),
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
            _reportes.join(_dispositivos, _dispositivos.c.id == _reportes.c.dispositivoId)
            .outerjoin(device_lugar, device_lugar.c.id == _dispositivos.c.lugarId)
            .outerjoin(_status_devices, _status_devices.c.id == _dispositivos.c.statusId)
            .outerjoin(_usuarios, _usuarios.c.id == _reportes.c.usuarioId)
            .outerjoin(_roles, _roles.c.id == _usuarios.c.rolId)
            .outerjoin(_status_usuarios, _status_usuarios.c.id == _usuarios.c.statusId)
        )
    )


def _build_reporte_from_row(row: dict) -> dict:
    reporte = {
        "id": row.get("reporte_id"),
        "dispositivoId": row.get("reporte_dispositivoId"),
        "usuarioId": row.get("reporte_usuarioId"),
        "comentarios": row.get("reporte_comentarios"),
        "foto": row.get("reporte_foto"),
        "fechaAlta": row.get("reporte_fechaAlta"),
        "fechaUltimaModificacion": row.get("reporte_fechaUltimaModificacion"),
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
        "fechaAlta": row.get("dispositivo_fechaAlta"),
        "fechaUltimaModificacion": row.get("dispositivo_fechaUltimaModificacion"),
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

    reporte["dispositivo"] = dispositivo if any(v is not None for v in dispositivo.values()) else None
    reporte["usuario"] = usuario if any(v is not None for v in usuario.values()) else None
    return _json_safe_value(reporte)


def _fetch_reporte_by_id(db: Session, reporte_id: int) -> dict | None:
    stmt = _base_reporte_join_stmt().where(_reportes.c.id == reporte_id).limit(1)
    row = db.execute(stmt).mappings().first()
    if not row:
        return None
    return _build_reporte_from_row(dict(row))


@router.get("", summary="Listar reportes")
async def reportes_list(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(_base_reporte_join_stmt().order_by(_reportes.c.id.desc())).mappings().all()
    reportes = [_build_reporte_from_row(dict(row)) for row in rows]
    return fastapi_response(reportes, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear reporte")
async def reportes_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    try:
        dispositivo_id = payload.get("dispositivoId")
        usuario_id = payload.get("usuarioId")
        comentarios = payload.get("comentarios")
        foto = payload.get("foto")

        existe_dispositivo = db.execute(select(_dispositivos.c.id).where(_dispositivos.c.id == dispositivo_id).limit(1)).scalar_one_or_none()
        if not existe_dispositivo:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(dispositivo_id))])

        existe_usuario = db.execute(select(_usuarios.c.id).where(_usuarios.c.id == usuario_id).limit(1)).scalar_one_or_none()
        if not existe_usuario:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(usuario_id))])

        now = datetime.utcnow()
        insert_stmt = (
            insert(_reportes)
            .values(
                dispositivoId=dispositivo_id,
                usuarioId=usuario_id,
                comentarios=comentarios,
                foto=foto,
                fechaAlta=now,
                fechaUltimaModificacion=now,
            )
            .returning(_reportes.c.id)
        )
        reporte_id = int(db.execute(insert_stmt).scalar_one())

        update_dispositivo_stmt = update(_dispositivos).where(_dispositivos.c.id == dispositivo_id).values(descompostura=comentarios)
        db.execute(update_dispositivo_stmt)
        db.commit()

        reporte_completo = _fetch_reporte_by_id(db, reporte_id)
        return fastapi_response(reporte_completo, status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar reporte")
async def reportes_update(payload: dict) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="reportes.update pendiente de migracion")


@router.get("/{id}", summary="Obtener reporte por ID")
async def reportes_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    reporte = _fetch_reporte_by_id(db, id)
    if not reporte:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(reporte, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar reportes")
async def reportes_query() -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="reportes.query pendiente de migracion")


@router.get("/filter/{value}", summary="Filtrar reportes")
async def reportes_filter(value: str) -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message=f"reportes.filter({value}) pendiente de migracion")
