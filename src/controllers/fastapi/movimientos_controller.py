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


def _json_safe_dict(record: dict | None) -> dict | None:
	if record is None:
		return None

	output = {}
	for key, value in record.items():
		if isinstance(value, datetime):
			output[key] = value.isoformat()
		else:
			output[key] = value
	return output


def _get_lugar(db: Session, lugar_id: int | None) -> dict | None:
	if lugar_id is None:
		return None
	query = text(
		"""
		SELECT id, lugar, fechaAlta, fechaUltimaModificacion, activo
		FROM invLugares
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": lugar_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_status_device(db: Session, status_id: int | None) -> dict | None:
	if status_id is None:
		return None
	query = text(
		"""
		SELECT id, descripcion, fechaAlta, fechaUltimaModificacion
		FROM invStatusDevices
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": status_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_tipo_movimiento(db: Session, tipo_mov_id: int | None) -> dict | None:
	if tipo_mov_id is None:
		return None
	query = text(
		"""
		SELECT id, tipo, fechaAlta, fechaUltimaModificacion
		FROM invTipoMoves
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": tipo_mov_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_rol(db: Session, rol_id: int | None) -> dict | None:
	if rol_id is None:
		return None
	query = text(
		"""
		SELECT id, nombre, fechaAlta, fechaUltimaModificacion
		FROM invRoles
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": rol_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_status_usuario(db: Session, status_id: int | None) -> dict | None:
	if status_id is None:
		return None
	query = text(
		"""
		SELECT id, descripcion, fechaAlta, fechaUltimaModificacion
		FROM invStatusUsuarios
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": status_id}).mappings().first()
	return _json_safe_dict(dict(row)) if row else None


def _get_usuario(db: Session, usuario_id: int | None) -> dict | None:
	if usuario_id is None:
		return None
	query = text(
		"""
		SELECT id, nombre, username, apellidoPaterno, apellidoMaterno, password, telefono, correo, foto, rolId, statusId,
			   fechaAlta, fechaUltimaModificacion
		FROM invUsuarios
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": usuario_id}).mappings().first()
	if not row:
		return None

	usuario = _json_safe_dict(dict(row))
	usuario["rol"] = _get_rol(db, usuario.get("rolId"))
	usuario["status"] = _get_status_usuario(db, usuario.get("statusId"))
	return usuario


def _get_dispositivo(db: Session, dispositivo_id: int | None) -> dict | None:
	if dispositivo_id is None:
		return None
	query = text(
		"""
		SELECT id, codigo, producto, marca, modelo, origen, foto, cantidad, observaciones, lugarId, pertenece,
			   descompostura, costo, compra, proveedor, idMov, statusId, fechaAlta, fechaUltimaModificacion,
			   serie, accesorios
		FROM invDispositivos
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": dispositivo_id}).mappings().first()
	if not row:
		return None

	dispositivo = _json_safe_dict(dict(row))
	dispositivo["lugar"] = _get_lugar(db, dispositivo.get("lugarId"))
	dispositivo["status"] = _get_status_device(db, dispositivo.get("statusId"))
	return dispositivo


def _build_movimiento_response(db: Session, movimiento_id: int) -> dict | None:
	query = text(
		"""
		SELECT id, idMovimiento, dispositivoId, usuarioId, tipoMovId, LugarId, comentarios, foto, foto2,
			   fechaAlta, fechaUltimaModificacion, cantidad_Actual
		FROM invMovimientos
		WHERE id = :id
		"""
	)
	row = db.execute(query, {"id": movimiento_id}).mappings().first()
	if not row:
		return None

	movimiento = _json_safe_dict(dict(row))
	movimiento["lugar"] = _get_lugar(db, movimiento.get("LugarId"))
	movimiento["dispositivo"] = _get_dispositivo(db, movimiento.get("dispositivoId"))
	movimiento["tipoMovimiento"] = _get_tipo_movimiento(db, movimiento.get("tipoMovId"))
	movimiento["usuario"] = _get_usuario(db, movimiento.get("usuarioId"))
	return movimiento


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

			movimiento_completo = _build_movimiento_response(db, created_id)
			if movimiento_completo:
				lista_objetos_creados.append(movimiento_completo)
			else:
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
async def movimientos_update(payload: dict, db: Session = Depends(get_db)) -> dict:
	if not payload:
		return _legacy_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

	try:
		movimiento_id = payload.get("id")
		existe_mov = db.execute(text("SELECT id FROM invMovimientos WHERE id = :id"), {"id": movimiento_id}).scalar_one_or_none()
		if not existe_mov:
			return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

		dispositivo_id = payload.get("dispositivoId")
		if dispositivo_id:
			existe_dispositivo = db.execute(text("SELECT id FROM invDispositivos WHERE id = :id"), {"id": dispositivo_id}).scalar_one_or_none()
			if not existe_dispositivo:
				return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=dispositivo_id)

		lugar_id = payload.get("LugarId")
		if lugar_id:
			existe_lugar = db.execute(text("SELECT id FROM invLugares WHERE id = :id"), {"id": lugar_id}).scalar_one_or_none()
			if not existe_lugar:
				return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=lugar_id)

		tipo_mov_id = payload.get("tipoMovId")
		if tipo_mov_id:
			existe_tipo = db.execute(text("SELECT id FROM invTipoMoves WHERE id = :id"), {"id": tipo_mov_id}).scalar_one_or_none()
			if not existe_tipo:
				return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=tipo_mov_id)

		usuario_id = payload.get("usuarioId")
		if usuario_id:
			existe_usuario = db.execute(text("SELECT id FROM invUsuarios WHERE id = :id"), {"id": usuario_id}).scalar_one_or_none()
			if not existe_usuario:
				return _legacy_response(None, status.HTTP_409_CONFLICT, "TPM-4", item=usuario_id)

		now = datetime.utcnow()
		update_query = text(
			"""
			UPDATE invMovimientos
			SET dispositivoId = COALESCE(:dispositivoId, dispositivoId),
				LugarId = COALESCE(:LugarId, LugarId),
				tipoMovId = COALESCE(:tipoMovId, tipoMovId),
				cantidad = COALESCE(:cantidad, cantidad),
				usuarioId = COALESCE(:usuarioId, usuarioId),
				observaciones = COALESCE(:observaciones, observaciones),
				fechaUltimaModificacion = :fechaUltimaModificacion
			WHERE id = :id
			"""
		)
		db.execute(update_query, {
			"id": movimiento_id,
			"dispositivoId": dispositivo_id,
			"LugarId": lugar_id,
			"tipoMovId": tipo_mov_id,
			"cantidad": payload.get("cantidad"),
			"usuarioId": usuario_id,
			"observaciones": payload.get("observaciones"),
			"fechaUltimaModificacion": now
		})
		db.commit()

		movimiento_completo = _build_movimiento_response(db, movimiento_id)
		return _legacy_response(movimiento_completo, status.HTTP_200_OK, "TPM-6")
	except Exception as err:
		db.rollback()
		return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))


@router.get("/{id}", summary="Obtener movimiento por ID")
async def movimientos_get_one(id: int, db: Session = Depends(get_db)) -> dict:
	movimiento = _build_movimiento_response(db, id)
	if not movimiento:
		return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return _legacy_response(movimiento, status.HTTP_200_OK, "TPM-3")


@router.get("/LastOne/{id}", summary="Obtener ultimo movimiento por dispositivo")
async def movimientos_last_one(id: int, db: Session = Depends(get_db)) -> dict:
	query = text(
		"""
		SELECT TOP 1 id FROM invMovimientos 
		WHERE dispositivoId = :dispositivo_id AND tipoMovId = 1 
		ORDER BY fechaAlta DESC
		"""
	)
	last_mov_id = db.execute(query, {"dispositivo_id": id}).scalar_one_or_none()
	if not last_mov_id:
		return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

	movimiento = _build_movimiento_response(db, last_mov_id)
	if not movimiento:
		return _legacy_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return _legacy_response(movimiento, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar movimientos")
async def movimientos_query(payload: dict, db: Session = Depends(get_db)) -> dict:
	base_query = "SELECT id, dispositivoId, LugarId, tipoMovId, cantidad, usuarioId, observaciones, fechaAlta, fechaUltimaModificacion FROM invMovimientos WHERE 1=1"
	params = {}

	if payload.get("dispositivoId"):
		base_query += " AND dispositivoId = :dispositivoId"
		params["dispositivoId"] = payload.get("dispositivoId")

	if payload.get("LugarId"):
		base_query += " AND LugarId = :LugarId"
		params["LugarId"] = payload.get("LugarId")

	if payload.get("tipoMovId"):
		base_query += " AND tipoMovId = :tipoMovId"
		params["tipoMovId"] = payload.get("tipoMovId")

	if payload.get("usuarioId"):
		base_query += " AND usuarioId = :usuarioId"
		params["usuarioId"] = payload.get("usuarioId")

	base_query += " ORDER BY fechaAlta DESC"

	try:
		rows = db.execute(text(base_query), params).mappings().fetchall()
		movimientos = []
		for row in rows:
			mov_dict = _json_safe_dict(dict(row))
			mov_dict["lugar"] = _get_lugar(db, mov_dict.get("LugarId"))
			mov_dict["dispositivo"] = _get_dispositivo(db, mov_dict.get("dispositivoId"))
			mov_dict["tipoMovimiento"] = _get_tipo_movimiento(db, mov_dict.get("tipoMovId"))
			mov_dict["usuario"] = _get_usuario(db, mov_dict.get("usuarioId"))
			movimientos.append(mov_dict)

		return _legacy_response(movimientos, status.HTTP_200_OK, "TPM-3", is_query=True, total=len(movimientos))
	except Exception as err:
		return _legacy_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", str(err))


@router.get("/filter", summary="Filtrar movimientos")
async def movimientos_filter() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.filter pendiente de migracion")


@router.get("/filtermovementFields", summary="Filtrar movimientos campos minimos")
async def movimientos_filter_fields() -> dict:
	return _legacy_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", "movimientos.filtermovementFields pendiente de migracion")
