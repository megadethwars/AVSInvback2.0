from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.post("/login", summary="Login usuario")
async def users_login() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="usuarios.login pendiente de migracion")


@router.put("/pass", summary="Cambiar password")
async def users_update_password() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="usuarios.pass pendiente de migracion")


@router.get("", summary="Listar usuarios")
async def users_list() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="usuarios.list pendiente de migracion")


@router.post("", summary="Crear usuario")
async def users_create() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="usuarios.create pendiente de migracion")


@router.put("", summary="Actualizar usuario")
async def users_update() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="usuarios.update pendiente de migracion")


@router.get("/{id}", summary="Obtener usuario por ID")
async def users_get_one(id: int) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"usuarios.get({id}) pendiente de migracion")


@router.post("/query", summary="Consultar usuarios")
async def users_query() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="usuarios.query pendiente de migracion")
