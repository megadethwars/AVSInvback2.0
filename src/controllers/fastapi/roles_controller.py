from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


@router.get("", summary="Listar roles")
async def roles_list() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="roles.list pendiente de migracion")


@router.post("", summary="Crear rol")
async def roles_create() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="roles.create pendiente de migracion")


@router.put("", summary="Actualizar rol")
async def roles_update() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="roles.update pendiente de migracion")


@router.get("/{id}", summary="Obtener rol por ID")
async def roles_get_one(id: int) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"roles.get({id}) pendiente de migracion")
