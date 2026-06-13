from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/statusUsuarios", tags=["EstatusUsuarios"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
    payload = {
        "app_code": app_code,
        "message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
        "data": res,
    }
    return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar estatus de usuarios")
async def estatususuarios_list() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "estatususuarios.list pendiente de migracion")


@router.post("", summary="Crear estatus de usuario")
async def estatususuarios_create() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "estatususuarios.create pendiente de migracion")


@router.put("", summary="Actualizar estatus de usuario")
async def estatususuarios_update() -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "estatususuarios.update pendiente de migracion")


@router.get("/{id}", summary="Obtener estatus de usuario por ID")
async def estatususuarios_get_one(id: int) -> dict:
    return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"estatususuarios.get({id}) pendiente de migracion")
