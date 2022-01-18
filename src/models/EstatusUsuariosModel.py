# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class EstatusUsuariosModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invStatusUsuarios'

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
    def get_all_status():
        return EstatusUsuariosModel.query.all()


    @staticmethod
    def get_one_status(id):
        return EstatusUsuariosModel.query.get(id)

    @staticmethod
    def get_status_by_tipo(value):
        return EstatusUsuariosModel.query.filter_by(descripcion=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class EstatusUsuariosSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    descripcion = fields.Str(required=True, validate=[validate.Length(max=45)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class EstatusUsuariosSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    descripcion = fields.Str(required=True, validate=[validate.Length(max=45)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()