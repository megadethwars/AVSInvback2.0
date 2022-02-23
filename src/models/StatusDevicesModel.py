from marshmallow import fields, Schema, validate
import datetime
from . import db

class StatusDevicesModel(db.Model):
    """
    status Model
    """
    
    __tablename__ = 'invStatusDevices'

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
        return StatusDevicesModel.query.all()

    @staticmethod
    def get_one_status(id):
        return StatusDevicesModel.query.get(id)

    @staticmethod
    def get_status_by_nombre(value):
        return StatusDevicesModel.query.filter_by(descripcion=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class StatusDevicesSchema(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    descripcion = fields.Str(required=True, validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()



class StatusDevicesSchemaUpdate(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    descripcion = fields.Str(validate=[validate.Length(max=100)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()