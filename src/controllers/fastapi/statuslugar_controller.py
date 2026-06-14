from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.orm import Session

from ...database import engine, get_db
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusLugar", tags=["StatusLugar"])

_metadata = MetaData()
_lugares = Table("invLugares", _metadata, autoload_with=engine)


def _serialize_status_lugar(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "descripcion": row.get("lugar"),
        "activo": row.get("activo"),
        "fechaAlta": row.get("fechaAlta").isoformat() if row.get("fechaAlta") else None,
        "fechaUltimaModificacion": row.get("fechaUltimaModificacion").isoformat() if row.get("fechaUltimaModificacion") else None,
    }


@router.get("", summary="Listar status de lugar")
async def statuslugar_list(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(
            _lugares.c.id,
            _lugares.c.lugar,
            _lugares.c.activo,
            _lugares.c.fechaAlta,
            _lugares.c.fechaUltimaModificacion,
        ).order_by(_lugares.c.id)
    ).mappings().all()
    serialized = [_serialize_status_lugar(dict(row)) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear status de lugar")
async def statuslugar_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    descripcion = payload.get("descripcion") or payload.get("lugar")
    if not descripcion:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="descripcion es requerido")

    existing = db.execute(select(_lugares.c.id).where(_lugares.c.lugar == descripcion).limit(1)).scalar_one_or_none()
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": descripcion}])

    try:
        now = datetime.utcnow()
        new_id = int(
            db.execute(
                insert(_lugares)
                .values(
                    lugar=descripcion,
                    activo=bool(payload.get("activo", True)),
                    fechaAlta=now,
                    fechaUltimaModificacion=now,
                )
                .returning(_lugares.c.id)
            ).scalar_one()
        )
        db.commit()
        row = db.execute(
            select(
                _lugares.c.id,
                _lugares.c.lugar,
                _lugares.c.activo,
                _lugares.c.fechaAlta,
                _lugares.c.fechaUltimaModificacion,
            ).where(_lugares.c.id == new_id)
        ).mappings().first()
        return fastapi_response(_serialize_status_lugar(dict(row)) if row else None, status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar status de lugar")
async def statuslugar_update(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    status_id = int(payload.get("id"))
    exists = db.execute(select(_lugares.c.id).where(_lugares.c.id == status_id)).scalar_one_or_none()
    if not exists:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if payload.get("descripcion") is not None:
        update_values["lugar"] = payload.get("descripcion")
    if payload.get("lugar") is not None:
        update_values["lugar"] = payload.get("lugar")
    if payload.get("activo") is not None:
        update_values["activo"] = bool(payload.get("activo"))

    if not update_values:
        unchanged = db.execute(
            select(
                _lugares.c.id,
                _lugares.c.lugar,
                _lugares.c.activo,
                _lugares.c.fechaAlta,
                _lugares.c.fechaUltimaModificacion,
            ).where(_lugares.c.id == status_id)
        ).mappings().first()
        return fastapi_response(_serialize_status_lugar(dict(unchanged)) if unchanged else None, status.HTTP_200_OK, "TPM-6")

    update_values["fechaUltimaModificacion"] = datetime.utcnow()
    try:
        db.execute(update(_lugares).where(_lugares.c.id == status_id).values(**update_values))
        db.commit()
        updated = db.execute(
            select(
                _lugares.c.id,
                _lugares.c.lugar,
                _lugares.c.activo,
                _lugares.c.fechaAlta,
                _lugares.c.fechaUltimaModificacion,
            ).where(_lugares.c.id == status_id)
        ).mappings().first()
        return fastapi_response(_serialize_status_lugar(dict(updated)) if updated else None, status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener status de lugar por ID")
async def statuslugar_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        select(
            _lugares.c.id,
            _lugares.c.lugar,
            _lugares.c.activo,
            _lugares.c.fechaAlta,
            _lugares.c.fechaUltimaModificacion,
        ).where(_lugares.c.id == id)
    ).mappings().first()
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(_serialize_status_lugar(dict(row)), status.HTTP_200_OK, "TPM-3")
