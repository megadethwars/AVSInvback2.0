from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/statusUsuarios", tags=["EstatusUsuarios"])


@router.get("", summary="Listar estatus de usuarios")
async def estatususuarios_list() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="estatususuarios.list pendiente de migracion")


@router.post("", summary="Crear estatus de usuario")
async def estatususuarios_create() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="estatususuarios.create pendiente de migracion")


@router.put("", summary="Actualizar estatus de usuario")
async def estatususuarios_update() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="estatususuarios.update pendiente de migracion")


@router.get("/{id}", summary="Obtener estatus de usuario por ID")
async def estatususuarios_get_one(id: int) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"estatususuarios.get({id}) pendiente de migracion")
