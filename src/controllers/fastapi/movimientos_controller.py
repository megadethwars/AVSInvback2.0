from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
	payload = {
		"app_code": app_code,
		"message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
		"data": res,
	}
	return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar movimientos")
async def movimientos_list() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.list pendiente de migracion")


@router.post("", summary="Crear movimiento")
async def movimientos_create() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.create pendiente de migracion")


@router.put("", summary="Actualizar movimiento")
async def movimientos_update() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.update pendiente de migracion")


@router.get("/{id}", summary="Obtener movimiento por ID")
async def movimientos_get_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"movimientos.get({id}) pendiente de migracion")


@router.get("/LastOne/{id}", summary="Obtener ultimo movimiento por dispositivo")
async def movimientos_last_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"movimientos.lastone({id}) pendiente de migracion")


@router.post("/query", summary="Consultar movimientos")
async def movimientos_query() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.query pendiente de migracion")


@router.get("/filter", summary="Filtrar movimientos")
async def movimientos_filter() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.filter pendiente de migracion")


@router.get("/filtermovementFields", summary="Filtrar movimientos campos minimos")
async def movimientos_filter_fields() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.filtermovementFields pendiente de migracion")
