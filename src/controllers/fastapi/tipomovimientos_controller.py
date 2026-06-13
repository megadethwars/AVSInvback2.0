from fastapi import APIRouter, status

from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/tipomovimientos", tags=["TipoMovimientos"])



@router.get("", summary="Listar tipos de movimiento")
async def tipomovimientos_list() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "tipomovimientos.list pendiente de migracion")


@router.post("", summary="Crear tipo de movimiento")
async def tipomovimientos_create() -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "tipomovimientos.create pendiente de migracion")


@router.put("", summary="Actualizar tipo de movimiento")
async def tipomovimientos_update(payload: dict) -> dict:
	if not payload or payload.get("id") is None:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "tipomovimientos.update pendiente de migracion")


@router.get("/{id}", summary="Obtener tipo de movimiento por ID")
async def tipomovimientos_get_one(id: int) -> dict:
	return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"tipomovimientos.get({id}) pendiente de migracion")
