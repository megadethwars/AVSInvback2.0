from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from ...database import get_db
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


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


def _get_usuario_full(db: Session, usuario_id: int) -> dict | None:
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


@router.post("/login", summary="Login usuario")
async def users_login(payload: dict, db: Session = Depends(get_db)) -> dict:
	if not payload:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

	try:
		username = payload.get("username")
		password = payload.get("password")
		if not username or not password:
			return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

		query = text(
			"""
			SELECT id, password, statusId
			FROM invUsuarios
			WHERE username = :username
			"""
		)
		user = db.execute(query, {"username": username}).mappings().first()
		if not user:
			return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4", message="Usuario no encontrado")

		if int(user.get("statusId") or 0) == 3:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-19", message="Usuario dado de baja")

		if not check_password_hash(str(user.get("password") or ""), password):
			return fastapi_response(None, status.HTTP_401_UNAUTHORIZED, "TPM-10", message="acceso no autorizado, usuario y/o contraseña incorrecto")

		serialized_user = _get_usuario_full(db, int(user.get("id")))
		return fastapi_response(serialized_user, status.HTTP_201_CREATED, "TPM-18")
	except Exception as err:
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("/pass", summary="Cambiar password")
async def users_update_password() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="usuarios.pass pendiente de migracion")


@router.get("", summary="Listar usuarios")
async def users_list(db: Session = Depends(get_db)) -> dict:
	query = text("SELECT id, nombre, username, apellidoPaterno, apellidoMaterno, password, telefono, correo, foto, rolId, statusId, fechaAlta, fechaUltimaModificacion FROM invUsuarios WHERE statusId != 3")
	rows = db.execute(query).mappings().fetchall()
	usuarios = []
	for row in rows:
		usuario = _json_safe_dict(dict(row))
		usuario["rol"] = _get_rol(db, usuario.get("rolId"))
		usuario["status"] = _get_status_usuario(db, usuario.get("statusId"))
		usuarios.append(usuario)
	return fastapi_response(usuarios, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear usuario")
async def users_create(payload: dict, db: Session = Depends(get_db)) -> dict:
	if not payload:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

	try:
		user_data = {
			"nombre": payload.get("nombre"),
			"username": payload.get("username"),
			"apellidoPaterno": payload.get("apellidoPaterno"),
			"apellidoMaterno": payload.get("apellidoMaterno"),
			"password": generate_password_hash(payload.get("password", "")),
			"telefono": payload.get("telefono"),
			"correo": payload.get("correo"),
			"foto": payload.get("foto"),
			"rolId": payload.get("rolId"),
			"statusId": payload.get("statusId"),
		}

		existe_user = db.execute(text("SELECT id FROM invUsuarios WHERE username = :username"), {"username": user_data["username"]}).scalar_one_or_none()
		if existe_user:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[partial_response("TPM-5", name=user_data["username"])])

		existe_rol = db.execute(text("SELECT id FROM invRoles WHERE id = :id"), {"id": user_data["rolId"]}).scalar_one_or_none()
		if not existe_rol:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(user_data["rolId"]))])

		existe_status = db.execute(text("SELECT id FROM invStatusUsuarios WHERE id = :id"), {"id": user_data["statusId"]}).scalar_one_or_none()
		if not existe_status:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(user_data["statusId"]))])

		now = datetime.utcnow()
		insert_query = text(
			"""
			INSERT INTO invUsuarios (nombre, username, apellidoPaterno, apellidoMaterno, password, telefono, correo, foto, rolId, statusId, fechaAlta, fechaUltimaModificacion)
			OUTPUT INSERTED.id
			VALUES (:nombre, :username, :apellidoPaterno, :apellidoMaterno, :password, :telefono, :correo, :foto, :rolId, :statusId, :fechaAlta, :fechaUltimaModificacion)
			"""
		)
		usuario_id = int(db.execute(insert_query, {**user_data, "fechaAlta": now, "fechaUltimaModificacion": now}).scalar_one())
		db.commit()

		usuario_completo = _get_usuario_full(db, usuario_id)
		return fastapi_response(usuario_completo, status.HTTP_201_CREATED, "TPM-1")
	except Exception as err:
		db.rollback()
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar usuario")
async def users_update() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="usuarios.update pendiente de migracion")


@router.get("/{id}", summary="Obtener usuario por ID")
async def users_get_one(id: int, db: Session = Depends(get_db)) -> dict:
	usuario = _get_usuario_full(db, id)
	if not usuario:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return fastapi_response(usuario, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar usuarios")
async def users_query() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="usuarios.query pendiente de migracion")
