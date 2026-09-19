from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.EstatusUsuariosModelSchema import (
    EstatusUsuariosModel,
    EstatusUsuariosSchemaCreate,
    EstatusUsuariosSchemaUpdate,
)
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusUsuarios", tags=["EstatusUsuarios"])


@router.get("", summary="Listar estatus de usuarios")
async def estatususuarios_list(db: Session = Depends(get_db)) -> dict:
    rows = EstatusUsuariosModel.get_all_status(db)
    serialized = [EstatusUsuariosModel.to_dict(row) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear estatus de usuario")
async def estatususuarios_create(payload: EstatusUsuariosSchemaCreate, db: Session = Depends(get_db)) -> dict:
    descripcion = payload.descripcion

    existing = EstatusUsuariosModel.get_status_by_tipo(db, descripcion)
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": descripcion}])

    try:
        row = EstatusUsuariosModel.create_status(db, descripcion)
        return fastapi_response(EstatusUsuariosModel.to_dict(row), status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar estatus de usuario")
async def estatususuarios_update(payload: EstatusUsuariosSchemaUpdate, db: Session = Depends(get_db)) -> dict:
    if payload.id is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    status_id = int(payload.id)
    row = EstatusUsuariosModel.get_one_status(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if payload.descripcion is not None:
        update_values["descripcion"] = payload.descripcion

    if not update_values:
        return fastapi_response(EstatusUsuariosModel.to_dict(row), status.HTTP_200_OK, "TPM-6")

    try:
        updated = row.update(db, update_values)
        return fastapi_response(EstatusUsuariosModel.to_dict(updated), status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener estatus de usuario por ID")
async def estatususuarios_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    row = EstatusUsuariosModel.get_one_status(db, id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(EstatusUsuariosModel.to_dict(row), status.HTTP_200_OK, "TPM-3")
