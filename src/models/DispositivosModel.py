# app/src/models/CatalogoModel.py
from pkgutil import ModuleInfo
from marshmallow import fields, Schema, validate
import datetime
from sqlalchemy import desc
import sqlalchemy
from . import db
from sqlalchemy import Date,cast

class DispositivosModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invDispositivos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(45))
    producto = db.Column(db.String(45))
    marca = db.Column(db.String(45))
    modelo = db.Column(db.String(45))
    origen = db.Column(db.String(45))
    foto = db.Column(db.Text)
    cantidad =db.Column(db.Integer)
    observaciones = db.Column(db.String(250))
    lugarId = db.Column(
        db.Integer,db.ForeignKey("invLugares.id"),nullable=False
    )
    pertenece = db.Column(db.String(45))
    descompostura = db.Column(db.String(100))
    costo = db.Column(db.Integer)
    compra = db.Column(db.String(100))
    proveedor = db.Column(db.String(100))
    idMov = db.Column(db.Text)
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)

    def __init__(self, data):
        """
        Class constructor
        """
      

        self.codigo = data.get("codigo")
        self.producto = data.get("producto")
        self.marca = data.get("marca")
        self.modelo = data.get("modelo")
        self.origen = data.get("origen")
        self.foto = data.get("foto")
        self.cantidad = data.get("cantidad")
        self.observaciones = data.get("observaciones")
        self.lugarId = data.get("lugarId")
        self.pertenece = data.get("pertenece")
        self.descompostura = data.get("descompostura")
        self.costo = data.get("costo")
        self.compra = data.get("compra")
        self.proveedor = data.get("proveedor")
        self.idMov = data.get("idMov")

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
    def get_all_devices(offset=0,limit=10):
        return DispositivosModel.query.order_by(DispositivosModel.id).offset(offset).limit(limit).all()


    @staticmethod
    def get_one_device(id):
        return DispositivosModel.query.get(id)

    @staticmethod
    def get_devices_by_codigo(value):
        return DispositivosModel.query.filter_by(codigo=value).first()

    @staticmethod
    def get_devices_by_producto(value):
        return DispositivosModel.query.filter_by(producto=value).first()

    @staticmethod
    def get_devices_by_query(jsonFiltros,offset=1,limit=5):
        #return DispositivosModel.query.filter_by(**jsonFiltros).paginate(offset,limit,error_out=False)
        return DispositivosModel.query.filter_by(**jsonFiltros).order_by(DispositivosModel.id).offset(offset).limit(limit).all()


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

class DispositivosSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    codigo = fields.Str(required=True, validate=[validate.Length(max=45)])
    producto = fields.Str(required=True, validate=[validate.Length(max=45)])
    marca = fields.Str(required=True, validate=[validate.Length(max=45)])
    modelo = fields.Str(required=True, validate=[validate.Length(max=45)])
    origen = fields.Str( validate=[validate.Length(max=45)])
    foto = fields.Str()
    cantidad = fields.Integer(required=True)
    observaciones = fields.Str( validate=[validate.Length(max=250)])
    lugarId = fields.Integer(required=True)
    pertenece = fields.Str( validate=[validate.Length(max=45)])
    descompostura = fields.Str( validate=[validate.Length(max=100)])
    costo = fields.Integer()
    compra = fields.Str( validate=[validate.Length(max=100)])
    proveedor = fields.Str( validate=[validate.Length(max=100)])
    idMov = fields.Str( validate=[validate.Length(max=500)])

    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class DispositivosSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    codigo = fields.Str(validate=[validate.Length(max=45)])
    producto = fields.Str(validate=[validate.Length(max=45)])
    marca = fields.Str(validate=[validate.Length(max=45)])
    modelo = fields.Str(validate=[validate.Length(max=45)])
    origen = fields.Str(validate=[validate.Length(max=45)])
    foto = fields.Str()
    cantidad = fields.Integer()
    observaciones = fields.Str(validate=[validate.Length(max=250)])
    lugarId = fields.Integer()
    pertenece = fields.Str(validate=[validate.Length(max=45)])
    descompostura = fields.Str(validate=[validate.Length(max=100)])
    costo = fields.Integer()
    compra = fields.Str(validate=[validate.Length(max=100)])
    proveedor = fields.Str(validate=[validate.Length(max=100)])
    idMov = fields.Str(validate=[validate.Length(max=500)])
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class DispositivosSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    codigo = fields.Str(validate=[validate.Length(max=45)])
    producto = fields.Str(validate=[validate.Length(max=45)])
    marca = fields.Str(validate=[validate.Length(max=45)])
    modelo = fields.Str(validate=[validate.Length(max=45)])
    origen = fields.Str(validate=[validate.Length(max=45)])
    foto = fields.Str()
    cantidad = fields.Integer()
    observaciones = fields.Str(validate=[validate.Length(max=250)])
    lugarId = fields.Integer()
    pertenece = fields.Str(validate=[validate.Length(max=45)])
    descompostura = fields.Str(validate=[validate.Length(max=100)])
    costo = fields.Integer()
    compra = fields.Str(validate=[validate.Length(max=100)])
    proveedor = fields.Str(validate=[validate.Length(max=100)])
    idMov = fields.Str(validate=[validate.Length(max=500)])