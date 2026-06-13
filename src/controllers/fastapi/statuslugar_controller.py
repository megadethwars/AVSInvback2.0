from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/statusLugar", tags=["StatusLugar"])


@router.get("", summary="Listar status de lugar")
async def statuslugar_list() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="statuslugar.list pendiente de migracion")


@router.post("", summary="Crear status de lugar")
async def statuslugar_create() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="statuslugar.create pendiente de migracion")


@router.put("", summary="Actualizar status de lugar")
async def statuslugar_update() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="statuslugar.update pendiente de migracion")


@router.get("/{id}", summary="Obtener status de lugar por ID")
async def statuslugar_get_one(id: int) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"statuslugar.get({id}) pendiente de migracion")
