# app/src/models/CatalogoModel.py
from enum import unique
from pkgutil import ModuleInfo
from marshmallow import fields, Schema, validate
import datetime
from sqlalchemy import desc
import sqlalchemy
from . import db
from sqlalchemy import Date,cast
from .DispositivosModel import DispositivosSchema,DispositivosModel
from .UsuariosModel import UsuariosSchema,UsuariosModel
from .LugaresModel import LugaresSchema,LugaresModel
from sqlalchemy import or_
class ReportesModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invReportes'

    id = db.Column(db.Integer, primary_key=True)
    dispositivoId = db.Column(
        db.Integer,db.ForeignKey("invDispositivos.id"),nullable=False
    )
    usuarioId = db.Column(
        db.Integer,db.ForeignKey("invUsuarios.id"),nullable=False
    )
    
    comentarios = db.Column(db.Text)
    foto = db.Column(db.Text)
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    dispositivo=db.relationship(
        "DispositivosModel",backref=db.backref("invDispositivos",lazy=True)
    )

  
    usuario=db.relationship(
        "UsuariosModel",backref=db.backref("invUsuarios",lazy=True)
    )

    def __init__(self, data):
        """
        Class constructor
        """
        self.dispositivoId = data.get("dispositivoId")
        self.usuarioId = data.get("usuarioId")
        self.comentarios = data.get("comentarios")
        self.foto = data.get("foto")
        

        self.fechaAlta = datetime.datetime.utcnow()
        self.fechaUltimaModificacion = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, item in data.items():
            setattr(self, key, item)
        self.fechaUltimaModificacion = datetime.datetime.utcnow()
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all_reportes(offset=0,limit=10):
        return ReportesModel.query.order_by(ReportesModel.id).offset(offset).limit(limit).all()

    @staticmethod
    def saveAndUpdate(data):
        try:
            with db.session.begin() as session:  # Comienza una transacción
                # Crear un nuevo registro en "invReportes"
                report = ReportesModel(data)
                session.add(report)

                # Realiza la actualización en "invDispositivos" si se proporciona la información
                if "dispositivoId" in data:
                    dispositivo = session.query(DispositivosModel).filter_by(id=report["dispositivoId"]).first()
                    if dispositivo:
                        dispositivo.descompostura = data["dispositivoId"]

                # La transacción se confirmará automáticamente si no hay errores
        except Exception as err:
            return False,{}

        return True,report

    @staticmethod
    def get_one_report(id):
        return ReportesModel.query.get(id)
    
    @staticmethod
    def get_all_reports_by_like(value,offset=1,limit=10):
        lugares=[]
        devices=[]
        users=[]

        lugar = LugaresModel.get_lugar_by_like(value,offset=1,limit=100)
        
        if len(lugar.items)!=0:
            for x in lugar.items:
                lugares.append(x.id)
        
        device = DispositivosModel.get_device_by_codigo_like_entity(value,offset=1,limit=1000)
        
        if len(device.items)!=0:
            for x in device.items:
                devices.append(x.id)
        
        user = UsuariosModel.get_user_by_params_like_entity(value,offset=1,limit=100)
        
        if len(user.items)!=0:
            for x in user.items:
                users.append(x.id)

     
        result = ReportesModel.query.filter(or_(ReportesModel.usuarioId.in_(users),ReportesModel.dispositivoId.in_(devices), ReportesModel.comentarios.ilike(f'%{value}%'))).order_by(ReportesModel.id).paginate(page=offset,per_page=limit,error_out=False) 
        return result


    @staticmethod
    def get_reportes_by_query(jsonFiltros,offset=1,limit=5):
        #return DispositivosModel.query.filter_by(**jsonFiltros).paginate(page=offset,per_page=limit,error_out=False)
        #return ReportesModel.query.filter_by(**jsonFiltros).order_by(ReportesModel.id).offset(offset).limit(limit).all()


        if "fechaAltaRangoInicio" in jsonFiltros and "fechaAltaRangoFin" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            end = jsonFiltros["fechaAltaRangoFin"]
            del jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoFin"]
            alta = alta+" 00:00:00.000"
            end = end + " 23:59:59.999"
            return ReportesModel.query.filter_by(**jsonFiltros).filter(ReportesModel.fechaAlta >= alta).filter(ReportesModel.fechaAlta <= end).order_by(ReportesModel.id).paginate(page=offset,per_page=limit,error_out=False)
        
        elif "fechaAltaRangoInicio" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoInicio"]
            return ReportesModel.query.filter_by(**jsonFiltros).filter(cast(ReportesModel.fechaAlta,Date) == alta).order_by(ReportesModel.id).paginate(page=offset,per_page=limit,error_out=False)
        
        else:
            return ReportesModel.query.filter_by(**jsonFiltros).order_by(ReportesModel.id).paginate(page=offset,per_page=limit,error_out=False)

    def __repr(self):
        return '<id {}>'.format(self.id)

class ReportesSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    dispositivoId = fields.Integer(required=True)
    usuarioId = fields.Integer(required=True)
    comentarios = fields.Str()
    foto = fields.Str()
    dispositivo = fields.Nested(DispositivosSchema)
    usuario = fields.Nested(UsuariosSchema)
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class ReportesSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    dispositivoId = fields.Integer()
    usuarioId = fields.Integer()
    comentarios = fields.Str()
    foto = fields.Str()
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class ReportesSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    dispositivoId = fields.Integer()
    usuarioId = fields.Integer()
    comentarios = fields.Str()
    foto = fields.Str( validate=[validate.Length(max=500)])
    fechaAltaRangoInicio=fields.Date()
    fechaAltaRangoFin=fields.Date()
  
