from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])


@router.get("", summary="Listar reportes")
async def reportes_list() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="reportes.list pendiente de migracion")


@router.post("", summary="Crear reporte")
async def reportes_create() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="reportes.create pendiente de migracion")


@router.put("", summary="Actualizar reporte")
async def reportes_update() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="reportes.update pendiente de migracion")


@router.get("/{id}", summary="Obtener reporte por ID")
async def reportes_get_one(id: int) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"reportes.get({id}) pendiente de migracion")


@router.post("/query", summary="Consultar reportes")
async def reportes_query() -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="reportes.query pendiente de migracion")


@router.get("/filter/{value}", summary="Filtrar reportes")
async def reportes_filter(value: str) -> dict:
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"reportes.filter({value}) pendiente de migracion")
