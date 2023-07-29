# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class LugaresModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invLugares'

    id = db.Column(db.Integer, primary_key=True)
    lugar = db.Column(db.String(100))
    activo = db.Column(db.Boolean)
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.lugar = data.get('lugar')
        self.fechaAlta = datetime.datetime.utcnow()
        self.fechaUltimaModificacion = datetime.datetime.utcnow()
        self.activo = data.get("activo")

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
    def get_all_lugares():
        return LugaresModel.query.all()

    @staticmethod
    def get_one_lugar(id):
        return LugaresModel.query.get(id)

    @staticmethod
    def get_lugar_by_nombre(value):
        return LugaresModel.query.filter_by(lugar=value).first()
    
    @staticmethod
    def get_lugar_by_like(value,offset,limit):
        return LugaresModel.query.with_entities(LugaresModel.id).filter(LugaresModel.lugar.ilike(f'%{value}%') ).order_by(LugaresModel.id).paginate(page=offset,per_page=limit,error_out=False)

    def __repr(self):
        return '<id {}>'.format(self.id)

class LugaresSchema(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    lugar = fields.Str(required=True, validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
    activo = fields.Boolean()


class LugaresSchemaUpdate(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    lugar = fields.Str(validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
    activo = fields.Boolean()