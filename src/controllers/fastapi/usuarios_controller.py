from datetime import date, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import MetaData, Table, cast, insert, select
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from ...database import engine, get_db
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


_metadata = MetaData()
_usuarios = Table("invUsuarios", _metadata, autoload_with=engine)
_roles = Table("invRoles", _metadata, autoload_with=engine)
_status_usuarios = Table("invStatusUsuarios", _metadata, autoload_with=engine)


def _json_safe_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    return value


def _base_usuario_join_stmt():
    return (
        select(
            _usuarios.c.id.label("usuario_id"),
            _usuarios.c.nombre.label("usuario_nombre"),
            _usuarios.c.username.label("usuario_username"),
            _usuarios.c.apellidoPaterno.label("usuario_apellidoPaterno"),
            _usuarios.c.apellidoMaterno.label("usuario_apellidoMaterno"),
            _usuarios.c.password.label("usuario_password"),
            _usuarios.c.telefono.label("usuario_telefono"),
            _usuarios.c.correo.label("usuario_correo"),
            _usuarios.c.foto.label("usuario_foto"),
            _usuarios.c.rolId.label("usuario_rolId"),
            _usuarios.c.statusId.label("usuario_statusId"),
            _usuarios.c.fechaAlta.label("usuario_fechaAlta"),
            _usuarios.c.fechaUltimaModificacion.label("usuario_fechaUltimaModificacion"),
            _roles.c.id.label("rol_id"),
            _roles.c.nombre.label("rol_nombre"),
            _roles.c.fechaAlta.label("rol_fechaAlta"),
            _roles.c.fechaUltimaModificacion.label("rol_fechaUltimaModificacion"),
            _status_usuarios.c.id.label("status_id"),
            _status_usuarios.c.descripcion.label("status_descripcion"),
            _status_usuarios.c.fechaAlta.label("status_fechaAlta"),
            _status_usuarios.c.fechaUltimaModificacion.label("status_fechaUltimaModificacion"),
        )
        .select_from(
            _usuarios.outerjoin(_roles, _roles.c.id == _usuarios.c.rolId).outerjoin(_status_usuarios, _status_usuarios.c.id == _usuarios.c.statusId)
        )
    )


def _build_usuario_from_row(row: dict) -> dict:
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

    rol = {
        "id": row.get("rol_id"),
        "nombre": row.get("rol_nombre"),
        "fechaAlta": row.get("rol_fechaAlta"),
        "fechaUltimaModificacion": row.get("rol_fechaUltimaModificacion"),
    }
    status_usuario = {
        "id": row.get("status_id"),
        "descripcion": row.get("status_descripcion"),
        "fechaAlta": row.get("status_fechaAlta"),
        "fechaUltimaModificacion": row.get("status_fechaUltimaModificacion"),
    }

    usuario["rol"] = rol if any(v is not None for v in rol.values()) else None
    usuario["status"] = status_usuario if any(v is not None for v in status_usuario.values()) else None
    return _json_safe_value(usuario)


def _get_usuario_full(db: Session, usuario_id: int) -> dict | None:
    stmt = _base_usuario_join_stmt().where(_usuarios.c.id == usuario_id).limit(1)
    row = db.execute(stmt).mappings().first()
    if not row:
        return None
    return _build_usuario_from_row(dict(row))


@router.post("/login", summary="Login usuario")
async def users_login(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    try:
        username = payload.get("username")
        password = payload.get("password")
        if not username or not password:
            return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

        stmt = select(_usuarios.c.id, _usuarios.c.password, _usuarios.c.statusId).where(_usuarios.c.username == username).limit(1)
        user = db.execute(stmt).mappings().first()
        if not user:
            return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4", message="Usuario no encontrado")

        if int(user.get("statusId") or 0) == 3:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-19", message="Usuario dado de baja")

        if not check_password_hash(str(user.get("password") or ""), password):
            return fastapi_response(None, status.HTTP_401_UNAUTHORIZED, "TPM-10", message="acceso no autorizado, usuario y/o contraseña incorrecto")

        serialized_user = _get_usuario_full(db, int(user.get("id")))
        return fastapi_response(serialized_user, status.HTTP_201_CREATED, "TPM-18")
    except Exception as err:
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("/pass", summary="Cambiar password")
async def users_update_password(payload: dict) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="usuarios.pass pendiente de migracion")


@router.get("", summary="Listar usuarios")
async def users_list(db: Session = Depends(get_db)) -> dict:
    stmt = _base_usuario_join_stmt().where(_usuarios.c.statusId != 3).order_by(_usuarios.c.id)
    rows = db.execute(stmt).mappings().all()
    usuarios = [_build_usuario_from_row(dict(row)) for row in rows]
    return fastapi_response(usuarios, status.HTTP_200_OK, "TPM-3")


@router.post("", summary="Crear usuario")
async def users_create(payload: dict, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    try:
        user_data = {
            "nombre": payload.get("nombre"),
            "username": payload.get("username"),
            "apellidoPaterno": payload.get("apellidoPaterno"),
            "apellidoMaterno": payload.get("apellidoMaterno"),
            "password": generate_password_hash(payload.get("password", "")),
            "telefono": payload.get("telefono"),
            "correo": payload.get("correo"),
            "foto": payload.get("foto"),
            "rolId": payload.get("rolId"),
            "statusId": payload.get("statusId"),
        }

        existe_user = db.execute(select(_usuarios.c.id).where(_usuarios.c.username == user_data["username"]).limit(1)).scalar_one_or_none()
        if existe_user:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[partial_response("TPM-5", name=user_data["username"])])

        existe_rol = db.execute(select(_roles.c.id).where(_roles.c.id == user_data["rolId"]).limit(1)).scalar_one_or_none()
        if not existe_rol:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(user_data["rolId"]))])

        existe_status = db.execute(select(_status_usuarios.c.id).where(_status_usuarios.c.id == user_data["statusId"]).limit(1)).scalar_one_or_none()
        if not existe_status:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(user_data["statusId"]))])

        now = datetime.utcnow()
        stmt = (
            insert(_usuarios)
            .values(
                nombre=user_data["nombre"],
                username=user_data["username"],
                apellidoPaterno=user_data["apellidoPaterno"],
                apellidoMaterno=user_data["apellidoMaterno"],
                password=user_data["password"],
                telefono=user_data["telefono"],
                correo=user_data["correo"],
                foto=user_data["foto"],
                rolId=user_data["rolId"],
                statusId=user_data["statusId"],
                fechaAlta=now,
                fechaUltimaModificacion=now,
            )
            .returning(_usuarios.c.id)
        )
        usuario_id = int(db.execute(stmt).scalar_one())
        db.commit()

        usuario_completo = _get_usuario_full(db, usuario_id)
        return fastapi_response(usuario_completo, status.HTTP_201_CREATED, "TPM-1")
    except Exception as err:
        db.rollback()
        return fastapi_response(None, status.HTTP_500_INTERNAL_SERVER_ERROR, "TPM-7", message=str(err))


@router.put("", summary="Actualizar usuario")
async def users_update(payload: dict) -> dict:
    if not payload or payload.get("id") is None:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2", message="id es requerido")
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="usuarios.update pendiente de migracion")


@router.get("/{id}", summary="Obtener usuario por ID")
async def users_get_one(id: int, db: Session = Depends(get_db)) -> dict:
    usuario = _get_usuario_full(db, id)
    if not usuario:
        return fastapi_response(None, status.HTTP_404_NOT_FOUND, "TPM-4")
    return fastapi_response(usuario, status.HTTP_200_OK, "TPM-3")


@router.post("/query", summary="Consultar usuarios")
async def users_query() -> dict:
    return fastapi_response(None, status.HTTP_501_NOT_IMPLEMENTED, "TPM-7", message="usuarios.query pendiente de migracion")
