from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])


@router.get("", summary="Listar movimientos")
async def movimientos_list() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="movimientos.list pendiente de migracion")


@router.post("", summary="Crear movimiento")
async def movimientos_create() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="movimientos.create pendiente de migracion")


@router.put("", summary="Actualizar movimiento")
async def movimientos_update() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="movimientos.update pendiente de migracion")


@router.get("/{id}", summary="Obtener movimiento por ID")
async def movimientos_get_one(id: int) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"movimientos.get({id}) pendiente de migracion")


@router.get("/LastOne/{id}", summary="Obtener ultimo movimiento por dispositivo")
async def movimientos_last_one(id: int) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"movimientos.lastone({id}) pendiente de migracion")


@router.post("/query", summary="Consultar movimientos")
async def movimientos_query() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="movimientos.query pendiente de migracion")


@router.get("/filter", summary="Filtrar movimientos")
async def movimientos_filter() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="movimientos.filter pendiente de migracion")


@router.get("/filtermovementFields", summary="Filtrar movimientos campos minimos")
async def movimientos_filter_fields() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="movimientos.filtermovementFields pendiente de migracion")
