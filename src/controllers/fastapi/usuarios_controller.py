from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
	payload = {
		"app_code": app_code,
		"message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
		"data": res,
	}
	return JSONResponse(status_code=status_code, content=payload)


@router.post("/login", summary="Login usuario")
async def users_login() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "usuarios.login pendiente de migracion")


@router.put("/pass", summary="Cambiar password")
async def users_update_password() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "usuarios.pass pendiente de migracion")


@router.get("", summary="Listar usuarios")
async def users_list() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "usuarios.list pendiente de migracion")


@router.post("", summary="Crear usuario")
async def users_create() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "usuarios.create pendiente de migracion")


@router.put("", summary="Actualizar usuario")
async def users_update() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "usuarios.update pendiente de migracion")


@router.get("/{id}", summary="Obtener usuario por ID")
async def users_get_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"usuarios.get({id}) pendiente de migracion")


@router.post("/query", summary="Consultar usuarios")
async def users_query() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "usuarios.query pendiente de migracion")
