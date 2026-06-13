from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.StatusDevicesModel import StatusDevicesModel
from ...schemas import StatusDevicesBase, StatusDevicesCreate, StatusDevicesUpdate
from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/statusDevices", tags=["StatusDevices"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "") -> JSONResponse:
    payload = {
        "app_code": app_code,
        "message": [{"status": returnCodes.app_codes[app_code] if message == "" else str(message)}],
        "data": res,
    }
    return JSONResponse(status_code=status_code, content=payload)


@router.get("", summary="Listar status devices")
async def get_status_devices(db: Session = Depends(get_db)) -> dict:
    rows = StatusDevicesModel.get_all_status(db)
    serialized = [StatusDevicesBase.model_validate(item).model_dump(mode="json") for item in rows]
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{status_id}", summary="Obtener status device por ID")
async def get_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    serialized = StatusDevicesBase.model_validate(row).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear status device")
async def create_status_device(status_data: StatusDevicesCreate, db: Session = Depends(get_db)) -> dict:
    try:
        row = StatusDevicesModel.create_status(db, descripcion=status_data.descripcion)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = StatusDevicesBase.model_validate(row).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_201_CREATED, "TPM-1")


@router.put("/{status_id}", summary="Actualizar status device")
async def update_status_device(
    status_id: int,
    status_data: StatusDevicesUpdate,
    db: Session = Depends(get_db),
) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    payload = status_data.model_dump(exclude_unset=True, exclude_none=True)
    payload.pop("id", None)
    payload.pop("fechaAlta", None)
    payload.pop("fechaUltimaModificacion", None)

    try:
        updated = row.update(db, **payload)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))

    serialized = StatusDevicesBase.model_validate(updated).model_dump(mode="json")
    return _legacy_response(serialized, status.HTTP_200_OK, "TPM-6")


@router.delete("/{status_id}", summary="Eliminar status device")
async def delete_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    try:
        row.delete(db)
    except Exception as err:
        return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))
    return _legacy_response(None, status.HTTP_200_OK, "TPM-9")
