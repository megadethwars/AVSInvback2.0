from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.StatusDevicesModel import StatusDevicesModel
from ...schemas import StatusDevicesBase, StatusDevicesCreate, StatusDevicesUpdate
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusDevices", tags=["StatusDevices"])



@router.get("", summary="Listar status devices")
async def get_status_devices(db: Session = Depends(get_db)) -> dict:
    rows = StatusDevicesModel.get_all_status(db)
    serialized = [StatusDevicesBase.model_validate(item).model_dump(mode="json") for item in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{status_id}", summary="Obtener status device por ID")
async def get_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = StatusDevicesBase.model_validate(row).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear status device")
async def create_status_device(status_data: StatusDevicesCreate, db: Session = Depends(get_db)) -> dict:
    try:
        row = StatusDevicesModel.create_status(db, descripcion=status_data.descripcion)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = StatusDevicesBase.model_validate(row).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_201_CREATED, "TPM-1")


@router.put("/{status_id}", summary="Actualizar status device")
async def update_status_device(
    status_id: int,
    status_data: StatusDevicesUpdate,
    db: Session = Depends(get_db),
) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    payload = status_data.model_dump(exclude_unset=True, exclude_none=True)
    payload.pop("id", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    try:
        updated = row.update(db, **payload)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = StatusDevicesBase.model_validate(updated).model_dump(mode="json")
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-6")


@router.delete("/{status_id}", summary="Eliminar status device")
async def delete_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    try:
        row.delete(db)
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))
    return fastapi_response(None, status.HTTP_200_OK, "TPM-9")
