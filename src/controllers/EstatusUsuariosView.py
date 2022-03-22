# /src/views/GiroView

from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from ..models.EstatusUsuariosModel import EstatusUsuariosModel, EstatusUsuariosSchema,EstatusUsuariosSchemaUpdate
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource

app = Flask(__name__)
statusUsuario_api = Blueprint("statususers_api", __name__)
estatus_schema = EstatusUsuariosSchema()
estatus_schema_update = EstatusUsuariosSchemaUpdate()
api = Api(statusUsuario_api)

nsStatusUsuarios = api.namespace("statususers", description="API operations for Status usuarios")

StatusModelApi = nsStatusUsuarios.model(
    "status",
    {
        "descripcion": fields.String(required=True, description="tipo")
    }
)

StatusModelListApi = nsStatusUsuarios.model('statususersList', {
    'statuslist': fields.List(fields.Nested(StatusModelApi)),
})

StatusPatchApi = nsStatusUsuarios.model(
    "status",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "descripcion": fields.String(required=True, description="tipo"),
        
    }
)

def createStatus(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = estatus_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    rol_in_db = EstatusUsuariosModel.get_status_by_tipo(data.get("descripcion"))
    if rol_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("descripcion"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre"))

    rol = EstatusUsuariosModel(data)

    try:
        rol.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_status = estatus_schema.dump(rol)
    listaObjetosCreados.append(serialized_status)
    return returnCodes.custom_response(serialized_status, 201, "TPM-1")

@nsStatusUsuarios.route("")
class RolesList(Resource):
    @nsStatusUsuarios.doc("lista de status usuarios")
    def get(self):
        """List all status"""
        print('getting')
        roles = EstatusUsuariosModel.get_all_status()
        #return catalogos
        serialized_status = estatus_schema.dump(roles, many=True)
        return returnCodes.custom_response(serialized_status, 200, "TPM-3")

    @nsStatusUsuarios.doc("Crear status")
    @nsStatusUsuarios.expect(StatusModelApi)
    @nsStatusUsuarios.response(201, "created")
    def post(self):
        
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = estatus_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
        
        createStatus(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsStatusUsuarios.doc("actualizar estatus")
    @nsStatusUsuarios.expect(StatusPatchApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.get_json()
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = estatus_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        rol = EstatusUsuariosModel.get_one_status(data.get("id"))
        if not rol:
            
            return returnCodes.custom_response(None, 404, "TPM-4")

        try:
            rol.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_status = estatus_schema.dump(rol)
        return returnCodes.custom_response(serialized_status, 200, "TPM-6")

@nsStatusUsuarios.route("/<int:id>")
@nsStatusUsuarios.param("id", "The id identifier")
@nsStatusUsuarios.response(404, "estatus no encontrado")
class OneCatalogo(Resource):
    @nsStatusUsuarios.doc("obtener un status")
    def get(self, id):
       
        rol = EstatusUsuariosModel.get_one_status(id)
        if not rol:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_status = estatus_schema.dump(rol)
        return returnCodes.custom_response(serialized_status, 200, "TPM-3")