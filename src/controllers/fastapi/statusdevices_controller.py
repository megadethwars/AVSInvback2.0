from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.StatusDevicesModelSchema import (
    StatusDevicesModel,
    StatusDevicesModelSchema,
    StatusDevicesSchemaCreate,
    StatusDevicesSchemaUpdate,
)
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusDevices", tags=["StatusDevices"])


@router.get("", summary="Listar status devices")
async def get_status_devices(db: Session = Depends(get_db)) -> dict:
    rows = StatusDevicesModel.get_all_status(db)
    serialized = [StatusDevicesModelSchema.to_dict(row) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{status_id}", summary="Obtener status device por ID")
async def get_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(StatusDevicesModelSchema.to_dict(row), status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear status device")
async def create_status_device(payload: StatusDevicesSchemaCreate, db: Session = Depends(get_db)) -> dict:
    descripcion = payload.descripcion
    if not descripcion:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="descripcion es requerido")

    existing = StatusDevicesModel.get_status_by_nombre(db, descripcion)
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": descripcion}])

    try:
        row = StatusDevicesModel.create_status(db, descripcion)
        return fastapi_response(StatusDevicesModelSchema.to_dict(row), status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar status device")
async def update_status_device(payload: StatusDevicesSchemaUpdate, db: Session = Depends(get_db)) -> dict:
    if payload.id is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    status_id = int(payload.id)
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if payload.descripcion is not None:
        update_values["descripcion"] = payload.descripcion

    if not update_values:
        return fastapi_response(StatusDevicesModelSchema.to_dict(row), status.HTTP_200_OK, "TPM-6")

    try:
        updated = row.update(db, **update_values)
        return fastapi_response(StatusDevicesModelSchema.to_dict(updated), status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.delete("/{status_id}", summary="Eliminar status device")
async def delete_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    row = StatusDevicesModel.get_one_status(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    try:
        row.delete(db)
        return fastapi_response(None, status.HTTP_200_OK, "TPM-9")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))
