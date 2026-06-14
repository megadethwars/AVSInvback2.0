from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import MetaData, Table, insert, select, update
from sqlalchemy.orm import Session

from ...database import engine, get_db
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/tipomovimientos", tags=["TipoMovimientos"])

_metadata = MetaData()
_tipos_mov = Table("invTipoMoves", _metadata, autoload_with=engine)


def _serialize_tipo(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "tipo": row.get("tipo"),
        "fechaAlta": row.get("fechaAlta").isoformat() if row.get("fechaAlta") else None,
        "fechaUltimaModificacion": row.get("fechaUltimaModificacion").isoformat() if row.get("fechaUltimaModificacion") else None,
    }


@router.get("", summary="Listar tipos de movimiento")
async def tipomovimientos_list(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(
            _tipos_mov.c.id,
            _tipos_mov.c.tipo,
            _tipos_mov.c.fechaAlta,
            _tipos_mov.c.fechaUltimaModificacion,
        ).order_by(_tipos_mov.c.id)
    ).mappings().all()
    serialized = [_serialize_tipo(dict(row)) for row in rows]
    return fastapi_response(serialized, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear tipo de movimiento")
async def tipomovimientos_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    tipo = payload.get("tipo")
    if not tipo:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="tipo es requerido")

    existing = db.execute(select(_tipos_mov.c.id).where(_tipos_mov.c.tipo == tipo).limit(1)).scalar_one_or_none()
    if existing:
        return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[{"object": tipo}])

    try:
        now = datetime.utcnow()
        new_id = int(
            db.execute(
                insert(_tipos_mov)
                .values(tipo=tipo, fechaAlta=now, fechaUltimaModificacion=now)
                .returning(_tipos_mov.c.id)
            ).scalar_one()
        )
        db.commit()
        row = db.execute(
            select(
                _tipos_mov.c.id,
                _tipos_mov.c.tipo,
                _tipos_mov.c.fechaAlta,
                _tipos_mov.c.fechaUltimaModificacion,
            ).where(_tipos_mov.c.id == new_id)
        ).mappings().first()
        return fastapi_response(_serialize_tipo(dict(row)) if row else None, status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar tipo de movimiento")
async def tipomovimientos_update(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

    tipo_id = int(payload.get("id"))
    exists = db.execute(select(_tipos_mov.c.id).where(_tipos_mov.c.id == tipo_id)).scalar_one_or_none()
    if not exists:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_values = {}
    if "tipo" in payload and payload.get("tipo") is not None:
        update_values["tipo"] = payload.get("tipo")

    if not update_values:
        unchanged = db.execute(
            select(
                _tipos_mov.c.id,
                _tipos_mov.c.tipo,
                _tipos_mov.c.fechaAlta,
                _tipos_mov.c.fechaUltimaModificacion,
            ).where(_tipos_mov.c.id == tipo_id)
        ).mappings().first()
        return fastapi_response(_serialize_tipo(dict(unchanged)) if unchanged else None, status.HTTP_200_OK, "TPM-6")

    update_values["fechaUltimaModificacion"] = datetime.utcnow()
    try:
        db.execute(update(_tipos_mov).where(_tipos_mov.c.id == tipo_id).values(**update_values))
        db.commit()
        updated = db.execute(
            select(
                _tipos_mov.c.id,
                _tipos_mov.c.tipo,
                _tipos_mov.c.fechaAlta,
                _tipos_mov.c.fechaUltimaModificacion,
            ).where(_tipos_mov.c.id == tipo_id)
        ).mappings().first()
        return fastapi_response(_serialize_tipo(dict(updated)) if updated else None, status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener tipo de movimiento por ID")
async def tipomovimientos_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        select(
            _tipos_mov.c.id,
            _tipos_mov.c.tipo,
            _tipos_mov.c.fechaAlta,
            _tipos_mov.c.fechaUltimaModificacion,
        ).where(_tipos_mov.c.id == id)
    ).mappings().first()
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(_serialize_tipo(dict(row)), status.HTTP_200_OK, "TPM-3")
