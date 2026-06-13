from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.StatusDevicesModel import StatusDevicesModel
from ...schemas import StatusDevicesBase, StatusDevicesCreate, StatusDevicesUpdate

router = APIRouter(prefix="/api/v1/statusDevices", tags=["StatusDevices"])


@router.get("", response_model=list[StatusDevicesBase], summary="Listar status devices")
async def get_status_devices(db: Session = Depends(get_db)) -> list[StatusDevicesBase]:
    rows = StatusDevicesModel.get_all_status(db)
    return [StatusDevicesBase.model_validate(item) for item in rows]


@router.get("/{status_id}", response_model=StatusDevicesBase, summary="Obtener status device por ID")
async def get_status_device(status_id: int, db: Session = Depends(get_db)) -> StatusDevicesBase:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return StatusDevicesBase.model_validate(row)


@router.post("", response_model=StatusDevicesBase, status_code=status.HTTP_201_CREATED, summary="Crear status device")
async def create_status_device(status_data: StatusDevicesCreate, db: Session = Depends(get_db)) -> StatusDevicesBase:
    row = StatusDevicesModel.create_status(db, descripcion=status_data.descripcion)
    return StatusDevicesBase.model_validate(row)


@router.put("/{status_id}", response_model=StatusDevicesBase, summary="Actualizar status device")
async def update_status_device(
    status_id: int,
    status_data: StatusDevicesUpdate,
    db: Session = Depends(get_db),
) -> StatusDevicesBase:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")

    payload = status_data.model_dump(exclude_unset=True, exclude_none=True)
    payload.pop("id", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    updated = row.update(db, **payload)
    return StatusDevicesBase.model_validate(updated)


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar status device")
async def delete_status_device(status_id: int, db: Session = Depends(get_db)) -> None:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    row.delete(db)
    return None
