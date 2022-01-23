# /src/views/GiroView

from email.policy import default
from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from sqlalchemy import true
from ..models.DispositivosModel import DispositivosModel, DispositivosSchema,DispositivosSchemaUpdate,DispositivosSchemaQuery
from ..models.LugaresModel import LugaresModel
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource,reqparse

app = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, location='args')
parser.add_argument('offset', type=int, location='args')
Device_api = Blueprint("devices_api", __name__)
dispositivos_schema = DispositivosSchema()
dispositivos_schema_update = DispositivosSchemaUpdate()
dispositivos_schema_query = DispositivosSchemaQuery()
api = Api(Device_api)

nsDevices = api.namespace("devices", description="API operations for usuarios")

DevicesQueryModel = nsDevices.model(
    "dispositivos",
    {
     
        "id": fields.Integer(description="identificador"),
        "codigo":fields.String(description="codigo"),
        "producto" : fields.String( description="producto"),
        "marca" : fields.String( description="marca"),
        "modelo" :fields.String( description="modelo"),
        "origen" : fields.String(description="origen"),
        "foto" : fields.String(description="foto"),
        "cantidad" : fields.Integer(description="cantidad"),
        "observaciones" : fields.String(description="observaciones"),
        "lugarId" : fields.Integer(description="lugarId"),
        "pertenece" : fields.String( description="pertenece"),
        "descompostura" : fields.String( description="descompostura"),
        "costo" : fields.Integer(description="costo"),
        "compra" : fields.String( description="compra"),
        "proveedor" : fields.String( description="proveedor"),
        "idMov" : fields.String( description="idMov")

    }
)

#parser.add_argument('DevicesQueryModel', type=json, location='body')

DevicesModelApi = nsDevices.model(
    "dispositivos",
    {
     
      
        "codigo":fields.String(required=True,description="codigo"),
        "producto" : fields.String(required=True, description="producto"),
        "marca" : fields.String(required=True, description="stamarcatusId"),
        "modelo" :fields.String(required=True, description="modelo"),
        "origen" : fields.String(description="origen"),
        "foto" : fields.String(description="foto"),
        "cantidad" : fields.Integer(required=True,description="cantidad"),
        "observaciones" : fields.String(description="observaciones"),
        "lugarId" : fields.Integer(required=True,description="lugarId"),
        "pertenece" : fields.String( description="pertenece"),
        "descompostura" : fields.String( description="descompostura"),
        "costo" : fields.Integer(description="observaciones"),
        "compra" : fields.String( description="compra"),
        "proveedor" : fields.String( description="proveedor"),
        "idMov" : fields.String( description="idMov")

    }
)

DevicesModelListApi = nsDevices.model('usersList', {
    'userslist': fields.List(fields.Nested(DevicesModelApi)),
})

DevicesPatchApi = nsDevices.model(
    "users",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "codigo":fields.String(description="codigo"),
        "producto" : fields.String( description="producto"),
        "marca" : fields.String( description="marca"),
        "modelo" :fields.String( description="modelo"),
        "origen" : fields.String(description="origen"),
        "foto" : fields.String(description="foto"),
        "cantidad" : fields.Integer(description="cantidad"),
        "observaciones" : fields.String(description="observaciones"),
        "lugarId" : fields.Integer(description="lugarId"),
        "pertenece" : fields.String( description="pertenece"),
        "descompostura" : fields.String( description="descompostura"),
        "costo" : fields.Integer(description="costo"),
        "compra" : fields.String( description="compra"),
        "proveedor" : fields.String( description="proveedor"),
        "idMov" : fields.String( description="idMov")
        
    }
)

def createDevices(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = dispositivos_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    user_in_db = DispositivosModel.get_devices_by_codigo(data.get("codigo"))
    if user_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","",data.get("codigo"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("username"))

    lugar_in_db = LugaresModel.get_one_lugar(data.get("lugarId"))
    if not lugar_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("lugarId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("lugarId"))

    #status_in_db = EstatusUsuariosModel.get_one_status(data.get("statusId"))
    #if not status_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
    #    error = returnCodes.partial_response("TPM-4","",data.get("statusId"))
    #    listaErrores.append(error)
    #    return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("statusId"))

    device = DispositivosModel(data)

    try:
        device.save()
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_device = dispositivos_schema.dump(device)
    listaObjetosCreados.append(serialized_device)
    return returnCodes.custom_response(serialized_device, 201, "TPM-1")

@nsDevices.route("")
class DevicesList(Resource):
    @nsDevices.doc("lista de dispositivos")
    @nsDevices.expect(parser)
    def get(self):
        """List all status"""
        offset = 0
        limit = 10
        if "offset" in request.args:
            offset = request.args.get('offset',default = 0, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)
        devices = DispositivosModel.get_all_devices(offset,limit)
        #return catalogos
        serialized_devices = dispositivos_schema.dump(devices, many=True)
        return returnCodes.custom_response(serialized_devices, 200, "TPM-3")

    @nsDevices.doc("Crear equipo")
    @nsDevices.expect(DevicesModelApi)
    @nsDevices.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = dispositivos_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
       
        createDevices(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-20", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-20","", listaErrores)
    
    @nsDevices.doc("actualizar dispositivos")
    @nsDevices.expect(DevicesPatchApi)
    def patch(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = dispositivos_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        device = DispositivosModel.get_one_device(data.get("id"))
        if not device:
            
            return returnCodes.custom_response(None, 404, "TPM-4")
        if "lugarId" in data:
            lugar_in_db = LugaresModel.get_one_lugar(data.get("lugarId"))
            if not lugar_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("lugarId"))

        #if "statusId" in data:
        #    status_in_db = EstatusUsuariosModel.get_one_status(data.get("statusId"))
        #    if not status_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
        #        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("statusId"))

        try:
            device.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_device = dispositivos_schema.dump(device)
        return returnCodes.custom_response(serialized_device, 200, "TPM-6")

@nsDevices.route("/<int:id>")
@nsDevices.param("id", "The id identifier")
@nsDevices.response(404, "equipo no encontrado")
class OneDevice(Resource):
    @nsDevices.doc("obtener un equipo")
    def get(self, id):
       
        rol = DispositivosModel.get_one_device(id)
        if not rol:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = dispositivos_schema.dump(rol)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")

@nsDevices.route("/query")
@nsDevices.expect(parser)
@nsDevices.response(404, "equipo no encontrado")
class DeviceQuery(Resource):
    
    @nsDevices.doc("obtener varios equipos")
    @api.expect(DevicesQueryModel)
    def post(self):
        print(request.args)
        offset = 0
        limit = 10

        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        if "offset" in request.args:
            offset = request.args.get('offset',default = 0, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)

        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = dispositivos_schema_query.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        devices = DispositivosModel.get_devices_by_query(data,offset,limit)
        if not devices:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = dispositivos_schema.dump(devices,many=true)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")