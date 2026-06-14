from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.orm import Session

from ...database import engine, get_db
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusDevices", tags=["StatusDevices"])

_metadata = MetaData()
_status_devices = Table("invStatusDevices", _metadata, autoload_with=engine)


def _serialize_status(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "descripcion": row.get("descripcion"),
        "fechaAlta": row.get("fechaAlta").isoformat() if row.get("fechaAlta") else None,
        "fechaUltimaModificacion": row.get("fechaUltimaModificacion").isoformat() if row.get("fechaUltimaModificacion") else None,
    }


@router.get("", summary="Listar status devices")
async def get_status_devices(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(
            _status_devices.c.id,
            _status_devices.c.descripcion,
            _status_devices.c.fechaAlta,
            _status_devices.c.fechaUltimaModificacion,
        ).order_by(_status_devices.c.id)
    ).mappings().all()
    serialized = [_serialize_status(dict(row)) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.get("/{status_id}", summary="Obtener status device por ID")
async def get_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        select(
            _status_devices.c.id,
            _status_devices.c.descripcion,
            _status_devices.c.fechaAlta,
            _status_devices.c.fechaUltimaModificacion,
        ).where(_status_devices.c.id == status_id)
    ).mappings().first()
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(_serialize_status(dict(row)), status.HTTP_200_OK, "TPM-3")


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear status device")
async def create_status_device(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    descripcion = payload.get("descripcion")
    if not descripcion:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="descripcion es requerido")

    existing = db.execute(
        select(_status_devices.c.id).where(_status_devices.c.descripcion == descripcion).limit(1)
    ).scalar_one_or_none()
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": descripcion}])

    try:
        now = datetime.utcnow()
        new_id = int(
            db.execute(
                insert(_status_devices)
                .values(descripcion=descripcion, fechaAlta=now, fechaUltimaModificacion=now)
                .returning(_status_devices.c.id)
            ).scalar_one()
        )
        db.commit()
        row = db.execute(
            select(
                _status_devices.c.id,
                _status_devices.c.descripcion,
                _status_devices.c.fechaAlta,
                _status_devices.c.fechaUltimaModificacion,
            ).where(_status_devices.c.id == new_id)
        ).mappings().first()
        return fastapi_response(_serialize_status(dict(row)) if row else None, status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar status device")
async def update_status_device(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    status_id = int(payload.get("id"))
    exists = db.execute(select(_status_devices.c.id).where(_status_devices.c.id == status_id)).scalar_one_or_none()
    if not exists:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if "descripcion" in payload and payload.get("descripcion") is not None:
        update_values["descripcion"] = payload.get("descripcion")

    if not update_values:
        unchanged = db.execute(
            select(
                _status_devices.c.id,
                _status_devices.c.descripcion,
                _status_devices.c.fechaAlta,
                _status_devices.c.fechaUltimaModificacion,
            ).where(_status_devices.c.id == status_id)
        ).mappings().first()
        return fastapi_response(_serialize_status(dict(unchanged)) if unchanged else None, status.HTTP_200_OK, "TPM-6")

    update_values["fechaUltimaModificacion"] = datetime.utcnow()
    try:
        db.execute(update(_status_devices).where(_status_devices.c.id == status_id).values(**update_values))
        db.commit()
        updated = db.execute(
            select(
                _status_devices.c.id,
                _status_devices.c.descripcion,
                _status_devices.c.fechaAlta,
                _status_devices.c.fechaUltimaModificacion,
            ).where(_status_devices.c.id == status_id)
        ).mappings().first()
        return fastapi_response(_serialize_status(dict(updated)) if updated else None, status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.delete("/{status_id}", summary="Eliminar status device")
async def delete_status_device(status_id: int, db: Session = Depends(get_db)) -> dict:
    exists = db.execute(select(_status_devices.c.id).where(_status_devices.c.id == status_id)).scalar_one_or_none()
    if not exists:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    try:
        db.execute(_status_devices.delete().where(_status_devices.c.id == status_id))
        db.commit()
        return fastapi_response(None, status.HTTP_200_OK, "TPM-9")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))
