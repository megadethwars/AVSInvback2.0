# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class RolesModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invRoles'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.nombre = data.get('nombre')
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
    def get_all_roles():
        return RolesModel.query.all()

    @staticmethod
    def get_one_rol(id):
        return RolesModel.query.get(id)

    @staticmethod
    def get_rol_by_nombre(value):
        return RolesModel.query.filter_by(nombre=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class RolesSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    nombre = fields.Str(required=True, validate=[validate.Length(max=45)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()