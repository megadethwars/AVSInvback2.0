from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.RolesModelSchema import RolesModel, RolesSchemaCreate, RolesSchemaUpdate
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


@router.get("", summary="Listar roles")
async def roles_list(db: Session = Depends(get_db)) -> dict:
	rows = RolesModel.get_all_roles(db)
	roles = [RolesModel.to_dict(row) for row in rows]
	return fastapi_response(roles, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear rol")
async def roles_create(payload: RolesSchemaCreate, db: Session = Depends(get_db)) -> dict:
	try:
		existing = RolesModel.get_rol_by_nombre(db, payload.nombre)
		if existing:
			return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": payload.nombre}])

		created = RolesModel.create_role(db, payload.nombre)
		return fastapi_response([created], status.HTTP_201_CREATED, "TPM-8")
	except Exception as err:
		db.rollback()
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar rol")
async def roles_update(payload: RolesSchemaUpdate, db: Session = Depends(get_db)) -> dict:
	if payload.id is None:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

	role = RolesModel.get_one_rol(db, int(payload.id))
	if not role:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

	update_fields = {}
	if payload.nombre is not None:
		update_fields["nombre"] = payload.nombre

	if not update_fields:
		return fastapi_response(RolesModel.to_dict(role), status.HTTP_200_OK, "TPM-6")

	update_fields["fechaUltimaModificacion"] = datetime.utcnow()

	try:
		updated = role.update(db, update_fields)
		return fastapi_response(RolesModel.to_dict(updated), status.HTTP_200_OK, "TPM-6")
	except Exception as err:
		db.rollback()
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener rol por ID")
async def roles_get_one(id: int, db: Session = Depends(get_db)) -> dict:
	role = RolesModel.get_one_rol(db, id)
	if not role:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return fastapi_response(RolesModel.to_dict(role), status.HTTP_200_OK, "TPM-3")
