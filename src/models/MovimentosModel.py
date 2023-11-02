
from enum import unique
from pkgutil import ModuleInfo
from marshmallow import fields, Schema, validate
import datetime
from sqlalchemy import desc
import sqlalchemy
from . import db
from sqlalchemy import Date,cast
from .LugaresModel import LugaresSchema,LugaresModel
from .DispositivosModel import DispositivosSchema,DispositivosModel
from .UsuariosModel import UsuariosModel, UsuariosSchema
from .TipoMovimientosModel import TipoMoveModel, TipoMoveSchema
from sqlalchemy import or_
from sqlalchemy.orm import aliased
class MovimientosModel(db.Model):
    """
    Catalogo Model
    """
    
    __tablename__ = 'invMovimientos'

    id = db.Column(db.Integer, primary_key=True)
    idMovimiento = db.Column(db.Text)
    dispositivoId = db.Column(
        db.Integer,db.ForeignKey("invDispositivos.id"),nullable=False
    )
    usuarioId = db.Column(
        db.Integer,db.ForeignKey("invUsuarios.id"),nullable=False
    )
    
    tipoMovId = db.Column(
        db.Integer,db.ForeignKey("invTipoMoves.id"),nullable=False
    )
    LugarId = db.Column(
        db.Integer,db.ForeignKey("invLugares.id"),nullable=False
    )
    comentarios = db.Column(db.Text)
    foto = db.Column(db.Text)
    foto2 = db.Column(db.Text)
    fechaAlta = db.Column(db.DateTime)
    fechaUltimaModificacion = db.Column(db.DateTime)
    cantidad_Actual=db.Column(db.Integer,default=0)
    lugar=db.relationship(
         "LugaresModel",backref=db.backref("invLugares2",lazy=True)
    )

  
    usuario=db.relationship(
         "UsuariosModel",backref=db.backref("invUsuarios2",lazy=True)
    )

    dispositivo=db.relationship(
         "DispositivosModel",backref=db.backref("invDispositivos2",lazy=True)
    )

    tipoMovimiento=db.relationship(
         "TipoMoveModel",backref=db.backref("invTipoMoves2",lazy=True)
    )

    def __init__(self, data):
        """
        Class constructor
        """
        self.idMovimiento = data.get("idMovimiento")
        self.dispositivoId = data.get("dispositivoId")
        self.usuarioId = data.get("usuarioId")
        self.tipoMovId = data.get("tipoMovId")
        self.comentarios = data.get("comentarios")
        self.foto = data.get("foto")
        self.foto2 = data.get("foto2")
        self.LugarId = data.get("LugarId")
        self.fechaAlta = datetime.datetime.utcnow()
        self.fechaUltimaModificacion = datetime.datetime.utcnow()
        self.cantidad_Actual=data.get("cantidad_Actual")

    def save(self):
        db.session.add(self)
        db.session.commit()


    @staticmethod
    def guardar_masivo(listMovements):
        db.session.bulk_save_objects(listMovements)
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
    def get_all_movimientos(offset=1,limit=10):
        return MovimientosModel.query.order_by(MovimientosModel.fechaAlta.desc()).paginate(page=offset,per_page=limit,error_out=False)
    
    @staticmethod
    def get_all_movimientos_somefields(offset=1,limit=10):
        result = db.session.query(MovimientosModel).select_from(MovimientosModel).with_entities(
            MovimientosModel.id,
            MovimientosModel.fechaAlta,
            DispositivosModel.producto,
            MovimientosModel.idMovimiento,
            UsuariosModel.nombre,
            LugaresModel.lugar,
            TipoMoveModel.tipo
        ).join(DispositivosModel).join(UsuariosModel).join(
            LugaresModel,LugaresModel.id == MovimientosModel.LugarId
        ).join(TipoMoveModel).order_by(MovimientosModel.fechaAlta.desc()).paginate(page=offset,per_page=limit,error_out=False)


        return result,result.total

    @staticmethod
    def get_all_movimientos_by_like_new_query(value,offset=1,limit=30):


        result = db.session.query(MovimientosModel).select_from(MovimientosModel).with_entities(
            MovimientosModel.id,
            MovimientosModel.fechaAlta,
            DispositivosModel.producto,
            MovimientosModel.idMovimiento,
            UsuariosModel.nombre,
            LugaresModel.lugar,
            TipoMoveModel.tipo
        ).join(DispositivosModel).join(UsuariosModel).join(
            LugaresModel,LugaresModel.id == MovimientosModel.LugarId
        ).join(TipoMoveModel).filter(
                or_(DispositivosModel.codigo.ilike(f'%{value}%') ,
                    DispositivosModel.producto.ilike(f'%{value}%') ,
                    DispositivosModel.marca.ilike(f'%{value}%') ,
                    DispositivosModel.modelo.ilike(f'%{value}%') ,
                    DispositivosModel.serie.ilike(f'%{value}%') ,
                    DispositivosModel.accesorios.ilike(f'%{value}%'),
                    MovimientosModel.idMovimiento.ilike(f'%{value}%'),
                    UsuariosModel.nombre.ilike(f'%{value}%'),
                    TipoMoveModel.tipo.ilike(f'%{value}%'))).order_by(MovimientosModel.fechaAlta.desc()).paginate(page=offset,per_page=limit,error_out=False)


        return result,result.total
        

    @staticmethod
    def get_all_movimientos_by_like(value,offset=1,limit=10):
        lugares=[]
        devices=[]
        users=[]

        lugar = LugaresModel.get_lugar_by_like(value,offset=1,limit=100)
        
        if len(lugar.items)!=0:
            for x in lugar.items:
                lugares.append(x.id)
        
        device = DispositivosModel.get_device_by_codigo_like_entity(value,offset=1,limit=100)
        
        if len(device.items)!=0:
            for x in device.items:
                devices.append(x.id)
        
        user = UsuariosModel.get_user_by_params_like_entity(value,offset=1,limit=100)
        
        if len(user.items)!=0:
            for x in user.items:
                users.append(x.id)

     
        result = MovimientosModel.query.filter(or_(MovimientosModel.usuarioId.in_(users),MovimientosModel.dispositivoId.in_(devices),MovimientosModel.LugarId.in_(lugares), MovimientosModel.idMovimiento.ilike(f'%{value}%'))).order_by(MovimientosModel.id).paginate(page=offset,per_page=limit,error_out=False) 
        return result


    @staticmethod
    def get_one_movimiento(id):
        return MovimientosModel.query.get(id)

    @staticmethod
    def get_lastone_movimiento(id):
       
        return MovimientosModel.query.filter_by(dispositivoId=id,tipoMovId=1).order_by(MovimientosModel.fechaAlta.desc()).first()


    @staticmethod
    def get_movimientos_by_query(jsonFiltros,offset=1,limit=5):
        #return DispositivosModel.query.filter_by(**jsonFiltros).paginate(page=offset,per_page=limit,error_out=False)
        #return MovimientosModel.query.filter_by(**jsonFiltros).order_by(MovimientosModel.id).paginate(page=offset,per_page=limit,error_out=False) 


        if "fechaAltaRangoInicio" in jsonFiltros and "fechaAltaRangoFin" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            end = jsonFiltros["fechaAltaRangoFin"]
            del jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoFin"]
            alta = alta+"T00:00:00.000"
            end = end + "T23:59:59.999"
            return MovimientosModel.query.filter_by(**jsonFiltros).filter(MovimientosModel.fechaAlta >= alta).order_by(MovimientosModel.id).filter(MovimientosModel.fechaAlta <= end).paginate(page=offset,per_page=limit,error_out=False)
        
        elif "fechaAltaRangoInicio" in jsonFiltros:
            alta = jsonFiltros["fechaAltaRangoInicio"]
            del jsonFiltros["fechaAltaRangoInicio"]
            return MovimientosModel.query.filter_by(**jsonFiltros).filter(cast(MovimientosModel.fechaAlta,Date) == alta).order_by(MovimientosModel.id).paginate(page=offset,per_page=limit,error_out=False)
        
        else:
            return MovimientosModel.query.filter_by(**jsonFiltros).order_by(MovimientosModel.id).paginate(page=offset,per_page=limit,error_out=False)

    def __repr(self):
        return '<id {}>'.format(self.id)




    @staticmethod
    def get_movements_by_like_someFields(value,offset=1,limit=100):

        # LugarAlias = aliased(LugaresModel)
        # result = MovimientosModel.query.with_entities(
        #         MovimientosModel.idMovimiento,
        #         MovimientosModel.fechaAlta,
        #         DispositivosModel.codigo,
        #         DispositivosModel.producto,
        #         UsuariosModel.nombre,
        #         TipoMoveModel.tipo
        #         ).join(DispositivosModel
        #         ).join(UsuariosModel
        #         ).join(TipoMoveModel
        #         ).join(LugarAlias, LugarAlias.id == MovimientosModel.LugarId
        #         ).filter(
        #             or_(MovimientosModel.idMovimiento.ilike(f'%{value}%'),
        #             DispositivosModel.codigo.ilike(f'%{value}%'),
        #             DispositivosModel.producto.ilike(f'%{value}%'),
        #             UsuariosModel.nombre.ilike(f'%{value}%'),
        #             UsuariosModel.username.ilike(f'%{value}%'),
        #             TipoMoveModel.tipo.ilike(f'%{value}%'),
        #             LugarAlias.lugar.ilike(f'%{value}%'),
        #             TipoMoveModel.fechaAlta.ilike(f'%{value}%'))).order_by(MovimientosModel.id).paginate(page=offset,per_page=limit,error_out=False)

        # result = MovimientosModel.query(
        #         MovimientosModel.idMovimiento,
        #         MovimientosModel.fechaAlta,
        #         DispositivosModel.codigo,
        #         DispositivosModel.producto,
        #         UsuariosModel.nombre,
        #         TipoMoveModel.tipo,
        #         MovimientosModel.LugarId
        #         #func.group_concat(func.distinct(LugarAlias.lugar)).label('lugarMov')
        #         ).join(DispositivosModel
        #         ).join(UsuariosModel
        #         ).join(TipoMoveModel
        #         ).join(LugaresModel, LugaresModel.id == MovimientosModel.LugarId
        #         ).filter(
        #             or_(MovimientosModel.idMovimiento.ilike(f'%{value}%'),
        #             DispositivosModel.codigo.ilike(f'%{value}%'),
        #             DispositivosModel.producto.ilike(f'%{value}%'),
        #             UsuariosModel.nombre.ilike(f'%{value}%'),
        #             UsuariosModel.username.ilike(f'%{value}%'),
        #             TipoMoveModel.tipo.ilike(f'%{value}%'),
        #             LugaresModel.lugar.ilike(f'%{value}%'),
        #             TipoMoveModel.fechaAlta.ilike(f'%{value}%'))).order_by(MovimientosModel.id).paginate(page=offset,per_page=limit,error_out=False)
        if offset<0:
            offset=0
        
        query = "select idMovimiento,codigo,producto,lugar,tipo,nombre,username,invMovimientos.fechaAlta from invMovimientos inner join invDispositivos on invMovimientos.dispositivoId = invDispositivos.id inner join invLugares on invMovimientos.LugarId = invLugares.id inner join invTipoMoves on invMovimientos.tipoMovId = invTipoMoves.id inner join invUsuarios on invMovimientos.usuarioId = invUsuarios.id where codigo like '%"+value+"%' or producto like '%"+value+"%' or lugar like '%"+value+"%' or nombre like '%"+value+"%' or idMovimiento like '%"+value+"%' order by invMovimientos.id asc offset " +str(offset-1)+ " rows fetch next "+str(limit)+" rows only"
        result = db.session.execute(query)
        listOutput = []
        if result:
            for res in result:
                print(res)
                output={}
                output['idMovimiento']=res[0]
                output['codigo']=res[1]
                output['producto']=res[2]
                output['lugar']=res[3]
                output['tipo']=res[4]
                output['nombre']=res[5]
                output['username']=res[6]
                output['fechaAlta']=res[7]

                listOutput.append(output)
        else:
            return listOutput
        
        return listOutput



class MovimientosSchema(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    dispositivoId = fields.Integer(required=True)
    usuarioId = fields.Integer(required=True)
    idMovimiento = fields.Str(required=True)  
    tipoMovId = fields.Integer(required=True)
    comentarios =fields.Str( validate=[validate.Length(max=500)])
    foto = fields.Str()
    foto2 = fields.Str()
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()
    LugarId = fields.Integer(required=True)
    lugar=fields.Nested(LugaresSchema)
    dispositivo=fields.Nested(DispositivosSchema)
    tipoMovimiento=fields.Nested(TipoMoveSchema)
    usuario = fields.Nested(UsuariosSchema)
    cantidad_Actual = fields.Integer(required=False)
    


class MovimientosSchemaUpdate(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int(required=True)
    dispositivoId = fields.Integer(required=True)
    usuarioId = fields.Integer(required=True)
    idMovimiento = fields.Str(required=True)
    tipoMovId = fields.Integer(required=True)
    comentarios =fields.Str( validate=[validate.Length(max=500)])
    foto = fields.Str()
    foto2 = fields.Str()
    LugarId = fields.Integer(required=True)
    fechaAlta = fields.DateTime()
    fechaUltimaModificacion = fields.DateTime()


class MovimientosSchemaQuery(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    dispositivoId = fields.Integer()
    usuarioId = fields.Integer()
    idMovimiento = fields.Str(required=True)
    tipoMovId = fields.Integer(required=True)
    LugarId = fields.Integer(required=True)
    fechaAltaRangoInicio=fields.Date()
    fechaAltaRangoFin=fields.Date()


class MovimientosSchemaSomeFields(Schema):
    """
    Catalogo Schema
    """
    id = fields.Int()
    codigo = fields.Str(required=True, validate=[validate.Length(max=100)])
    producto = fields.Str(required=True, validate=[validate.Length(max=100)])

    fechaAlta = fields.DateTime()
  
    idMovimiento = fields.Str( validate=[validate.Length(max=200)])
    lugar = fields.Str( validate=[validate.Length(max=100)])
    tipo = fields.Str( validate=[validate.Length(max=100)])
    nombre = fields.Str( validate=[validate.Length(max=100)])
    username = fields.Str( validate=[validate.Length(max=100)])
  