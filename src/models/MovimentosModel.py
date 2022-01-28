# app/src/models/CatalogoModel.py
from enum import unique
from pkgutil import ModuleInfo
from marshmallow import fields, Schema, validate
import datetime
from sqlalchemy import desc
import sqlalchemy
from . import db
from sqlalchemy import Date,cast

class MovimientosModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invMovimientos'

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
        return MovimientosModel.query.order_by(MovimientosModel.id).offset(offset).limit(limit).all()


    @staticmethod
    def get_one_report(id):
        return MovimientosModel.query.get(id)


    @staticmethod
    def get_reportes_by_query(jsonFiltros,offset=1,limit=5):
        #return DispositivosModel.query.filter_by(**jsonFiltros).paginate(offset,limit,error_out=False)
        return MovimientosModel.query.filter_by(**jsonFiltros).order_by(ReportesModel.id).offset(offset).limit(limit).all()


        if "fechaAltaRangoInicio" in jsonFiltros and "fechaAltaRangoFin" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            end = jsonFiltros["fechaAltaRangoFin"]
            del jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoFin"]
            alta = alta+"T00:00:00.000000"
            end = end + "T23:59:59.999999"
            return ComercioModel.query.filter_by(**jsonFiltros).filter(ComercioModel.fechaAlta >= alta).filter(ComercioModel.fechaAlta <= end).paginate(offset,limit,error_out=False),rows
        
        elif "fechaAltaRangoInicio" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoInicio"]
            return ComercioModel.query.filter_by(**jsonFiltros).filter(cast(ComercioModel.fechaAlta,Date) == alta).paginate(offset,limit,error_out=False),rows
        
        else:
            return ComercioModel.query.filter_by(**jsonFiltros).paginate(offset,limit,error_out=False),rows

    def __repr(self):
        return '<id {}>'.format(self.id)

class MovimientosSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    dispositivoId = fields.Integer(required=True)
    usuarioId = fields.Integer(required=True)
    comentarios = fields.Str()
    foto = fields.Str( validate=[validate.Length(max=500)])

    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class MovimientosSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    dispositivoId = fields.Integer()
    usuarioId = fields.Integer()
    comentarios = fields.Str()
    foto = fields.Str( validate=[validate.Length(max=500)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class MovimientosSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    dispositivoId = fields.Integer()
    usuarioId = fields.Integer()
    comentarios = fields.Str()
    foto = fields.Str( validate=[validate.Length(max=500)])
