from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.JobMovimientosModelSchema import JobMovimientosModel, JobMovimientosSchemaCreate, JobMovimientosSchemaUpdate
from ...shared.returnCodes import fastapi_response

router = APIRouter(prefix="/api/v1/jobmovimientos", tags=["JobMovimientos"])


@router.get("", summary="Listar jobs de movimientos")
async def job_movimientos_list(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict:
    rows = JobMovimientosModel.list_all(db, offset=offset, limit=limit)
    payload = [JobMovimientosModel.to_dict(row) for row in rows]
    return fastapi_response(payload, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear job de movimientos")
async def job_movimientos_create(payload: JobMovimientosSchemaCreate, db: Session = Depends(get_db)) -> dict:
    try:
        now = datetime.utcnow()
        created = JobMovimientosModel.create_job(
            db,
            {
                "idMovimiento": payload.idMovimiento,
                "usuarioId": payload.usuarioId,
                "tipoMovId": payload.tipoMovId,
                "LugarId": payload.LugarId,
                "comentarios": payload.comentarios,
                "estado": payload.estado,
                "status": payload.status,
                "fechaAlta": payload.fechaAlta or now,
                "fechaUltimaModificacion": payload.fechaUltimaModificacion or now,
            },
        )
        return fastapi_response(JobMovimientosModel.to_dict(created), status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar job de movimientos")
async def job_movimientos_update(payload: JobMovimientosSchemaUpdate, db: Session = Depends(get_db)) -> dict:
    row = JobMovimientosModel.get_one(db, int(payload.id))
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

    update_data = {}
    if payload.idMovimiento is not None:
        update_data["idMovimiento"] = payload.idMovimiento
    if payload.usuarioId is not None:
        update_data["usuarioId"] = payload.usuarioId
    if payload.tipoMovId is not None:
        update_data["tipoMovId"] = payload.tipoMovId
    if payload.LugarId is not None:
        update_data["LugarId"] = payload.LugarId
    if payload.comentarios is not None:
        update_data["comentarios"] = payload.comentarios
    if payload.estado is not None:
        update_data["estado"] = payload.estado
    if payload.status is not None:
        update_data["status"] = payload.status

    if not update_data:
        return fastapi_response(JobMovimientosModel.to_dict(row), status.HTTP_200_OK, "TPM-6")

    try:
        updated = row.update(db, update_data)
        return fastapi_response(JobMovimientosModel.to_dict(updated), status.HTTP_200_OK, "TPM-6")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/movement/{id_movimiento}", summary="Obtener ultimo job por idMovimiento")
async def job_movimientos_get_by_movement(id_movimiento: str, db: Session = Depends(get_db)) -> dict:
    row = JobMovimientosModel.get_latest_by_id_movimiento(db, id_movimiento)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(JobMovimientosModel.to_dict(row), status.HTTP_200_OK, "TPM-3")


@router.get("/{id}", summary="Obtener job de movimientos por ID")
async def job_movimientos_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    row = JobMovimientosModel.get_one(db, id)
    if not row:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(JobMovimientosModel.to_dict(row), status.HTTP_200_OK, "TPM-3")
