# /src/views/GiroView

from email.policy import default
from flask import Flask, request, json, Response, Blueprint, g
from marshmallow import ValidationError
from sqlalchemy import true


from ..models.DispositivosModel import DispositivosModel
from ..models.UsuariosModel import UsuariosModel
from ..models.ReportesModel import ReportesModel,ReportesSchema,ReportesSchemaUpdate,ReportesSchemaQuery
from ..models import db
from ..shared import returnCodes
from flask_restx import Api,fields,Resource,reqparse

app = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('limit', type=int, location='args')
parser.add_argument('offset', type=int, location='args')
Report_api = Blueprint("reports_api", __name__)
reportes_schema = ReportesSchema()
reportes_schema_update = ReportesSchemaUpdate()
reportes_schema_query = ReportesSchemaQuery()
api = Api(Report_api)

nsReports = api.namespace("reports", description="API operations for reportes")

ReportsQueryModel = nsReports.model(
    "reportesQuery",
    {
     
        "id": fields.Integer(description="identificador"),
        "dispositivoId" : fields.Integer(description="dispositivoId"),
        "usuarioId" : fields.Integer(description="usuarioId"),
        "comentarios" : fields.String(description="comentarios"),
        "foto" : fields.String( description="foto"),
        "fechaAltaRangoInicio":fields.String( description="foto"),
        "fechaAltaRangoFin":fields.String( description="foto")

    }
)

#parser.add_argument('DevicesQueryModel', type=json, location='body')

ReportsModelApi = nsReports.model(
    "reportes",
    {

        "dispositivoId" : fields.Integer(required=True,description="dispositivoId"),
        "usuarioId" : fields.Integer(required=True,description="usuarioId"),
        "comentarios" : fields.String(description="comentarios"),
        "foto" : fields.String( description="foto")

    }
)

DevicesModelListApi = nsReports.model('usersList', {
    'reportlist': fields.List(fields.Nested(ReportsModelApi)),
})

ReportsPatchApi = nsReports.model(
    "reportes",
    {
        "id": fields.Integer(required=True, description="identificador"),
        "dispositivoId" : fields.Integer(required=True,description="dispositivoId"),
        "usuarioId" : fields.Integer(required=True,description="usuarioId"),
        "comentarios" : fields.String(description="comentarios"),
        "foto" : fields.String( description="foto")
        
    }
)

def createReports(req_data, listaObjetosCreados, listaErrores):
    #app.logger.info("Creando catalogo" + json.dumps(req_data))
    data = None
    try:
        data = reportes_schema.load(req_data)
    except ValidationError as err:
        #error = returnCodes.custom_response(None, 400, "TPM-2", str(err)).json
        error = returnCodes.partial_response("TPM-2",str(err))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 400, "TPM-2", str(err))

    user_in_db = UsuariosModel.get_one_users(data.get("usuarioId"))
    if not user_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","",data.get("usuarioId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("usuarioId"))

    device_in_db = DispositivosModel.get_one_device(data.get("dispositivoId"))
    if not device_in_db:
        #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
        error = returnCodes.partial_response("TPM-4","el equipo no existe",data.get("dispositivoId"))
        listaErrores.append(error)
        return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("dispositivoId"))

    report = ReportesModel(data)

    try:
        report.save()
        dataToUpdateDevice={"id":data["dispositivoId"],"descompostura":data["comentarios"]}
        device_in_db.update(dataToUpdateDevice)
    except Exception as err:
        error = returnCodes.custom_response(None, 500, "TPM-7", str(err)).json
        error = returnCodes.partial_response("TPM-7",str(err))
        #error="Error al intentar dar de alta el registro "+data.get("nombre")+", "+error["message"]
        listaErrores.append(error)
        db.session.rollback()
        return returnCodes.custom_response(None, 500, "TPM-7", str(err))
    
    serialized_report = reportes_schema.dump(report)
    listaObjetosCreados.append(serialized_report)
    return returnCodes.custom_response(serialized_report, 201, "TPM-1")

@nsReports.route("")
class ReportesList(Resource):
    @nsReports.doc("lista de reportes")
    @nsReports.expect(parser)
    def get(self):
        """List all status"""
        offset = 0
        limit = 10
        if "offset" in request.args:
            offset = request.args.get('offset',default = 0, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 10, type = int)
        reportes = ReportesModel.get_all_reportes(offset,limit)
        #return catalogos
        serialized_reportes = reportes_schema.dump(reportes, many=True)
        return returnCodes.custom_response(serialized_reportes, 200, "TPM-3")

    @nsReports.doc("Crear reporte")
    @nsReports.expect(ReportsModelApi)
    @nsReports.response(201, "created")
    def post(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")

        req_data = request.json
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = reportes_schema.load(req_data)
        except ValidationError as err:    
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))
        
        listaObjetosCreados = list()
        listaErrores = list()
        
       
        createReports(data, listaObjetosCreados, listaErrores)
        
        if(len(listaObjetosCreados)>0):
            if(len(listaErrores)==0):
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-8")
            else:
                return returnCodes.custom_response(listaObjetosCreados, 201, "TPM-16", "",listaErrores)
        else:
            return returnCodes.custom_response(None, 409, "TPM-16","", listaErrores)
    
    @nsReports.doc("actualizar reportes")
    @nsReports.expect(ReportsPatchApi)
    def put(self):
        if request.is_json is False:
            return returnCodes.custom_response(None, 400, "TPM-2")
        req_data = request.json
        data = None
        if(not req_data):
            return returnCodes.custom_response(None, 400, "TPM-2")
        try:
            data = reportes_schema_update.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        report = ReportesModel.get_one_report(data.get("id"))
        if not report:
            return returnCodes.custom_response(None, 404, "TPM-4","el reporte no existe")
        if "dispositivoId" in data:
            device_in_db = DispositivosModel.get_one_device(data.get("dispositivoId"))
            if not device_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("dispositivoId"))

        if "usuarioId" in data:
            user_in_db = UsuariosModel.get_one_users(data.get("usuarioId"))
            if not user_in_db:
                #error = returnCodes.custom_response(None, 409, "TPM-5", "", data.get("nombre")).json
                
                return returnCodes.custom_response(None, 409, "TPM-4", "", data.get("usuarioId"))

        try:
            report.update(data)
        except Exception as err:
            return returnCodes.custom_response(None, 500, "TPM-7", str(err))

        serialized_report = reportes_schema.dump(report)
        return returnCodes.custom_response(serialized_report, 200, "TPM-6")

@nsReports.route("/<int:id>")
@nsReports.param("id", "The id identifier")
@nsReports.response(404, "reporte no encontrado")
class OneReport(Resource):
    @nsReports.doc("obtener un equipo")
    def get(self, id):
       
        report = ReportesModel.get_one_report(id)
        if not report:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_report = reportes_schema.dump(report)
        return returnCodes.custom_response(serialized_report, 200, "TPM-3")

@nsReports.route("/query")
@nsReports.expect(parser)
@nsReports.response(404, "reporte no encontrado")
class ReportQuery(Resource):
    
    @nsReports.doc("obtener varios reportes")
    @api.expect(ReportsQueryModel)
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
            data = reportes_schema_query.load(req_data, partial=True)
        except ValidationError as err:
            return returnCodes.custom_response(None, 400, "TPM-2", str(err))

        devices = ReportesModel.get_reportes_by_query(data,offset,limit)
        if not devices:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_reportes = reportes_schema.dump(devices.items,many=true)
        return returnCodes.custom_response(serialized_reportes, 200, "TPM-3")


@nsReports.route("/filter/<value>")
@nsReports.expect(parser)
@nsReports.response(404, "reporte no encontrado")
class MovementFilter(Resource):
    
    @nsReports.doc("obtener varios reportes")
    def get(self,value):
      
        offset = 1
        limit = 100

        

        if "offset" in request.args:
            offset = request.args.get('offset',default = 1, type = int)

        if "limit" in request.args:
            limit = request.args.get('limit',default = 100, type = int)


        moves = ReportesModel.get_all_reports_by_like(value,offset,limit)
        if not moves:
            return returnCodes.custom_response(None, 404, "TPM-4")

        serialized_device = reportes_schema.dump(moves.items,many=True)
        return returnCodes.custom_response(serialized_device, 200, "TPM-3")