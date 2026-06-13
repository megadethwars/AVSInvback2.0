from datetime import date, datetime

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.DispositivosModel import DispositivosModel
from ...models.LugaresModel import LugaresModel
from ...schemas import MovimientosCreate
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/movimientos", tags=["Movimientos"])


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


def _json_safe_value(value):
	if isinstance(value, (datetime, date)):
		return value.isoformat()
	if isinstance(value, dict):
		return {key: _json_safe_value(item) for key, item in value.items()}
	if isinstance(value, list):
		return [_json_safe_value(item) for item in value]
	return value


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


def _build_movimiento_from_joined_row(row: dict) -> dict:
	movimiento = {
		"id": row.get("movimiento_id"),
		"idMovimiento": row.get("movimiento_idMovimiento"),
		"dispositivoId": row.get("movimiento_dispositivoId"),
		"usuarioId": row.get("movimiento_usuarioId"),
		"tipoMovId": row.get("movimiento_tipoMovId"),
		"LugarId": row.get("movimiento_LugarId"),
		"comentarios": row.get("movimiento_comentarios"),
		"foto": row.get("movimiento_foto"),
		"foto2": row.get("movimiento_foto2"),
		"fechaAlta": row.get("movimiento_fechaAlta"),
		"fechaUltimaModificacion": row.get("movimiento_fechaUltimaModificacion"),
		"cantidad_Actual": row.get("movimiento_cantidad_Actual"),
	}

	dispositivo = {
		"id": row.get("dispositivo_id"),
		"codigo": row.get("dispositivo_codigo"),
		"producto": row.get("dispositivo_producto"),
		"marca": row.get("dispositivo_marca"),
		"modelo": row.get("dispositivo_modelo"),
		"origen": row.get("dispositivo_origen"),
		"foto": row.get("dispositivo_foto"),
		"cantidad": row.get("dispositivo_cantidad"),
		"observaciones": row.get("dispositivo_observaciones"),
		"lugarId": row.get("dispositivo_lugarId"),
		"pertenece": row.get("dispositivo_pertenece"),
		"descompostura": row.get("dispositivo_descompostura"),
		"costo": row.get("dispositivo_costo"),
		"compra": row.get("dispositivo_compra"),
		"proveedor": row.get("dispositivo_proveedor"),
		"idMov": row.get("dispositivo_idMov"),
		"statusId": row.get("dispositivo_statusId"),
		"serie": row.get("dispositivo_serie"),
		"accesorios": row.get("dispositivo_accesorios"),
	}
	dispositivo_lugar = {
		"id": row.get("dispositivo_lugar_id"),
		"lugar": row.get("dispositivo_lugar_lugar"),
		"activo": row.get("dispositivo_lugar_activo"),
		"fechaAlta": row.get("dispositivo_lugar_fechaAlta"),
		"fechaUltimaModificacion": row.get("dispositivo_lugar_fechaUltimaModificacion"),
	}
	dispositivo_status = {
		"id": row.get("dispositivo_status_id"),
		"descripcion": row.get("dispositivo_status_descripcion"),
		"fechaAlta": row.get("dispositivo_status_fechaAlta"),
		"fechaUltimaModificacion": row.get("dispositivo_status_fechaUltimaModificacion"),
	}
	dispositivo["lugar"] = dispositivo_lugar if any(v is not None for v in dispositivo_lugar.values()) else None
	dispositivo["status"] = dispositivo_status if any(v is not None for v in dispositivo_status.values()) else None

	lugar = {
		"id": row.get("lugar_id"),
		"lugar": row.get("lugar_lugar"),
		"activo": row.get("lugar_activo"),
		"fechaAlta": row.get("lugar_fechaAlta"),
		"fechaUltimaModificacion": row.get("lugar_fechaUltimaModificacion"),
	}

	tipo_movimiento = {
		"id": row.get("tipoMovimiento_id"),
		"tipo": row.get("tipoMovimiento_tipo"),
		"fechaAlta": row.get("tipoMovimiento_fechaAlta"),
		"fechaUltimaModificacion": row.get("tipoMovimiento_fechaUltimaModificacion"),
	}

	usuario = {
		"id": row.get("usuario_id"),
		"nombre": row.get("usuario_nombre"),
		"username": row.get("usuario_username"),
		"apellidoPaterno": row.get("usuario_apellidoPaterno"),
		"apellidoMaterno": row.get("usuario_apellidoMaterno"),
		"password": row.get("usuario_password"),
		"telefono": row.get("usuario_telefono"),
		"correo": row.get("usuario_correo"),
		"foto": row.get("usuario_foto"),
		"rolId": row.get("usuario_rolId"),
		"statusId": row.get("usuario_statusId"),
		"fechaAlta": row.get("usuario_fechaAlta"),
		"fechaUltimaModificacion": row.get("usuario_fechaUltimaModificacion"),
	}

	movimiento["lugar"] = lugar if any(v is not None for v in lugar.values()) else None
	movimiento["dispositivo"] = dispositivo if any(v is not None for v in dispositivo.values()) else None
	movimiento["tipoMovimiento"] = tipo_movimiento if any(v is not None for v in tipo_movimiento.values()) else None
	movimiento["usuario"] = usuario if any(v is not None for v in usuario.values()) else None
	return _json_safe_value(movimiento)


def _fetch_movimientos_some_fields(
	db: Session,
	offset: int,
	limit: int,
	search_value: str | None = None,
) -> tuple[list[dict], int]:
	base_from = """
		FROM invMovimientos m
		LEFT JOIN invDispositivos d ON d.id = m.dispositivoId
		LEFT JOIN invLugares l ON l.id = m.LugarId
		LEFT JOIN invTipoMoves tm ON tm.id = m.tipoMovId
		LEFT JOIN invUsuarios u ON u.id = m.usuarioId
	"""

	where_clause = ""
	params: dict = {"offset": int(offset), "limit": int(limit)}

	if search_value:
		where_clause = """
			WHERE
				d.codigo LIKE :pattern OR
				d.producto LIKE :pattern OR
				m.idMovimiento LIKE :pattern OR
				l.lugar LIKE :pattern OR
				tm.tipo LIKE :pattern OR
				u.nombre LIKE :pattern OR
				u.username LIKE :pattern
		"""
		params["pattern"] = f"%{search_value}%"

	count_query = text(f"SELECT COUNT(1) {base_from} {where_clause}")
	total_rows = int(db.execute(count_query, params).scalar() or 0)

	data_query = text(
		f"""
		SELECT
			m.id,
			d.codigo,
			d.producto,
			m.fechaAlta,
			m.idMovimiento,
			l.lugar,
			tm.tipo,
			u.nombre,
			u.username
		{base_from}
		{where_clause}
		ORDER BY m.fechaAlta DESC
		OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
		"""
	)

	rows = db.execute(data_query, params).mappings().all()
	serialized = [_json_safe_dict(dict(row)) for row in rows]
	return serialized, total_rows


@router.get("", summary="Listar movimientos")
async def movimientos_list(
	offset: int = 0,
	limit: int = 10,
	db: Session = Depends(get_db),
) -> dict:
	try:
		movimientos, total_rows = _fetch_movimientos_some_fields(db, offset, limit)
		return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)
	except Exception as err:
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.post("", summary="Crear movimiento")
async def movimientos_create(payload: dict, db: Session = Depends(get_db)) -> dict:
	if not payload:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

	try:
		movimientos_raw = payload.get("movimientosList", payload)
		if isinstance(movimientos_raw, dict):
			movimientos_raw = [movimientos_raw]
		if not isinstance(movimientos_raw, list):
			raise ValueError("movimientosList debe ser una lista")
		movimientos = [MovimientosCreate.model_validate(item).model_dump(exclude_none=True) for item in movimientos_raw]
	except Exception as err:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message=str(err))

	lista_objetos_creados = []
	lista_errores = []

	for item in movimientos:
		dispositivo = DispositivosModel.get_one_device(db, item.get("dispositivoId"))
		if not dispositivo:
			lista_errores.append(partial_response("TPM-5", "el dispositivo no existe", item.get("dispositivoId"), item.get("id", 0)))
			continue

		lugar = LugaresModel.get_one_lugar(db, item.get("LugarId"))
		if not lugar:
			lista_errores.append(partial_response("TPM-4", "el lugar no existe", item.get("LugarId"), item.get("id", 0)))
			continue

		if not _usuario_exists(db, int(item.get("usuarioId"))):
			lista_errores.append(partial_response("TPM-5", "el usuario no existe", item.get("usuarioId"), item.get("id", 0)))
			continue

		if not _tipo_mov_exists(db, int(item.get("tipoMovId"))):
			lista_errores.append(partial_response("TPM-5", "el tipo de movimiento no existe", item.get("tipoMovId"), item.get("id", 0)))
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
			lista_errores.append(partial_response("TPM-17", "", item.get("dispositivoId"), item.get("id", 0)))
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
			lista_errores.append(partial_response("TPM-7", "", str(err), item.get("id", 0)))

	if len(lista_objetos_creados) > 0:
		if len(lista_errores) == 0:
			return fastapi_response(lista_objetos_creados, status.HTTP_201_CREATED, "TPM-8")
		return fastapi_response(lista_objetos_creados, status.HTTP_201_CREATED, "TPM-16", items=lista_errores)

	return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-16", items=lista_errores)


@router.put("", summary="Actualizar movimiento")
async def movimientos_update(payload: dict, db: Session = Depends(get_db)) -> dict:
	if not payload:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")
	if payload.get("id") is None:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")

	try:
		movimiento_id = payload.get("id")
		existe_mov = db.execute(text("SELECT id FROM invMovimientos WHERE id = :id"), {"id": movimiento_id}).scalar_one_or_none()
		if not existe_mov:
			return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

		dispositivo_id = payload.get("dispositivoId")
		if dispositivo_id:
			existe_dispositivo = db.execute(text("SELECT id FROM invDispositivos WHERE id = :id"), {"id": dispositivo_id}).scalar_one_or_none()
			if not existe_dispositivo:
				return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(dispositivo_id))])

		lugar_id = payload.get("LugarId")
		if lugar_id:
			existe_lugar = db.execute(text("SELECT id FROM invLugares WHERE id = :id"), {"id": lugar_id}).scalar_one_or_none()
			if not existe_lugar:
				return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(lugar_id))])

		tipo_mov_id = payload.get("tipoMovId")
		if tipo_mov_id:
			existe_tipo = db.execute(text("SELECT id FROM invTipoMoves WHERE id = :id"), {"id": tipo_mov_id}).scalar_one_or_none()
			if not existe_tipo:
				return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(tipo_mov_id))])

		usuario_id = payload.get("usuarioId")
		if usuario_id:
			existe_usuario = db.execute(text("SELECT id FROM invUsuarios WHERE id = :id"), {"id": usuario_id}).scalar_one_or_none()
			if not existe_usuario:
				return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(usuario_id))])

		now = datetime.utcnow()
		update_query = text(
			"""
			UPDATE invMovimientos
			SET dispositivoId = COALESCE(:dispositivoId, dispositivoId),
				LugarId = COALESCE(:LugarId, LugarId),
				tipoMovId = COALESCE(:tipoMovId, tipoMovId),
				cantidad_Actual = COALESCE(:cantidad_Actual, cantidad_Actual),
				usuarioId = COALESCE(:usuarioId, usuarioId),
				comentarios = COALESCE(:comentarios, comentarios),
				fechaUltimaModificacion = :fechaUltimaModificacion
			WHERE id = :id
			"""
		)
		db.execute(update_query, {
			"id": movimiento_id,
			"dispositivoId": dispositivo_id,
			"LugarId": lugar_id,
			"tipoMovId": tipo_mov_id,
			"cantidad_Actual": payload.get("cantidad_Actual"),
			"usuarioId": usuario_id,
			"comentarios": payload.get("comentarios"),
			"fechaUltimaModificacion": now
		})
		db.commit()

		movimiento_completo = _build_movimiento_response(db, movimiento_id)
		return fastapi_response(movimiento_completo, status.HTTP_200_OK, "TPM-6")
	except Exception as err:
		db.rollback()
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))

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
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")

	movimiento = _build_movimiento_response(db, last_mov_id)
	if not movimiento:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return fastapi_response(movimiento, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar movimientos")
async def movimientos_query(
	payload: dict,
	offset: int = 0,
	limit: int = 100,
	db: Session = Depends(get_db),
) -> dict:
	if payload is None:
		return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

	base_query = """
		SELECT
			m.id AS movimiento_id,
			m.idMovimiento AS movimiento_idMovimiento,
			m.dispositivoId AS movimiento_dispositivoId,
			m.usuarioId AS movimiento_usuarioId,
			m.tipoMovId AS movimiento_tipoMovId,
			m.LugarId AS movimiento_LugarId,
			m.comentarios AS movimiento_comentarios,
			m.foto AS movimiento_foto,
			m.foto2 AS movimiento_foto2,
			m.fechaAlta AS movimiento_fechaAlta,
			m.fechaUltimaModificacion AS movimiento_fechaUltimaModificacion,
			m.cantidad_Actual AS movimiento_cantidad_Actual,
			d.id AS dispositivo_id,
			d.codigo AS dispositivo_codigo,
			d.producto AS dispositivo_producto,
			d.marca AS dispositivo_marca,
			d.modelo AS dispositivo_modelo,
			d.origen AS dispositivo_origen,
			d.foto AS dispositivo_foto,
			d.cantidad AS dispositivo_cantidad,
			d.observaciones AS dispositivo_observaciones,
			d.lugarId AS dispositivo_lugarId,
			d.pertenece AS dispositivo_pertenece,
			d.descompostura AS dispositivo_descompostura,
			d.costo AS dispositivo_costo,
			d.compra AS dispositivo_compra,
			d.proveedor AS dispositivo_proveedor,
			d.idMov AS dispositivo_idMov,
			d.statusId AS dispositivo_statusId,
			d.serie AS dispositivo_serie,
			d.accesorios AS dispositivo_accesorios,
			ld.id AS dispositivo_lugar_id,
			ld.lugar AS dispositivo_lugar_lugar,
			ld.activo AS dispositivo_lugar_activo,
			ld.fechaAlta AS dispositivo_lugar_fechaAlta,
			ld.fechaUltimaModificacion AS dispositivo_lugar_fechaUltimaModificacion,
			sd.id AS dispositivo_status_id,
			sd.descripcion AS dispositivo_status_descripcion,
			sd.fechaAlta AS dispositivo_status_fechaAlta,
			sd.fechaUltimaModificacion AS dispositivo_status_fechaUltimaModificacion,
			l.id AS lugar_id,
			l.lugar AS lugar_lugar,
			l.activo AS lugar_activo,
			l.fechaAlta AS lugar_fechaAlta,
			l.fechaUltimaModificacion AS lugar_fechaUltimaModificacion,
			tm.id AS tipoMovimiento_id,
			tm.tipo AS tipoMovimiento_tipo,
			tm.fechaAlta AS tipoMovimiento_fechaAlta,
			tm.fechaUltimaModificacion AS tipoMovimiento_fechaUltimaModificacion,
			u.id AS usuario_id,
			u.nombre AS usuario_nombre,
			u.username AS usuario_username,
			u.apellidoPaterno AS usuario_apellidoPaterno,
			u.apellidoMaterno AS usuario_apellidoMaterno,
			u.password AS usuario_password,
			u.telefono AS usuario_telefono,
			u.correo AS usuario_correo,
			u.foto AS usuario_foto,
			u.rolId AS usuario_rolId,
			u.statusId AS usuario_statusId,
			u.fechaAlta AS usuario_fechaAlta,
			u.fechaUltimaModificacion AS usuario_fechaUltimaModificacion
		FROM invMovimientos m
		INNER JOIN invDispositivos d ON d.id = m.dispositivoId
		LEFT JOIN invLugares ld ON ld.id = d.lugarId
		LEFT JOIN invStatusDevices sd ON sd.id = d.statusId
		LEFT JOIN invLugares l ON l.id = m.LugarId
		LEFT JOIN invTipoMoves tm ON tm.id = m.tipoMovId
		LEFT JOIN invUsuarios u ON u.id = m.usuarioId
		WHERE 1=1
	"""
	count_query = """
		SELECT COUNT(1) AS total_rows
		FROM invMovimientos m
		INNER JOIN invDispositivos d ON d.id = m.dispositivoId
		LEFT JOIN invLugares ld ON ld.id = d.lugarId
		LEFT JOIN invStatusDevices sd ON sd.id = d.statusId
		LEFT JOIN invLugares l ON l.id = m.LugarId
		LEFT JOIN invTipoMoves tm ON tm.id = m.tipoMovId
		LEFT JOIN invUsuarios u ON u.id = m.usuarioId
		WHERE 1=1
	"""
	where_clause = ""
	params = {}
	filters_applied = 0

	if "id" in payload and payload.get("id") is not None:
		where_clause += " AND m.id = :id"
		params["id"] = payload.get("id")
		filters_applied += 1

	if "dispositivoId" in payload and payload.get("dispositivoId") is not None:
		where_clause += " AND m.dispositivoId = :dispositivoId"
		params["dispositivoId"] = payload.get("dispositivoId")
		filters_applied += 1

	if "LugarId" in payload and payload.get("LugarId") is not None:
		where_clause += " AND m.LugarId = :LugarId"
		params["LugarId"] = payload.get("LugarId")
		filters_applied += 1

	if "tipoMovId" in payload and payload.get("tipoMovId") is not None:
		where_clause += " AND m.tipoMovId = :tipoMovId"
		params["tipoMovId"] = payload.get("tipoMovId")
		filters_applied += 1

	if "usuarioId" in payload and payload.get("usuarioId") is not None:
		where_clause += " AND m.usuarioId = :usuarioId"
		params["usuarioId"] = payload.get("usuarioId")
		filters_applied += 1

	if "idMovimiento" in payload and payload.get("idMovimiento"):
		where_clause += " AND m.idMovimiento LIKE :idMovimiento"
		params["idMovimiento"] = f"%{str(payload.get('idMovimiento')).strip()}%"
		filters_applied += 1

	if "fechaAltaRangoInicio" in payload and payload.get("fechaAltaRangoInicio"):
		where_clause += " AND CAST(m.fechaAlta AS DATE) >= :fechaAltaRangoInicio"
		params["fechaAltaRangoInicio"] = payload.get("fechaAltaRangoInicio")
		filters_applied += 1

	if "fechaAltaRangoFin" in payload and payload.get("fechaAltaRangoFin"):
		where_clause += " AND CAST(m.fechaAlta AS DATE) <= :fechaAltaRangoFin"
		params["fechaAltaRangoFin"] = payload.get("fechaAltaRangoFin")
		filters_applied += 1

	# Keep query endpoint bounded: when no valid movement filters are provided,
	# return an empty successful response instead of scanning all movements.
	if filters_applied == 0:
		return fastapi_response([], status.HTTP_200_OK, "TPM-3")

	data_query = base_query + where_clause + " ORDER BY m.fechaAlta DESC OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY"
	count_sql = count_query + where_clause
	params["offset"] = int(offset)
	params["limit"] = int(limit)

	try:
		total_rows = int(db.execute(text(count_sql), params).scalar() or 0)
		rows = db.execute(text(data_query), params).mappings().all()
		if not rows:
			return fastapi_response([], status.HTTP_200_OK, "TPM-3")

		movimientos = [_build_movimiento_from_joined_row(dict(row)) for row in rows]

		return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)
	except Exception as err:
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/filter", summary="Filtrar movimientos")
async def movimientos_filter(
	offset: int = 0,
	limit: int = 100,
	value: str = "",
	header_value: str | None = Header(default=None, alias="value"),
	db: Session = Depends(get_db),
) -> dict:
	search_value = (header_value or value or "").strip()

	try:
		movimientos, total_rows = _fetch_movimientos_some_fields(db, offset, limit, search_value)
		if not movimientos:
			return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
		return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3", isQuery=True, total=total_rows)
	except Exception as err:
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/filtermovementFields", summary="Filtrar movimientos campos minimos")
async def movimientos_filter_fields(
	offset: int = 0,
	limit: int = 100,
	value: str = "",
	header_value: str | None = Header(default=None, alias="value"),
	db: Session = Depends(get_db),
) -> dict:
	search_value = (header_value or value or "").strip()

	try:
		movimientos, _ = _fetch_movimientos_some_fields(db, offset, limit, search_value)
		return fastapi_response(movimientos, status.HTTP_200_OK, "TPM-3")
	except Exception as err:
		return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.get("/{id}", summary="Obtener movimiento por ID")
async def movimientos_get_one(id: int, db: Session = Depends(get_db)) -> dict:
	movimiento = _build_movimiento_response(db, id)
	if not movimiento:
		return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
	return fastapi_response(movimiento, status.HTTP_200_OK, "TPM-3")
