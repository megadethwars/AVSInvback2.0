from flask import Flask, request, json, Response, Blueprint, g
#from marshmallow import ValidationError

#from ..shared import returnCodes
from flask_restx import Api,fields,Resource

app = Flask(__name__)
lugares_api = Blueprint("lugares_api", __name__)

api = Api(lugares_api)

nsLugares = api.namespace("lugares", description="API operations for lugares")