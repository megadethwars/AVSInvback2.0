# /src/views/GiroView

from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from ..models.UsuariosModel import UsuariosModel, UsuariosSchema,UsuariosSchemaUpdate,UsuarioLoginSchema,UsuarioLoginUpdateSchema, UsuariosSchemaQuery
from ..models.RolesModel import RolesModel
from ..models.EstatusUsuariosModel import EstatusUsuariosModel
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
Usuario_api = Blueprint("users_api", __name__)
usuarios_schema = UsuariosSchema()
usuarios_schema_update = UsuariosSchemaUpdate()
user_auth = UsuarioLoginSchema()
user_pass_update = UsuarioLoginUpdateSchema()
usuarios_schema_query = UsuariosSchemaQuery()
api = Api(Usuario_api)

nsUsuarios = api.namespace("users", description="API operations for usuarios")

UsersModelApi = nsUsuarios.model(
    "usuarios",
    {
     
        "nombre": fields.String(required=True, description="nombre"),
        "username":fields.String(required=True, description="username"),
        "apellidoPaterno":fields.String(required=True, description="apellidoPaterno"),
        "apellidoMaterno":fields.String(required=True, description="apellidoMaterno"),
        "password":fields.String(required=True, description="password"),
        "telefono":fields.String(required=True, description="telefono"),
        "correo":fields.String(required=True, description="correo"),
        "foto":fields.String( description="foto"),
        "rolId":fields.Integer(required=True, description="rolId"),
        "statusId":fields.Integer(required=True, description="statusId")
    }
)

UsersModelQueryApi = nsUsuarios.model(
    "usuariosuery",
    {
     
        "id": fields.Integer( description="identificador"),
        "nombre": fields.String( description="nombre"),
        "username":fields.String( description="username"),
        "apellidoPaterno":fields.String( description="apellidoPaterno"),
        "apellidoMaterno":fields.String( description="apellidoMaterno"),
        "password":fields.String( description="password"),
        "telefono":fields.String( description="telefono"),
        "correo":fields.String( description="correo"),
        "foto":fields.String( description="foto"),
        "rolId":fields.Integer(description="rolId"),
        "statusId":fields.Integer( description="statusId")
    }
)

UsersModelLoginApi = nsUsuarios.model(
    "usuariosLogin",
    {
     
       
        "username":fields.String(required=True, description="username"),
        "password":fields.String(required=True, description="password"),
        
    }
)

UsersModelLoginpassUpdateApi = nsUsuarios.model(
    "usuariosUpdatePass",
    {
     
       "id": fields.Integer(required=True, description="identificador"),
        "username":fields.String(required=True, description="username"),
        "password":fields.String(required=True, description="password")
        
    }
)

UsersModelListApi = nsUsuarios.model('usersList', {
    'userslist': fields.List(fields.Nested(UsersModelApi)),
})

UsersPutApi = nsUsuarios.model(
    "usersPut",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "nombre": fields.String(required=True, description="nombre"),
        "username":fields.String(required=True, description="username"),
        "apellidoPaterno":fields.String(required=True, description="apellidoPaterno"),
        "apellidoMaterno":fields.String(required=True, description="apellidoMaterno"),
        "password":fields.String(required=True, description="password"),
        "telefono":fields.String(required=True, description="telefono"),
        "correo":fields.String(required=True, description="correo"),
        "foto":fields.String( description="foto"),
        "rolId":fields.Integer(required=True, description="rolId"),
        "statusId":fields.Integer(required=True, description="statusId")
        
    }
)

def createUsers(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = usuarios_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    user_in_db = UsuariosModel.get_users_by_username(data.get("username"))
    if user_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("username"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("username"))

    rol_in_db = RolesModel.get_one_rol(data.get("rolId"))
    if not rol_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("rolId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("rolId"))

    status_in_db = EstatusUsuariosModel.get_one_status(data.get("statusId"))
    if not status_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("statusId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("statusId"))

    data['password'] = generate_password_hash(data['password'])

    user = UsuariosModel(data)

    try:
        user.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_user = usuarios_schema.dump(user)
    listaObjetosCreados.append(serialized_user)
    return returnCodes.custom_response(serialized_user, 201, "TPM-1")



@nsUsuarios.route("/login")
class UsersLogin(Resource):
    @nsUsuarios.doc("login usuario")
    @nsUsuarios.expect(UsersModelLoginApi)
    @nsUsuarios.response(201, "auth")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = user_auth.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        user = UsuariosModel.get_users_by_username(data.get("username"))
        if not user:
            
            return returnCodes.custom_response(None, 404, "TPM-4","Usuario no encontrado")

        if user.statusId==3:
            return returnCodes.custom_response(None, 409, "TPM-19","Usuario dado de baja")


        if check_password_hash(user.password,data['password'])==False:
            return returnCodes.custom_response(None, 401, "TPM-10","acceso no autorizado, usuario y/o contraseña incorrecto")
        serialized_user = usuarios_schema.dump(user)
        return returnCodes.custom_response(serialized_user, 201, "TPM-18")


@nsUsuarios.route("/pass")
class Usersupdatepass(Resource):
    @nsUsuarios.doc("cambiar password")
    @nsUsuarios.expect(UsersModelLoginpassUpdateApi)
    @nsUsuarios.response(200, "success")
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = user_pass_update.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        user = UsuariosModel.get_one_users(data.get("id"))
        if not user:
            
            return returnCodes.custom_response(None, 404, "TPM-4","Usuario no encontrado")

        data['password'] = generate_password_hash(data['password'])

        try:
            user.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        
        serialized_user = usuarios_schema.dump(user)
        return returnCodes.custom_response(serialized_user, 201, "TPM-6")


@nsUsuarios.route("")
class UsersList(Resource):
    @nsUsuarios.doc("lista de  usuarios")
    def get(self):
        """List all status"""
        print('getting')
        users = UsuariosModel.get_all_users_ok()
        #return catalogos
        serialized_users = usuarios_schema.dump(users, many=True)
        return returnCodes.custom_response(serialized_users, 200, "TPM-3")

    @nsUsuarios.doc("Crear usuario")
    @nsUsuarios.expect(UsersModelApi)
    @nsUsuarios.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = usuarios_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
       
        createUsers(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsUsuarios.doc("actualizar usuario")
    @nsUsuarios.expect(UsersPutApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = usuarios_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        user = UsuariosModel.get_one_users(data.get("id"))
        if not user:
            
            return returnCodes.custom_response(None, 404, "TPM-4")
        if "rolId" in data:
            rol_in_db = RolesModel.get_one_rol(data.get("rolId"))
            if not rol_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("rolId"))

        if "statusId" in data:
            status_in_db = EstatusUsuariosModel.get_one_status(data.get("statusId"))
            if not status_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("statusId"))

        try:
            user.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_status = usuarios_schema.dump(user)
        return returnCodes.custom_response(serialized_status, 200, "TPM-6")

@nsUsuarios.route("/<int:id>")
@nsUsuarios.param("id", "The id identifier")
@nsUsuarios.response(404, "usuario no encontrado")
class OneCatalogo(Resource):
    @nsUsuarios.doc("obtener un usuario")
    def get(self, id):
       
        rol = UsuariosModel.get_one_users(id)
        if not rol:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_user = usuarios_schema.dump(rol)
        return returnCodes.custom_response(serialized_user, 200, "TPM-3")

@nsUsuarios.route("/query")

@nsUsuarios.response(404, "usuario no encontrado")
class UserQuery(Resource):
    
    @nsUsuarios.doc("obtener varios usuarios")
    @api.expect(UsersModelQueryApi)
    def post(self):
        print(request.args)
        offset = 1
        limit = 100

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)

        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = usuarios_schema_query.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        devices = UsuariosModel.get_users_by_query(data,offset,limit)
        if not devices:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = usuarios_schema.dump(devices.items,many=True)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")