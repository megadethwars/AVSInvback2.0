from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/tipomovimientos", tags=["TipoMovimientos"])


@router.get("", summary="Listar tipos de movimiento")
async def tipomovimientos_list() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="tipomovimientos.list pendiente de migracion")


@router.post("", summary="Crear tipo de movimiento")
async def tipomovimientos_create() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="tipomovimientos.create pendiente de migracion")


@router.put("", summary="Actualizar tipo de movimiento")
async def tipomovimientos_update() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="tipomovimientos.update pendiente de migracion")


@router.get("/{id}", summary="Obtener tipo de movimiento por ID")
async def tipomovimientos_get_one(id: int) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"tipomovimientos.get({id}) pendiente de migracion")
