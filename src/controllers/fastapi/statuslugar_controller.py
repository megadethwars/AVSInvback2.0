from fastapi import APIRouter, status

from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusLugar", tags=["StatusLugar"])



@router.get("", summary="Listar status de lugar")
async def statuslugar_list() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "statuslugar.list pendiente de migracion")


@router.post("", summary="Crear status de lugar")
async def statuslugar_create() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "statuslugar.create pendiente de migracion")


@router.put("", summary="Actualizar status de lugar")
async def statuslugar_update() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "statuslugar.update pendiente de migracion")


@router.get("/{id}", summary="Obtener status de lugar por ID")
async def statuslugar_get_one(id: int) -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"statuslugar.get({id}) pendiente de migracion")
