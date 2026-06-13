from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/statusLugar", tags=["StatusLugar"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
	payload = {
		"app_code": app_code,
		"message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
		"data": res,
	}
	return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar status de lugar")
async def statuslugar_list() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "statuslugar.list pendiente de migracion")


@router.post("", summary="Crear status de lugar")
async def statuslugar_create() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "statuslugar.create pendiente de migracion")


@router.put("", summary="Actualizar status de lugar")
async def statuslugar_update() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "statuslugar.update pendiente de migracion")


@router.get("/{id}", summary="Obtener status de lugar por ID")
async def statuslugar_get_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"statuslugar.get({id}) pendiente de migracion")
