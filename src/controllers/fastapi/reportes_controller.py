from datetime import date, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.ReportesModelSchema import ReportesModel
from ...models.UsuariosModelSchema import UsuariosModel
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])
def _fetch_reporte_by_id(db: Session, reporte_id: int) -> dict | None:
    return ReportesModel.fetch_by_id(db, reporte_id)


@router.get("", summary="Listar reportes")
async def reportes_list(db: Session = Depends(get_db)) -> dict:
    reportes = ReportesModel.list_all(db)
    return fastapi_response(reportes, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear reporte")
async def reportes_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    try:
        dispositivo_id = payload.get("dispositivoId")
        usuario_id = payload.get("usuarioId")
        comentarios = payload.get("comentarios")
        foto = payload.get("foto")

        existe_dispositivo = DispositivosModel.get_one_device(db, int(dispositivo_id))
        if not existe_dispositivo:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(dispositivo_id))])

        existe_usuario = UsuariosModel.fetch_by_id(db, int(usuario_id))
        if not existe_usuario:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(usuario_id))])

        now = datetime.utcnow()
        reporte = ReportesModel.create_reporte(
            db,
            {
                "dispositivoId": dispositivo_id,
                "usuarioId": usuario_id,
                "comentarios": comentarios,
                "foto": foto,
                "fechaAlta": now,
                "fechaUltimaModificacion": now,
            },
        )

        existe_dispositivo.descompostura = comentarios
        db.add(existe_dispositivo)
        db.commit()
        reporte_id = int(reporte.id)

        reporte_completo = _fetch_reporte_by_id(db, reporte_id)
        return fastapi_response(reporte_completo, status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar reporte")
async def reportes_update(payload: dict) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="reportes.update pendiente de migracion")


@router.get("/{id}", summary="Obtener reporte por ID")
async def reportes_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    reporte = _fetch_reporte_by_id(db, id)
    if not reporte:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(reporte, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar reportes")
async def reportes_query() -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="reportes.query pendiente de migracion")


@router.get("/filter/{value}", summary="Filtrar reportes")
async def reportes_filter(value: str) -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message=f"reportes.filter({value}) pendiente de migracion")
