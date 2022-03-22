# /src/views/GiroView

from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from ..models.RolesModel import RolesModel, RolesSchema
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource

app = Flask(__name__)
roles_api = Blueprint("roles_api", __name__)
roles_schema = RolesSchema()
api = Api(roles_api)

nsRoles = api.namespace("roles", description="API operations for roles")

RolesModelApi = nsRoles.model(
    "RolesModel",
    {
        "nombre": fields.String(required=True, description="nombre")
    }
)

RolesModelListApi = nsRoles.model('rolesList', {
    'roles': fields.List(fields.Nested(RolesModelApi)),
})

RolesPatchApi = nsRoles.model(
    "CatalogoPatchModel",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "nombre": fields.String(required=True, description="nombre"),
        
    }
)

def createRol(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = roles_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    rol_in_db = RolesModel.get_rol_by_nombre(data.get("nombre"))
    if rol_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("nombre"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre"))

    rol = RolesModel(data)

    try:
        rol.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_catalogo = roles_schema.dump(rol)
    listaObjetosCreados.append(serialized_catalogo)
    return returnCodes.custom_response(serialized_catalogo, 201, "TPM-1")

@nsRoles.route("")
class RolesList(Resource):
    @nsRoles.doc("lista de catalogos")
    def get(self):
        """List all catalogos"""
        print('getting')
        roles = RolesModel.get_all_roles()
        #return catalogos
        serialized_roles = roles_schema.dump(roles, many=True)
        return returnCodes.custom_response(serialized_roles, 200, "TPM-3")

    @nsRoles.doc("Crear catalogo")
    @nsRoles.expect(RolesModelApi)
    @nsRoles.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = roles_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
        
        createRol(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsRoles.doc("actualizar catalogo")
    @nsRoles.expect(RolesPatchApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.get_json()
        data = None
        try:
            data = roles_schema.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        rol = RolesModel.get_one_rol(data.get("id"))
        if not rol:
            
            return returnCodes.custom_response(None, 404, "TPM-4")

        try:
            rol.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_rol = roles_schema.dump(rol)
        return returnCodes.custom_response(serialized_rol, 200, "TPM-6")

@nsRoles.route("/<int:id>")
@nsRoles.param("id", "The id identifier")
@nsRoles.response(404, "rol no encontrado")
class OneCatalogo(Resource):
    @nsRoles.doc("obtener un rol")
    def get(self, id):
       
        rol = RolesModel.get_one_rol(id)
        if not rol:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_rol = roles_schema.dump(rol)
        return returnCodes.custom_response(serialized_rol, 200, "TPM-3")