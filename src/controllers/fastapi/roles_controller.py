from fastapi import APIRouter, status

from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])



@router.get("", summary="Listar roles")
async def roles_list() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "roles.list pendiente de migracion")


@router.post("", summary="Crear rol")
async def roles_create() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "roles.create pendiente de migracion")


@router.put("", summary="Actualizar rol")
async def roles_update() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "roles.update pendiente de migracion")


@router.get("/{id}", summary="Obtener rol por ID")
async def roles_get_one(id: int) -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"roles.get({id}) pendiente de migracion")
