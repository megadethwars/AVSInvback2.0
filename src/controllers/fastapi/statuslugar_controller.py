from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.StatusLugarModelSchema import LugaresModel, StatusLugarModelSchema
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusLugar", tags=["StatusLugar"])


@router.get("", summary="Listar status de lugar")
async def statuslugar_list(db: Session = Depends(get_db)) -> dict:
    rows = LugaresModel.get_all_lugares(db)
    serialized = [StatusLugarModelSchema.to_dict(row) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear status de lugar")
async def statuslugar_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    descripcion = payload.get("descripcion") or payload.get("lugar")
    if not descripcion:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="descripcion es requerido")

    existing = LugaresModel.get_lugar_by_nombre(db, descripcion)
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": descripcion}])

    try:
        row = LugaresModel.create_lugar(db, lugar=descripcion, activo=bool(payload.get("activo", True)))
        return fastapi_response(StatusLugarModelSchema.to_dict(row), status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar status de lugar")
async def statuslugar_update(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    status_id = int(payload.get("id"))
    row = LugaresModel.get_one_lugar(db, status_id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if payload.get("descripcion") is not None:
        update_values["lugar"] = payload.get("descripcion")
    if payload.get("lugar") is not None:
        update_values["lugar"] = payload.get("lugar")
    if payload.get("activo") is not None:
        update_values["activo"] = bool(payload.get("activo"))

    if not update_values:
        return fastapi_response(StatusLugarModelSchema.to_dict(row), status.HTTP_200_OK, "TPM-6")

    try:
        updated = row.update(db, **update_values)
        return fastapi_response(StatusLugarModelSchema.to_dict(updated), status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener status de lugar por ID")
async def statuslugar_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    row = LugaresModel.get_one_lugar(db, id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(StatusLugarModelSchema.to_dict(row), status.HTTP_200_OK, "TPM-3")
