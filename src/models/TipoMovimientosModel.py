# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class TipoMoveModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invTipoMoves'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(45))
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.tipo = data.get('tipo')
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
    def get_all_tipos():
        return TipoMoveModel.query.all()

    @staticmethod
    def get_one_tipo(id):
        return TipoMoveModel.query.get(id)

    @staticmethod
    def get_tipo_by_nombre(value):
        return TipoMoveModel.query.filter_by(tipo=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class TipoMoveSchema(Schema):
    """
    lugar Schema
    """
    id = fields.Int()
    tipo = fields.Str(required=True, validate=[validate.Length(max=45)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
 


class TipoMoveSchemaUpdate(Schema):
    """
    lugar Schema
    """
    id = fields.Int(required=True)
    tipo = fields.Str(validate=[validate.Length(max=45)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
