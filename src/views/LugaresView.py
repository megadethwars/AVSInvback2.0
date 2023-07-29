from flask import Flask, request, json, Response, Blueprint, g
#from marshmallow import ValidationError

#from ..shared import returnCodes
from flask_restx import Api,fields,Resource

app = Flask(__name__)
lugares_api = Blueprint("lugares_api", __name__)

api = Api(lugares_api)

#nsLugares = api.namespace("lugares", description="API operations for lugares")

# LugaresModelApi = nsLugares.model(
#     "LugaresModel",
#     {
#         "lugar": fields.String(required=True, description="lugar"),
#         "activo": fields.Boolean(required=True, description="activo")
#     }
# )

# LugaresModelListApi = nsLugares.model('lugaresList', {
#     'lugares': fields.List(fields.Nested(LugaresModelApi)),
# })

# LugaresPatchApi = nsLugares.model(
#     "LugarPatchModel",
#     {
#         "id": fields.Integer(required=True, description="identificador"),
#         "lugar": fields.String(required=True, description="lugar"),
#         "activo": fields.Boolean(description="activo")
        
#     }
# )


# @nsLugares.route("")
# class LugaresList(Resource):
#     @nsLugares.doc("lista de lugares")
#     def get(self):
#         """List all lugares"""
#         print('getting')
        
#         #return catalogos
#         serialized_lugares = [
#             {
#                 "id":1
#             },{
#                 "id":2
#             }
#         ]
#         return "OK"
#         #return returnCodes.custom_response(serialized_lugares, 200, "TPM-3")
