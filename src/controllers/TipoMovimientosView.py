from telnetlib import NAMS
from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError



from ..shared import returnCodes
from flask_restx import Api,fields,Resource
from ..models.TipoMovimientosModel import TipoMoveModel,TipoMoveSchema,TipoMoveSchemaUpdate
from ..models import db

app = Flask(__name__)
tipomoves_api = Blueprint("tipomoves_api", __name__)
lugares_schema = TipoMoveSchema()
lugares_schema_update = TipoMoveSchemaUpdate()
api = Api(tipomoves_api)

nstipomoves = api.namespace("tipomovimientos", description="API operations for tipos de movimientos")

tiposModelApi = nstipomoves.model(
    "tipos",
    {
        "tipo": fields.String(required=True, description="tipo"),
   
    }
)

tiposModelListApi = nstipomoves.model('tiposList', {
    'tipos': fields.List(fields.Nested(tiposModelApi)),
})

LugaresPatchApi = nstipomoves.model(
    "LugarPatchModel",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "tipo": fields.String(description="tipo")
  
        
    }
)

def createTipo(req_data, listaObjetosCreados, listaErrores):
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
    lugar_in_db = TipoMoveModel.get_tipo_by_nombre(data.get("lugar"))
    if lugar_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("lugar"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("lugar"))

    lugar = TipoMoveModel(data)

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

@nstipomoves.route("")
class TiposList(Resource):
    @nstipomoves.doc("lista de tipos")
    def get(self):
        """List all lugares"""
        print('getting')
        lugares = TipoMoveModel.get_all_tipos()
        #return catalogos
        serialized_lugares = lugares_schema.dump(lugares, many=True)
        return returnCodes.custom_response(serialized_lugares, 200, "TPM-3")

    
    @nstipomoves.doc("Crear tipos")
    @nstipomoves.expect(tiposModelApi)
    @nstipomoves.response(201, "created")
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
        
      
        createTipo(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)

    
    @nstipomoves.doc("actualizar tipo movimiento")
    @nstipomoves.expect(LugaresPatchApi)
    def put(self):

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.get_json()
        data = None
        try:
            data = lugares_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        move = TipoMoveModel.get_one_tipo(data.get("id"))
        if not move:
            
            return returnCodes.custom_response(None, 404, "TPM-4")

        try:
            move.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_lugar = lugares_schema.dump(move)
        return returnCodes.custom_response(serialized_lugar, 200, "TPM-6")

@nstipomoves.route("/<int:id>")
@nstipomoves.param("id", "The id identifier")
@nstipomoves.response(404, "tipo movimiento no encontrado")
class OneLugar(Resource):
    @nstipomoves.doc("obtener un tipo movimiento")
    def get(self, id):
       
        move = TipoMoveModel.get_one_tipo(id)
        if not move:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_lugar = lugares_schema.dump(move)
        return returnCodes.custom_response(serialized_lugar, 200, "TPM-3")