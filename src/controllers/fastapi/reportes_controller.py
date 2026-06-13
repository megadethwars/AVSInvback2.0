from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
	payload = {
		"app_code": app_code,
		"message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
		"data": res,
	}
	return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar reportes")
async def reportes_list() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "reportes.list pendiente de migracion")


@router.post("", summary="Crear reporte")
async def reportes_create() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "reportes.create pendiente de migracion")


@router.put("", summary="Actualizar reporte")
async def reportes_update() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "reportes.update pendiente de migracion")


@router.get("/{id}", summary="Obtener reporte por ID")
async def reportes_get_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"reportes.get({id}) pendiente de migracion")


@router.post("/query", summary="Consultar reportes")
async def reportes_query() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "reportes.query pendiente de migracion")


@router.get("/filter/{value}", summary="Filtrar reportes")
async def reportes_filter(value: str) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"reportes.filter({value}) pendiente de migracion")
