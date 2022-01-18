# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class StatusLugaresModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invLugares'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100))
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.descripcion = data.get('descripcion')
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
        return StatusLugaresModel.query.all()

    @staticmethod
    def get_one_lugar(id):
        return StatusLugaresModel.query.get(id)

    @staticmethod
    def get_lugar_by_nombre(value):
        return StatusLugaresModel.query.filter_by(descripcion=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class LugaresSchema(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    descripcion = fields.Str(required=True, validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()



class LugaresSchemaUpdate(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    descripcion = fields.Str(validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
 