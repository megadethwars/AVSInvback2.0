# app/src/models/CatalogoModel.py
from pkgutil import ModuleInfo
from marshmallow import fields, Schema, validate
import datetime
from .StatusDevicesModel import StatusDevicesSchema
from .LugaresModel import LugaresSchema,LugaresModel
from sqlalchemy import desc
import sqlalchemy
from . import db
from sqlalchemy import Date,cast
from sqlalchemy import or_
class DispositivosModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invDispositivos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100))
    producto = db.Column(db.String(100))
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    origen = db.Column(db.String(100))
    foto = db.Column(db.Text)
    cantidad =db.Column(db.Integer)
    observaciones = db.Column(db.String(250))
    lugarId = db.Column(
        db.Integer,db.ForeignKey("invLugares.id"),nullable=False
    )
    statusId= db.Column(
        db.Integer,db.ForeignKey("invStatusDevices.id"),nullable=False
    )
    pertenece = db.Column(db.String(100))
    descompostura = db.Column(db.String(100))
    costo = db.Column(db.Integer)
    compra = db.Column(db.String(100))
    proveedor = db.Column(db.String(100))
    idMov = db.Column(db.Text)
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)
    serie = db.Column(db.String(100))
    accesorios = db.Column(db.String(100))
    lugar=db.relationship(
        "LugaresModel",backref=db.backref("invLugares",lazy=True)
    )

  
    status=db.relationship(
        "StatusDevicesModel",backref=db.backref("invStatusDevices",lazy=True)
    )

  

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
        self.statusId= data.get("statusId")
        self.serie = data.get("serie")
        self.accesorios = data.get("accesorios")
        

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
    def get_all_devices(offset=1,limit=10):
        return DispositivosModel.query.order_by(DispositivosModel.id).paginate(offset,limit,error_out=False) 


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
    def get_device_by_codigo_like(value,offset,limit):
        return DispositivosModel.query.filter(DispositivosModel.codigo.ilike(f'%{value}%') ).order_by(DispositivosModel.id).paginate(offset,limit,error_out=False)

    def get_device_by_codigo_like_entity(value,offset,limit):
        return DispositivosModel.query.with_entities(DispositivosModel.id).filter(or_(DispositivosModel.codigo.ilike(f'%{value}%'),DispositivosModel.producto.ilike(f'%{value}%') , DispositivosModel.marca.ilike(f'%{value}%') , DispositivosModel.modelo.ilike(f'%{value}%'),DispositivosModel.serie.ilike(f'%{value}%')) ).order_by(DispositivosModel.id).paginate(offset,limit,error_out=False)

    @staticmethod
    def get_devices_by_like(value,offset=1,limit=100):

        lugares=[]
      
        lugar = LugaresModel.get_lugar_by_like(value,offset=1,limit=100)
        
        if len(lugar.items)!=0:
            for x in lugar.items:
                lugares.append(x.id)
        

        result = DispositivosModel.query.filter(or_(DispositivosModel.lugarId.in_(lugares),DispositivosModel.codigo.ilike(f'%{value}%') , DispositivosModel.producto.ilike(f'%{value}%') , DispositivosModel.marca.ilike(f'%{value}%') , DispositivosModel.modelo.ilike(f'%{value}%') , DispositivosModel.serie.ilike(f'%{value}%') , DispositivosModel.accesorios.ilike(f'%{value}%'))).order_by(DispositivosModel.id).paginate(offset,limit,error_out=False)
        return result
     

    @staticmethod
    def get_devices_by_query(jsonFiltros,offset=1,limit=100):
        #return DispositivosModel.query.filter_by(**jsonFiltros).paginate(offset,limit,error_out=False)
        return DispositivosModel.query.filter_by(**jsonFiltros).order_by(DispositivosModel.id).paginate(offset,limit,error_out=False) 


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
    codigo = fields.Str(required=True, validate=[validate.Length(max=100)])
    producto = fields.Str(required=True, validate=[validate.Length(max=100)])
    marca = fields.Str(required=True, validate=[validate.Length(max=100)])
    modelo = fields.Str(required=True, validate=[validate.Length(max=100)])
    origen = fields.Str( validate=[validate.Length(max=100)])
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
    statusId= fields.Integer(required=True)
    lugar=fields.Nested(LugaresSchema)
    status = fields.Nested(StatusDevicesSchema)
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
    serie = fields.Str( validate=[validate.Length(max=100)])
    accesorios = fields.Str( validate=[validate.Length(max=100)])

class DispositivosSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    codigo = fields.Str(validate=[validate.Length(max=100)])
    producto = fields.Str(validate=[validate.Length(max=100)])
    marca = fields.Str(validate=[validate.Length(max=100)])
    modelo = fields.Str(validate=[validate.Length(max=100)])
    origen = fields.Str(validate=[validate.Length(max=100)])
    foto = fields.Str()
    cantidad = fields.Integer()
    observaciones = fields.Str(validate=[validate.Length(max=250)])
    lugarId = fields.Integer()
    statusId= fields.Integer()
    pertenece = fields.Str(validate=[validate.Length(max=100)])
    descompostura = fields.Str(validate=[validate.Length(max=100)])
    costo = fields.Integer()
    compra = fields.Str(validate=[validate.Length(max=100)])
    proveedor = fields.Str(validate=[validate.Length(max=100)])
    idMov = fields.Str(validate=[validate.Length(max=500)])
    lugar=fields.Nested(LugaresSchema)
    status = fields.Nested(StatusDevicesSchema)
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
    serie = fields.Str( validate=[validate.Length(max=100)])
    accesorios = fields.Str( validate=[validate.Length(max=100)])


class DispositivosSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    codigo = fields.Str(validate=[validate.Length(max=100)])
    producto = fields.Str(validate=[validate.Length(max=100)])
    marca = fields.Str(validate=[validate.Length(max=100)])
    modelo = fields.Str(validate=[validate.Length(max=100)])
    origen = fields.Str(validate=[validate.Length(max=100)])
    foto = fields.Str()
    cantidad = fields.Integer()
    observaciones = fields.Str(validate=[validate.Length(max=250)])
    lugarId = fields.Integer()
    statusId= fields.Integer()
    pertenece = fields.Str(validate=[validate.Length(max=100)])
    descompostura = fields.Str(validate=[validate.Length(max=100)])
    costo = fields.Integer()
    lugar=fields.Nested(LugaresSchema)
    status = fields.Nested(StatusDevicesSchema)
    compra = fields.Str(validate=[validate.Length(max=100)])
    proveedor = fields.Str(validate=[validate.Length(max=100)])
    idMov = fields.Str(validate=[validate.Length(max=500)])
    serie = fields.Str( validate=[validate.Length(max=100)])
    accesorios = fields.Str( validate=[validate.Length(max=100)])
