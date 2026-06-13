from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/tipomovimientos", tags=["TipoMovimientos"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
	payload = {
		"app_code": app_code,
		"message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
		"data": res,
	}
	return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar tipos de movimiento")
async def tipomovimientos_list() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "tipomovimientos.list pendiente de migracion")


@router.post("", summary="Crear tipo de movimiento")
async def tipomovimientos_create() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "tipomovimientos.create pendiente de migracion")


@router.put("", summary="Actualizar tipo de movimiento")
async def tipomovimientos_update() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "tipomovimientos.update pendiente de migracion")


@router.get("/{id}", summary="Obtener tipo de movimiento por ID")
async def tipomovimientos_get_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"tipomovimientos.get({id}) pendiente de migracion")
