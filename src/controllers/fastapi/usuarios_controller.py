from datetime import date, datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from ...database import get_db
from ...models.RolesModelSchema import RolesModel
from ...models.EstatusUsuariosModelSchema import EstatusUsuariosModel
from ...models.UsuariosModelSchema import UsuariosLoginSchema, UsuariosModel
from ...shared.returnCodes import fastapi_response, partial_response

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])
def _get_usuario_full(db: Session, usuario_id: int) -> dict | None:
    return UsuariosModel.fetch_by_id(db, usuario_id)


@router.post("/login", summary="Login usuario")
async def users_login(payload: UsuariosLoginSchema, db: Session = Depends(get_db)) -> dict:
    if not payload:
        return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

    try:
        username = payload.username
        password = payload.password
        if not username or not password:
            return fastapi_response(None, status.HTTP_400_BAD_REQUEST, "TPM-2")

        user = UsuariosModel.get_credentials_row(db, username)
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
    usuarios = UsuariosModel.list_active(db)
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

        existe_user = UsuariosModel.exists_username(db, user_data["username"])
        if existe_user:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-5", items=[partial_response("TPM-5", name=user_data["username"])])

        existe_rol = RolesModel.get_one_rol(db, int(user_data["rolId"]))
        if not existe_rol:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(user_data["rolId"]))])

        existe_status = EstatusUsuariosModel.get_one_status(db, int(user_data["statusId"]))
        if not existe_status:
            return fastapi_response(None, status.HTTP_409_CONFLICT, "TPM-4", items=[partial_response("TPM-4", name=str(user_data["statusId"]))])

        user_data["fechaAlta"] = datetime.utcnow()
        user_data["fechaUltimaModificacion"] = datetime.utcnow()
        created = UsuariosModel.create_user(db, user_data)
        usuario_id = int(created.id)

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
