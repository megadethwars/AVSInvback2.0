from datetime import datetime

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.LugaresModel import LugaresModel
from ...schemas import MovimientosCreate
from ...shared import returnCodes

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])


def _legacy_response(res, status_code: int, app_code: str, message: str = "", item=None, is_query: bool = False, total: int = 0) -> JSONResponse:
	message_list = []
	if message == "":
		message_list.append({"status": returnCodes.app_codes[app_code]})
	else:
		message_list.append({"status": str(message)})

	if item is None:
		item = []

	if isinstance(item, list):
		for x in item:
			message_list.append(x)
	elif item != "":
		message_list.append({"object": item})

	payload = {
		"app_code": app_code,
		"message": message_list,
		"data": res,
	}
	if is_query:
		payload["total_rows"] = total

	return JSONResponse(status_code=status_code, content=payload)


def _usuario_exists(db: Session, usuario_id: int) -> bool:
	query = text("SELECT TOP 1 id FROM invUsuarios WHERE id = :usuario_id")
	return db.execute(query, {"usuario_id": usuario_id}).scalar_one_or_none() is not None


def _tipo_mov_exists(db: Session, tipo_mov_id: int) -> bool:
	query = text("SELECT TOP 1 id FROM invTipoMoves WHERE id = :tipo_mov_id")
	return db.execute(query, {"tipo_mov_id": tipo_mov_id}).scalar_one_or_none() is not None


def _insert_movimiento(db: Session, data: dict) -> int:
	query = text(
		"""
		INSERT INTO invMovimientos (
			idMovimiento,
			dispositivoId,
			usuarioId,
			tipoMovId,
			LugarId,
			comentarios,
			foto,
			foto2,
			fechaAlta,
			fechaUltimaModificacion,
			cantidad_Actual
		)
		OUTPUT INSERTED.id
		VALUES (
			:idMovimiento,
			:dispositivoId,
			:usuarioId,
			:tipoMovId,
			:LugarId,
			:comentarios,
			:foto,
			:foto2,
			:fechaAlta,
			:fechaUltimaModificacion,
			:cantidad_Actual
		)
		"""
	)
	return int(db.execute(query, data).scalar_one())


@router.get("", summary="Listar movimientos")
async def movimientos_list() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.list pendiente de migracion")


@router.post("", summary="Crear movimiento")
async def movimientos_create(payload: dict, db: Session = Depends(get_db)) -> dict:
	if not payload:
		return _legacy_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

	try:
		movimientos_raw = payload.get("movimientosList", payload)
		if isinstance(movimientos_raw, dict):
			movimientos_raw = [movimientos_raw]
		if not isinstance(movimientos_raw, list):
			raise ValueError("movimientosList debe ser una lista")
		movimientos = [MovimientosCreate.model_validate(item).model_dump(exclude_none=True) for item in movimientos_raw]
	except Exception as err:
		return _legacy_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", str(err))

	lista_objetos_creados = []
	lista_errores = []

	for item in movimientos:
		dispositivo = DispositivosModel.get_one_device(db, item.get("dispositivoId"))
		if not dispositivo:
			lista_errores.append(returnCodes.partial_response("TPM-5", "el dispositivo no existe", item.get("dispositivoId"), item.get("id", 0)))
			continue

		lugar = LugaresModel.get_one_lugar(db, item.get("LugarId"))
		if not lugar:
			lista_errores.append(returnCodes.partial_response("TPM-4", "el lugar no existe", item.get("LugarId"), item.get("id", 0)))
			continue

		if not _usuario_exists(db, int(item.get("usuarioId"))):
			lista_errores.append(returnCodes.partial_response("TPM-5", "el usuario no existe", item.get("usuarioId"), item.get("id", 0)))
			continue

		if not _tipo_mov_exists(db, int(item.get("tipoMovId"))):
			lista_errores.append(returnCodes.partial_response("TPM-5", "el tipo de movimiento no existe", item.get("tipoMovId"), item.get("id", 0)))
			continue

		cantidad_actual = int(item.get("cantidad_Actual") or 1)
		if cantidad_actual <= 0:
			cantidad_actual = 1

		diferencia = dispositivo.cantidad or 0
		if item.get("tipoMovId") == 1:
			diferencia = (dispositivo.cantidad or 0) - cantidad_actual
		elif item.get("tipoMovId") == 2:
			diferencia = (dispositivo.cantidad or 0) + cantidad_actual

		if diferencia < 0:
			lista_errores.append(returnCodes.partial_response("TPM-17", "", item.get("dispositivoId"), item.get("id", 0)))
			continue

		now = datetime.utcnow()
		insert_data = {
			"idMovimiento": item.get("idMovimiento"),
			"dispositivoId": item.get("dispositivoId"),
			"usuarioId": item.get("usuarioId"),
			"tipoMovId": item.get("tipoMovId"),
			"LugarId": item.get("LugarId"),
			"comentarios": item.get("comentarios"),
			"foto": item.get("foto"),
			"foto2": item.get("foto2"),
			"fechaAlta": now,
			"fechaUltimaModificacion": now,
			"cantidad_Actual": cantidad_actual,
		}

		try:
			dispositivo.cantidad = diferencia
			dispositivo.lugarId = int(item.get("LugarId"))
			dispositivo.fechaUltimaModificacion = now
			created_id = _insert_movimiento(db, insert_data)
			db.add(dispositivo)
			db.commit()

			lista_objetos_creados.append(
				{
					"id": created_id,
					"dispositivoId": item.get("dispositivoId"),
					"usuarioId": item.get("usuarioId"),
					"idMovimiento": item.get("idMovimiento"),
					"tipoMovId": item.get("tipoMovId"),
					"LugarId": item.get("LugarId"),
					"comentarios": item.get("comentarios"),
					"foto": item.get("foto"),
					"foto2": item.get("foto2"),
					"cantidad_Actual": cantidad_actual,
					"fechaAlta": now.isoformat(),
					"fechaUltimaModificacion": now.isoformat(),
				}
			)
		except Exception as err:
			db.rollback()
			lista_errores.append(returnCodes.partial_response("TPM-7", "", str(err), item.get("id", 0)))

	if len(lista_objetos_creados) > 0:
		if len(lista_errores) == 0:
			return _legacy_response(lista_objetos_creados, status.HTTP_201_CREATED, "TPM-8")
		return _legacy_response(lista_objetos_creados, status.HTTP_201_CREATED, "TPM-16", item=lista_errores)

	return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-16", item=lista_errores)


@router.put("", summary="Actualizar movimiento")
async def movimientos_update() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.update pendiente de migracion")


@router.get("/{id}", summary="Obtener movimiento por ID")
async def movimientos_get_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"movimientos.get({id}) pendiente de migracion")


@router.get("/LastOne/{id}", summary="Obtener ultimo movimiento por dispositivo")
async def movimientos_last_one(id: int) -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", f"movimientos.lastone({id}) pendiente de migracion")


@router.post("/query", summary="Consultar movimientos")
async def movimientos_query() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.query pendiente de migracion")


@router.get("/filter", summary="Filtrar movimientos")
async def movimientos_filter() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.filter pendiente de migracion")


@router.get("/filtermovementFields", summary="Filtrar movimientos campos minimos")
async def movimientos_filter_fields() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.filtermovementFields pendiente de migracion")
