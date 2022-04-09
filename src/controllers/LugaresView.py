from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError

from ..shared import returnCodes
from flask_restx import Api,fields,Resource
from ..models.LugaresModel import LugaresSchema,LugaresSchemaUpdate,LugaresModel
from ..models import db
app = Flask(__name__)
lugares_api = Blueprint("lugares_api", __name__)
lugares_schema = LugaresSchema()
lugares_schema_update = LugaresSchemaUpdate()
api = Api(lugares_api)

nsLugares = api.namespace("lugares", description="API operations for lugares")

LugaresModelApi = nsLugares.model(
    "LugaresModel",
    {
        "lugar": fields.String(required=True, description="lugar"),
        "activo": fields.Boolean(required=True, description="activo")
    }
)

LugaresModelListApi = nsLugares.model('lugaresList', {
    'lugares': fields.List(fields.Nested(LugaresModelApi)),
})

LugaresPutApi = nsLugares.model(
    "LugarputModel",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "lugar": fields.String(required=True, description="lugar"),
        "activo": fields.Boolean(description="activo")
        
    }
)

def createLugar(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = lugares_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    lugar_in_db = LugaresModel.get_lugar_by_nombre(data.get("lugar"))
    if lugar_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("lugar"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("lugar"))

    lugar = LugaresModel(data)

    try:
        lugar.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_lugar = lugares_schema.dump(lugar)
    listaObjetosCreados.append(serialized_lugar)
    return returnCodes.custom_response(serialized_lugar, 201, "TPM-1")

@nsLugares.route("")
class LugaresList(Resource):
    @nsLugares.doc("lista de lugares")
    def get(self):
        try:

            """List all lugares"""
            print('getting lugares')
            lugares = LugaresModel.get_all_lugares()
            #return catalogos
            serialized_lugares = lugares_schema.dump(lugares, many=True)
            return returnCodes.custom_response(serialized_lugares, 200, "TPM-3")
        except Exception as ex:
            print('ocurrio un error en lugares '+str(ex))
            return returnCodes.custom_response(None, 500, "TPM-7",str(ex))


    
    @nsLugares.doc("Crear lugares")
    @nsLugares.expect(LugaresModelApi)
    @nsLugares.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = lugares_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
      
        createLugar(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)

    
    @nsLugares.doc("actualizar lugar")
    @nsLugares.expect(LugaresPutApi)
    def put(self):

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.get_json()
        data = None
        try:
            data = lugares_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        lugar = LugaresModel.get_one_lugar(data.get("id"))
        if not lugar:
            
            return returnCodes.custom_response(None, 404, "TPM-4")

        try:
            lugar.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_lugar = lugares_schema.dump(lugar)
        return returnCodes.custom_response(serialized_lugar, 200, "TPM-6")

@nsLugares.route("/<int:id>")
@nsLugares.param("id", "The id identifier")
@nsLugares.response(404, "lugar no encontrado")
class OneLugar(Resource):
    @nsLugares.doc("obtener un lugar")
    def get(self, id):
       
        lugar = LugaresModel.get_one_lugar(id)
        if not lugar:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_lugar = lugares_schema.dump(lugar)
        return returnCodes.custom_response(serialized_lugar, 200, "TPM-3")