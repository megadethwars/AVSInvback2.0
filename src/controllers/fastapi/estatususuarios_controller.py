from fastapi import APIRouter, status

from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusUsuarios", tags=["EstatusUsuarios"])



@router.get("", summary="Listar estatus de usuarios")
async def estatususuarios_list() -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "estatususuarios.list pendiente de migracion")


@router.post("", summary="Crear estatus de usuario")
async def estatususuarios_create() -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "estatususuarios.create pendiente de migracion")


@router.put("", summary="Actualizar estatus de usuario")
async def estatususuarios_update() -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "estatususuarios.update pendiente de migracion")


@router.get("/{id}", summary="Obtener estatus de usuario por ID")
async def estatususuarios_get_one(id: int) -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"estatususuarios.get({id}) pendiente de migracion")
