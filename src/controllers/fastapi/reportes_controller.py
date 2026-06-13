from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...database import get_db
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


def _json_safe_dict(record: dict | None) -> dict | None:
	if record is None:
		return None
	output = {}
	for key, value in record.items():
		if isinstance(value, datetime):
			output[key] = value.isoformat()
		else:
			output[key] = value
	return output


def _get_status_device(db: Session, status_id: int | None) -> dict | None:
	if status_id is None:
		return None
	query = text("SELECT id, descripcion, fechaAlta, fechaUltimaModificacion FROM invStatusDevices WHERE id = :id")
	row = db.execute(query, {"id": status_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_lugar(db: Session, lugar_id: int | None) -> dict | None:
	if lugar_id is None:
		return None
	query = text("SELECT id, lugar, activo, fechaAlta, fechaUltimaModificacion FROM invLugares WHERE id = :id")
	row = db.execute(query, {"id": lugar_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_rol(db: Session, rol_id: int | None) -> dict | None:
	if rol_id is None:
		return None
	query = text("SELECT id, nombre, fechaAlta, fechaUltimaModificacion FROM invRoles WHERE id = :id")
	row = db.execute(query, {"id": rol_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_status_usuario(db: Session, status_id: int | None) -> dict | None:
	if status_id is None:
		return None
	query = text("SELECT id, descripcion, fechaAlta, fechaUltimaModificacion FROM invStatusUsuarios WHERE id = :id")
	row = db.execute(query, {"id": status_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_dispositivo(db: Session, dispositivo_id: int | None) -> dict | None:
	if dispositivo_id is None:
		return None
	query = text(
		"""
		SELECT id, codigo, producto, marca, modelo, origen, foto, cantidad, observaciones, lugarId, pertenece,
			   descompostura, costo, compra, proveedor, idMov, statusId, fechaAlta, fechaUltimaModificacion,
			   serie, accesorios
		FROM invDispositivos
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": dispositivo_id}).mappings().first()
	if not row:
		return None
	dispositivo = _json_safe_dict(dict(row))
	dispositivo["lugar"] = _get_lugar(db, dispositivo.get("lugarId"))
	dispositivo["status"] = _get_status_device(db, dispositivo.get("statusId"))
	return dispositivo


def _get_usuario(db: Session, usuario_id: int | None) -> dict | None:
	if usuario_id is None:
		return None
	query = text(
		"""
		SELECT id, nombre, username, apellidoPaterno, apellidoMaterno, password, telefono, correo, foto, rolId, statusId,
			   fechaAlta, fechaUltimaModificacion
		FROM invUsuarios
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": usuario_id}).mappings().first()
	if not row:
		return None
	usuario = _json_safe_dict(dict(row))
	usuario["rol"] = _get_rol(db, usuario.get("rolId"))
	usuario["status"] = _get_status_usuario(db, usuario.get("statusId"))
	return usuario


def _build_reporte_response(db: Session, reporte_id: int) -> dict | None:
	query = text(
		"""
		SELECT id, dispositivoId, usuarioId, comentarios, foto, fechaAlta, fechaUltimaModificacion
		FROM invReportes
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": reporte_id}).mappings().first()
	if not row:
		return None
	reporte = _json_safe_dict(dict(row))
	reporte["dispositivo"] = _get_dispositivo(db, reporte.get("dispositivoId"))
	reporte["usuario"] = _get_usuario(db, reporte.get("usuarioId"))
	return reporte


@router.get("", summary="Listar reportes")
async def reportes_list(db: Session = Depends(get_db)) -> dict:
	query = text("SELECT id, dispositivoId, usuarioId, comentarios, foto, fechaAlta, fechaUltimaModificacion FROM invReportes")
	rows = db.execute(query).mappings().fetchall()
	reportes = []
	for row in rows:
		reporte = _json_safe_dict(dict(row))
		reporte["dispositivo"] = _get_dispositivo(db, reporte.get("dispositivoId"))
		reporte["usuario"] = _get_usuario(db, reporte.get("usuarioId"))
		reportes.append(reporte)
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

		existe_dispositivo = db.execute(text("SELECT id FROM invDispositivos WHERE id = :id"), {"id": dispositivo_id}).scalar_one_or_none()
		if not existe_dispositivo:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(dispositivo_id))])

		existe_usuario = db.execute(text("SELECT id FROM invUsuarios WHERE id = :id"), {"id": usuario_id}).scalar_one_or_none()
		if not existe_usuario:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(usuario_id))])

		now = datetime.utcnow()
		insert_query = text(
			"""
			INSERT INTO invReportes (dispositivoId, usuarioId, comentarios, foto, fechaAlta, fechaUltimaModificacion)
			OUTPUT INSERTED.id
			VALUES (:dispositivoId, :usuarioId, :comentarios, :foto, :fechaAlta, :fechaUltimaModificacion)
			"""
		)
		reporte_id = int(db.execute(insert_query, {
			"dispositivoId": dispositivo_id,
			"usuarioId": usuario_id,
			"comentarios": comentarios,
			"foto": foto,
			"fechaAlta": now,
			"fechaUltimaModificacion": now
		}).scalar_one())

		db.execute(text("UPDATE invDispositivos SET descompostura = :comentarios WHERE id = :id"), {"comentarios": comentarios, "id": dispositivo_id})
		db.commit()

		reporte_completo = _build_reporte_response(db, reporte_id)
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
	reporte = _build_reporte_response(db, id)
	if not reporte:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return fastapi_response(reporte, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar reportes")
async def reportes_query() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="reportes.query pendiente de migracion")


@router.get("/filter/{value}", summary="Filtrar reportes")
async def reportes_filter(value: str) -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message=f"reportes.filter({value}) pendiente de migracion")
