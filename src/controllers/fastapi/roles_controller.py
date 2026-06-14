from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.orm import Session

from ...database import engine, get_db
from ...schemas import RolesCreate, RolesUpdate
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])

_metadata = MetaData()
_roles = Table("invRoles", _metadata, autoload_with=engine)


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


def _get_role(db: Session, role_id: int) -> dict | None:
	stmt = (
		select(_roles.c.id, _roles.c.nombre, _roles.c.fechaAlta, _roles.c.fechaUltimaModificacion)
		.where(_roles.c.id == role_id)
		.limit(1)
	)
	row = db.execute(stmt).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


@router.get("", summary="Listar roles")
async def roles_list(db: Session = Depends(get_db)) -> dict:
	stmt = select(_roles.c.id, _roles.c.nombre, _roles.c.fechaAlta, _roles.c.fechaUltimaModificacion).order_by(_roles.c.nombre)
	rows = db.execute(stmt).mappings().fetchall()
	roles = [_json_safe_dict(dict(row)) for row in rows]
	return fastapi_response(roles, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear rol")
async def roles_create(payload: RolesCreate, db: Session = Depends(get_db)) -> dict:
	try:
		existing = db.execute(select(_roles.c.id).where(_roles.c.nombre == payload.nombre).limit(1)).scalar_one_or_none()
		if existing:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": payload.nombre}])

		now = datetime.utcnow()
		insert_stmt = (
			insert(_roles)
			.values(nombre=payload.nombre, fechaAlta=now, fechaUltimaModificacion=now)
			.returning(_roles.c.id)
		)
		new_id = int(db.execute(insert_stmt).scalar_one())
		db.commit()

		created = _get_role(db, new_id)
		return fastapi_response([created], status.HTTP_201_CREATED, "TPM-8")
	except Exception as err:
		db.rollback()
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar rol")
async def roles_update(payload: RolesUpdate, db: Session = Depends(get_db)) -> dict:
	if payload.id is None:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

	role = _get_role(db, int(payload.id))
	if not role:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

	update_fields = {}
	if payload.nombre is not None:
		update_fields["nombre"] = payload.nombre

	if not update_fields:
		return fastapi_response(role, status.HTTP_200_OK, "TPM-6")

	update_fields["id"] = int(payload.id)
	update_fields["fechaUltimaModificacion"] = datetime.utcnow()

	try:
		stmt = (
			update(_roles)
			.where(_roles.c.id == int(payload.id))
			.values(nombre=update_fields.get("nombre"), fechaUltimaModificacion=update_fields["fechaUltimaModificacion"])
		)
		db.execute(stmt)
		db.commit()
		updated = _get_role(db, int(payload.id))
		return fastapi_response(updated, status.HTTP_200_OK, "TPM-6")
	except Exception as err:
		db.rollback()
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener rol por ID")
async def roles_get_one(id: int, db: Session = Depends(get_db)) -> dict:
	role = _get_role(db, id)
	if not role:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return fastapi_response(role, status.HTTP_200_OK, "TPM-3")
