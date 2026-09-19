from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.TipoMovimientosModelSchema import (
    TipoMovimientosModel,
    TipoMovimientosSchemaCreate,
    TipoMovimientosSchemaUpdate,
)
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/tipomovimientos", tags=["TipoMovimientos"])


@router.get("", summary="Listar tipos de movimiento")
async def tipomovimientos_list(db: Session = Depends(get_db)) -> dict:
    rows = TipoMovimientosModel.get_all_tipos(db)
    serialized = [TipoMovimientosModel.to_dict(row) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear tipo de movimiento")
async def tipomovimientos_create(payload: TipoMovimientosSchemaCreate, db: Session = Depends(get_db)) -> dict:
    tipo = payload.tipo
    if not tipo:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="tipo es requerido")

    existing = TipoMovimientosModel.get_tipo_by_nombre(db, tipo)
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": tipo}])

    try:
        row = TipoMovimientosModel.create_tipo(db, tipo)
        return fastapi_response(TipoMovimientosModel.to_dict(row), status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar tipo de movimiento")
async def tipomovimientos_update(payload: TipoMovimientosSchemaUpdate, db: Session = Depends(get_db)) -> dict:
    if payload.id is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    tipo_id = int(payload.id)
    row = TipoMovimientosModel.get_one_tipo(db, tipo_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if payload.tipo is not None:
        update_values["tipo"] = payload.tipo

    if not update_values:
        return fastapi_response(TipoMovimientosModel.to_dict(row), status.HTTP_200_OK, "TPM-6")

    try:
        updated = row.update(db, update_values)
        return fastapi_response(TipoMovimientosModel.to_dict(updated), status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener tipo de movimiento por ID")
async def tipomovimientos_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    row = TipoMovimientosModel.get_one_tipo(db, id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(TipoMovimientosModel.to_dict(row), status.HTTP_200_OK, "TPM-3")
