from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.LugaresModel import LugaresModel
from ...models.StatusDevicesModel import StatusDevicesModel
from ...schemas import DispositivosBase, DispositivosCreate, DispositivosUpdate

router = APIRouter(prefix="/api/v1/dispositivos", tags=["Dispositivos"])


@router.get("", response_model=list[DispositivosBase], summary="Listar dispositivos")
async def get_dispositivos(
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> list[DispositivosBase]:
    rows = DispositivosModel.get_all_devices(db, offset=offset, limit=limit)
    return [DispositivosBase.model_validate(item) for item in rows]


@router.get("/{dispositivo_id}", response_model=DispositivosBase, summary="Obtener dispositivo por ID")
async def get_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> DispositivosBase:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return DispositivosBase.model_validate(row)


@router.get("/search/{search_term}", response_model=list[DispositivosBase], summary="Buscar dispositivos")
async def search_dispositivos(
    search_term: str,
    offset: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> list[DispositivosBase]:
    rows = DispositivosModel.search_by_multiple_fields(db, search_term, offset, limit)
    return [DispositivosBase.model_validate(item) for item in rows]


@router.post("", response_model=DispositivosBase, status_code=status.HTTP_201_CREATED, summary="Crear dispositivo")
async def create_dispositivo(
    dispositivo_data: DispositivosCreate,
    db: Session = Depends(get_db),
) -> DispositivosBase:
    lugar = LugaresModel.get_one_lugar(db, dispositivo_data.lugarId)
    if not lugar:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid lugarId")

    status_device = StatusDevicesModel.get_one_status(db, dispositivo_data.statusId)
    if not status_device:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid statusId")

    payload = dispositivo_data.model_dump(exclude_none=True)
    payload.pop("lugar", None)
    payload.pop("status", None)
    payload.pop("id", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    row = DispositivosModel.create_device(db, **payload)
    return DispositivosBase.model_validate(row)


@router.put("/{dispositivo_id}", response_model=DispositivosBase, summary="Actualizar dispositivo")
async def update_dispositivo(
    dispositivo_id: int,
    dispositivo_data: DispositivosUpdate,
    db: Session = Depends(get_db),
) -> DispositivosBase:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    payload = dispositivo_data.model_dump(exclude_unset=True, exclude_none=True)
    payload.pop("id", None)
    payload.pop("lugar", None)
    payload.pop("status", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    if "lugarId" in payload:
        lugar = LugaresModel.get_one_lugar(db, payload["lugarId"])
        if not lugar:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid lugarId")

    if "statusId" in payload:
        status_device = StatusDevicesModel.get_one_status(db, payload["statusId"])
        if not status_device:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid statusId")

    updated = row.update(db, **payload)
    return DispositivosBase.model_validate(updated)


@router.delete("/{dispositivo_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar dispositivo")
async def delete_dispositivo(dispositivo_id: int, db: Session = Depends(get_db)) -> None:
    row = DispositivosModel.get_one_device(db, dispositivo_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    row.delete(db)
    return None


@router.post("/query", summary="Consultar dispositivos")
async def dispositivos_query() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="dispositivos.query pendiente de migracion")


@router.get("/filter/{value}", summary="Filtrar dispositivos por valor")
async def dispositivos_filter_by_value(value: str) -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"dispositivos.filter({value}) pendiente de migracion")


@router.post("/filterdevice", summary="Filtrar dispositivos")
async def dispositivos_filterdevice() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="dispositivos.filterdevice pendiente de migracion")


@router.post("/filterdeviceFields", summary="Filtrar dispositivos campos")
async def dispositivos_filterdevice_fields() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="dispositivos.filterdeviceFields pendiente de migracion")


@router.get("/filterdeviceminFields", summary="Filtrar dispositivos minimos")
async def dispositivos_filterdevice_min_fields() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="dispositivos.filterdeviceminFields pendiente de migracion")


@router.get("/filterdeviceByCodigo", summary="Filtrar dispositivos por codigo")
async def dispositivos_filter_by_codigo() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="dispositivos.filterdeviceByCodigo pendiente de migracion")


@router.get("/alldeviceSomeFields", summary="Listar dispositivos campos seleccionados")
async def dispositivos_some_fields() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="dispositivos.alldeviceSomeFields pendiente de migracion")


@router.get("/getAmount", summary="Obtener monto total dispositivos")
async def dispositivos_get_amount() -> dict:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="dispositivos.getAmount pendiente de migracion")
