# /src/views/GiroView

from email.policy import default
from heapq import nsmallest
from http import server
from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from sqlalchemy import true

from ..models.MovimentosModel import MovimientosModel, MovimientosSchema,MovimientosSchemaUpdate,MovimientosSchemaQuery,MovimientosSchemaSomeFields
from ..models.LugaresModel import LugaresModel
from ..models.UsuariosModel import UsuariosModel
from ..models.DispositivosModel import DispositivosModel
from ..models.TipoMovimientosModel import TipoMoveModel
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource,reqparse



app = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, location='args')
parser.add_argument('offset', type=int, location='args')
minFieldparser = reqparse.RequestParser()
minFieldparser.add_argument('limit', type=int, location='args')
minFieldparser.add_argument('offset', type=int, location='args')
minFieldparser.add_argument('value', type=str, location='headers')
movimientos_api = Blueprint("movimientos_api", __name__)
movimientos_schema = MovimientosSchema()
movimientos_schema_update = MovimientosSchemaUpdate()
movimientos_schema_query = MovimientosSchemaQuery()
movimientosschemasomefields = MovimientosSchemaSomeFields()
api = Api(movimientos_api)

nsMovements = api.namespace("movimientos", description="API operations for movimientos")

MovimientosQueryModel = nsMovements.model(
    "movimientosQuery",
    {
     
        "id": fields.Integer(description="identificador"),
        "dispositivoId" : fields.Integer(description="lugarId"),
        "usuarioId" : fields.Integer(description="lugarId"),
        "comentarios" : fields.String( description="idMov"),
        "LugarId" : fields.Integer( description="idMov"),
        "idMovimiento" :  fields.String(description="idMovimiento"),
        "tipoMovId" : fields.Integer(description="tipoMovId"),
        "comentarios" : fields.String( description="comentarios"),
        "fechaAltaRangoInicio":fields.String( description="foto"),
        "fechaAltaRangoFin":fields.String( description="foto")

    }
)

#parser.add_argument('DevicesQueryModel', type=json, location='body')

MovementsModelApi = nsMovements.model(
    "movimientos",
    {
     
      
     
        "dispositivoId" : fields.Integer(description="lugarId"),
        "usuarioId" : fields.Integer(description="lugarId"),
        "comentarios" : fields.String( description="idMov"),
        "LugarId" : fields.Integer( description="lugar id"),
        "idMovimiento" : fields.String(description="idMovimiento"),
        "tipoMovId" : fields.Integer(description="tipoMovId"),
        "comentarios" : fields.String( description="comentarios"),
        "foto" : fields.String( description="foto"),
        "foto2" : fields.String( description="foto2")

    }
)

MovementsModelListApi = nsMovements.model('movesList', {
    'movimientosList': fields.List(fields.Nested(MovementsModelApi)),
})

MovementsPatchApi = nsMovements.model(
    "movimientosPatch",
    {
        "id": fields.Integer(description="identificador"),
        "dispositivoId" : fields.Integer(description="lugarId"),
        "usuarioId" : fields.Integer(description="lugarId"),
        "comentarios" : fields.String( description="idMov"),
        "LugarId" : fields.Integer( description="idMov"),
        "idMovimiento" : fields.String(description="idMovimiento"),
        "tipoMovId" : fields.Integer(description="tipoMovId"),
        "comentarios" : fields.String( description="comentarios"),
        "foto" : fields.String( description="foto"),
        "foto2" : fields.String( description="foto2")
        
    }
)

def createMovements(data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    
    # Aquí hacemos las validaciones para ver si el catalogo de negocio ya existe previamente
    device_in_db = DispositivosModel.get_one_device(data.get("dispositivoId"))
    if not device_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","el dispositivo no existe",data.get("dispositivoId"),data.get("id"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("dispositivoId"))

    

    lugar_in_db = LugaresModel.get_one_lugar(data.get("LugarId"))
    if not lugar_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","el lugar no existe",data.get("LugarId"),data.get("id"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("LugarId"))

    user_in_db = UsuariosModel.get_one_users(data.get("usuarioId"))
    if not user_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","el usuario no existe",data.get("usuarioId"),data.get("id"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("usuarioId"))

    tipo_in_db = TipoMoveModel.get_one_tipo(data.get("tipoMovId"))
    if not tipo_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-5","el tipo de movimiento no existe",data.get("tipoMovId"),data.get("id"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-5", "", data.get("tipoMovId"),data.get("id"))
    diference = 1

    if 'cantidad_Actual' in data:

        if data['cantidad_Actual']>0:
            if tipo_in_db.id==1:
                diference=device_in_db.cantidad - data['cantidad_Actual']
            if tipo_in_db.id==2:
                diference=device_in_db.cantidad + data['cantidad_Actual']
        else:
            if tipo_in_db.id==1:
                diference=device_in_db.cantidad - 1
            if tipo_in_db.id==2:
                diference=device_in_db.cantidad + 1
    else:
        if tipo_in_db.id==1:
            diference=device_in_db.cantidad - 1
        if tipo_in_db.id==2:
            diference=device_in_db.cantidad + 1

    if diference<0:

    #restar cantidad a dispositivo que salio, sumar si entro
        error = returnCodes.partial_response("TPM-17","",data.get("dispositivoId"),data.get("id"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-17", "", data.get("dispositivoId"))


    dictDevice={
        "id":data.get("dispositivoId"),
        "cantidad":diference,
        "lugarId":data.get("LugarId")
    }

    
    move = MovimientosModel(data)

    try:
        device_in_db.update(dictDevice)
        move.save()
    except Exception as err:
        #error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7","",str(err),data.get("id"))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_move = movimientos_schema.dump(move)
    listaObjetosCreados.append(serialized_move)
    return returnCodes.custom_response(serialized_move, 201, "TPM-1")

@nsMovements.route("")
class DevicesList(Resource):
    @nsMovements.doc("lista de movimientos")
    @nsMovements.expect(parser)
    def get(self):
        """List all status"""
        offset = 1
        limit = 10
        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)
        devices,rows = MovimientosModel.get_all_movimientos_somefields(offset,limit)
        #return catalogos
        serialized_movimientos = movimientosschemasomefields.dump(devices.items, many=True)
        return returnCodes.custom_response(serialized_movimientos, 200, "TPM-3","",[],True,rows)

    @nsMovements.doc("Crear movimiento")
    @nsMovements.expect(MovementsModelListApi)
    @nsMovements.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:

            if  'movimientosList' in req_data:

                req_data =req_data['movimientosList']
                
            data = movimientos_schema.load(req_data,many=True)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
        for item in data:
            createMovements(item, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsMovements.doc("actualizar movimientos")
    @nsMovements.expect(MovementsPatchApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = movimientos_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        move = MovimientosModel.get_one_movimiento(data.get("id"))
        if not move:
            
            return returnCodes.custom_response(None, 404, "TPM-4")
        if "LugarId" in data:
            lugar_in_db = LugaresModel.get_one_lugar(data.get("LugarId"))
            if not lugar_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "el lugar no existe", data.get("LugarId"))

        if "usuarioId" in data:
            usuario_in_db = UsuariosModel.get_one_users(data.get("usuarioId"))
            if not usuario_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "el usuario no existe", data.get("usuarioId"))
        
        if "dispositivoId" in data:
            dispositivo_in_db = DispositivosModel.get_one_device(data.get("dispositivoId"))
            if not dispositivo_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "el dispositivo no existe", data.get("dispositivoId"))

        if "tipoMovId" in data:
            tipo_in_db = TipoMoveModel.get_one_tipo(data.get("tipoMovId"))
            if not tipo_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "el tipo de movimiento no existe", data.get("tipoMovId"))

        try:
            move.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_move = movimientos_schema.dump(move)
        return returnCodes.custom_response(serialized_move, 200, "TPM-6")

@nsMovements.route("/<int:id>")
@nsMovements.param("id", "The id identifier")
@nsMovements.response(404, "movimiento no encontrado")
class OneDevice(Resource):
    @nsMovements.doc("obtener un movimiento")
    def get(self, id):
       
        move = MovimientosModel.get_one_movimiento(id)
        if not move:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = movimientos_schema.dump(move)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")

@nsMovements.route("/LastOne/<int:id>")
@nsMovements.param("id", "The id identifier")
@nsMovements.response(404, "movimiento no encontrado")
class OneMovementLast(Resource):
    @nsMovements.doc("obtener un movimiento")
    def get(self, id):
       
        move = MovimientosModel.get_lastone_movimiento(id)
        if not move:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = movimientos_schema.dump(move)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")

@nsMovements.route("/query")
@nsMovements.expect(parser)
@nsMovements.response(404, "movimiento no encontrado")
class DeviceQuery(Resource):
    
    @nsMovements.doc("obtener varios movimientos")
    @api.expect(MovimientosQueryModel)
    def post(self):
        
        offset = 0
        limit = 10

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
            data = movimientos_schema_query.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        moves =MovimientosModel.get_movimientos_by_query(data,offset,limit)
        
        if not moves:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = movimientos_schema.dump(moves.items,many=true)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3") 


@nsMovements.route("/filter")
@nsMovements.expect(minFieldparser)
@nsMovements.response(404, "movimiento no encontrado")
class MovementFilter(Resource):
    
    @nsMovements.doc("obtener varios movimientos")
    def get(self):
      
        offset = 1
        limit = 100

        value=""
        if "value" in request.headers:
            value =request.headers['value']

        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 100, type = int)


        moves,rows = MovimientosModel.get_all_movimientos_by_like_new_query(value,offset,limit)
        if not moves:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = movimientosschemasomefields.dump(moves.items,many=True)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3","",[],True,rows)


@nsMovements.route("/filtermovementFields")
@nsMovements.expect(minFieldparser)
@nsMovements.response(404, "movimiento no encontrado")
class MovementFilterPost(Resource):
    

    @nsMovements.doc("obtener varios movimientos, filtro con pocos campos")
    @nsMovements.header("value", "el texto de valor a buscar", required=True)  # Agrega los encabezados aquí
    def get(self):
      
        offset = 1
        limit = 100

        value=""
        if "value" in request.headers:
            value =request.headers['value']

     
        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 100, type = int)


        devices = MovimientosModel.get_movements_by_like_someFields(value,offset,limit)

        serialized_movements = movimientosschemasomefields.dump(devices,many=True)
        return returnCodes.custom_response(serialized_movements, 200, "TPM-3")