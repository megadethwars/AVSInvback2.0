# app/src/models/CatalogoModel.py
from marshmallow import fields, Schema, validate
import datetime
from . import db

class UsuariosModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invUsuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(45))
    username = db.Column(db.String(45))
    apellidoPaterno = db.Column(db.String(45))
    apellidoMaterno = db.Column(db.String(45))
    password = db.Column(db.Text)
    telefono = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    foto = db.Column(db.Text)

    rolId = db.Column(
        db.Integer,db.ForeignKey("invRoles.id"),nullable=False
    )

    statusId = db.Column(
        db.Integer,db.ForeignKey("invStatusUsuarios.id"),nullable=False
    )

    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
        self.nombre = data.get('nombre')
        self.username = data.get("username")
        self.apellidoPaterno = data.get('apellidoPaterno')
        self.apellidoMaterno = data.get('apellidoMaterno')
        self.password = data.get('password')
        self.telefono = data.get('telefono')
        self.correo =data.get('correo') 
        self.foto =data.get('foto')
        self.rolId = data.get("rolId")
        self.statusId = data.get("statusId")
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
    def get_all_users():
        return UsuariosModel.query.all()


    @staticmethod
    def get_one_users(id):
        return UsuariosModel.query.get(id)

    @staticmethod
    def get_status_by_nombre(value):
        return UsuariosModel.query.filter_by(nombre=value).first()

    @staticmethod
    def get_users_by_username(value):
        return UsuariosModel.query.filter_by(username=value).first()

    def __repr(self):
        return '<id {}>'.format(self.id)

class UsuariosSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    nombre = fields.Str(required=True, validate=[validate.Length(max=45)])
    username = fields.Str(required=True, validate=[validate.Length(max=45)])
    apellidoPaterno = fields.Str(required=True, validate=[validate.Length(max=45)])
    apellidoMaterno = fields.Str(required=True, validate=[validate.Length(max=45)])
    password = fields.Str(required=True)
    telefono = fields.Str(required=True, validate=[validate.Length(max=45)])
    correo =fields.Str(required=True, validate=[validate.Length(max=100)])
    foto =fields.Str()
    rolId = fields.Integer(required=True)
    statusId = fields.Integer(required=True)
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class UsuariosSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    nombre = fields.Str(required=True, validate=[validate.Length(max=45)])
    username = fields.Str(required=True, validate=[validate.Length(max=45)])
    apellidoPaterno = fields.Str(required=True, validate=[validate.Length(max=45)])
    apellidoMaterno = fields.Str(required=True, validate=[validate.Length(max=45)])
    password = fields.Str(required=True)
    telefono = fields.Str(required=True, validate=[validate.Length(max=45)])
    correo =fields.Str(required=True, validate=[validate.Length(max=100)])
    foto =fields.Str()
    rolId = fields.Integer(required=True)
    statusId = fields.Integer(required=True)
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()