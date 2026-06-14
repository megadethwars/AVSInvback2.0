from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.orm import Session

from ...database import engine, get_db
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/statusUsuarios", tags=["EstatusUsuarios"])

_metadata = MetaData()
_status_usuarios = Table("invStatusUsuarios", _metadata, autoload_with=engine)


def _serialize_status(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "descripcion": row.get("descripcion"),
        "fechaAlta": row.get("fechaAlta").isoformat() if row.get("fechaAlta") else None,
        "fechaUltimaModificacion": row.get("fechaUltimaModificacion").isoformat() if row.get("fechaUltimaModificacion") else None,
    }


@router.get("", summary="Listar estatus de usuarios")
async def estatususuarios_list(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(
            _status_usuarios.c.id,
            _status_usuarios.c.descripcion,
            _status_usuarios.c.fechaAlta,
            _status_usuarios.c.fechaUltimaModificacion,
        ).order_by(_status_usuarios.c.id)
    ).mappings().all()
    serialized = [_serialize_status(dict(row)) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear estatus de usuario")
async def estatususuarios_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    descripcion = payload.get("descripcion")
    if not descripcion:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="descripcion es requerido")

    existing = db.execute(
        select(_status_usuarios.c.id).where(_status_usuarios.c.descripcion == descripcion).limit(1)
    ).scalar_one_or_none()
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": descripcion}])

    try:
        now = datetime.utcnow()
        new_id = int(
            db.execute(
                insert(_status_usuarios)
                .values(descripcion=descripcion, fechaAlta=now, fechaUltimaModificacion=now)
                .returning(_status_usuarios.c.id)
            ).scalar_one()
        )
        db.commit()
        row = db.execute(
            select(
                _status_usuarios.c.id,
                _status_usuarios.c.descripcion,
                _status_usuarios.c.fechaAlta,
                _status_usuarios.c.fechaUltimaModificacion,
            ).where(_status_usuarios.c.id == new_id)
        ).mappings().first()
        return fastapi_response(_serialize_status(dict(row)) if row else None, status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar estatus de usuario")
async def estatususuarios_update(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    status_id = int(payload.get("id"))
    exists = db.execute(select(_status_usuarios.c.id).where(_status_usuarios.c.id == status_id)).scalar_one_or_none()
    if not exists:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if "descripcion" in payload and payload.get("descripcion") is not None:
        update_values["descripcion"] = payload.get("descripcion")

    if not update_values:
        unchanged = db.execute(
            select(
                _status_usuarios.c.id,
                _status_usuarios.c.descripcion,
                _status_usuarios.c.fechaAlta,
                _status_usuarios.c.fechaUltimaModificacion,
            ).where(_status_usuarios.c.id == status_id)
        ).mappings().first()
        return fastapi_response(_serialize_status(dict(unchanged)) if unchanged else None, status.HTTP_200_OK, "TPM-6")

    update_values["fechaUltimaModificacion"] = datetime.utcnow()
    try:
        db.execute(update(_status_usuarios).where(_status_usuarios.c.id == status_id).values(**update_values))
        db.commit()
        updated = db.execute(
            select(
                _status_usuarios.c.id,
                _status_usuarios.c.descripcion,
                _status_usuarios.c.fechaAlta,
                _status_usuarios.c.fechaUltimaModificacion,
            ).where(_status_usuarios.c.id == status_id)
        ).mappings().first()
        return fastapi_response(_serialize_status(dict(updated)) if updated else None, status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener estatus de usuario por ID")
async def estatususuarios_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        select(
            _status_usuarios.c.id,
            _status_usuarios.c.descripcion,
            _status_usuarios.c.fechaAlta,
            _status_usuarios.c.fechaUltimaModificacion,
        ).where(_status_usuarios.c.id == id)
    ).mappings().first()
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(_serialize_status(dict(row)), status.HTTP_200_OK, "TPM-3")
