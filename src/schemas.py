from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")


class LugaresBase(ORMBaseModel):
    id: Optional[int] = None
    lugar: Optional[str] = Field(default=None, max_length=100)
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None
    activo: Optional[bool] = None


class LugaresCreate(LugaresBase):
    lugar: str = Field(..., max_length=100)


class LugaresUpdate(LugaresBase):
    pass


class RolesBase(ORMBaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = Field(default=None, max_length=45)
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None


class RolesCreate(RolesBase):
    nombre: str = Field(..., max_length=45)


class RolesUpdate(RolesBase):
    pass


class EstatusUsuariosBase(ORMBaseModel):
    id: Optional[int] = None
    descripcion: Optional[str] = Field(default=None, max_length=45)
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None


class EstatusUsuariosCreate(EstatusUsuariosBase):
    descripcion: str = Field(..., max_length=45)


class EstatusUsuariosUpdate(EstatusUsuariosBase):
    id: Optional[int] = None
    descripcion: Optional[str] = Field(default=None, max_length=45)


class StatusDevicesBase(ORMBaseModel):
    id: Optional[int] = None
    descripcion: Optional[str] = Field(default=None, max_length=100)
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None


class StatusDevicesCreate(StatusDevicesBase):
    descripcion: str = Field(..., max_length=100)


class StatusDevicesUpdate(StatusDevicesBase):
    pass


class TipoMoveBase(ORMBaseModel):
    id: Optional[int] = None
    tipo: Optional[str] = Field(default=None, max_length=45)
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None


class TipoMoveCreate(TipoMoveBase):
    tipo: str = Field(..., max_length=45)


class TipoMoveUpdate(TipoMoveBase):
    id: Optional[int] = None
    tipo: Optional[str] = Field(default=None, max_length=45)


class UsuarioLogin(ORMBaseModel):
    username: str = Field(..., max_length=45)
    password: str


class UsuarioPasswordUpdate(ORMBaseModel):
    id: int
    username: str = Field(..., max_length=45)
    password: str


class UsuariosBase(ORMBaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = Field(default=None, max_length=45)
    username: Optional[str] = Field(default=None, max_length=45)
    apellidoPaterno: Optional[str] = Field(default=None, max_length=45)
    apellidoMaterno: Optional[str] = Field(default=None, max_length=45)
    password: Optional[str] = None
    telefono: Optional[str] = Field(default=None, max_length=45)
    correo: Optional[str] = Field(default=None, max_length=100)
    foto: Optional[str] = None
    rolId: Optional[int] = None
    statusId: Optional[int] = None
    rol: Optional[RolesBase] = None
    status: Optional[EstatusUsuariosBase] = None
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None


class UsuariosCreate(UsuariosBase):
    nombre: str = Field(..., max_length=45)
    username: str = Field(..., max_length=45)
    apellidoPaterno: str = Field(..., max_length=45)
    apellidoMaterno: str = Field(..., max_length=45)
    password: str
    telefono: str = Field(..., max_length=45)
    correo: str = Field(..., max_length=100)
    rolId: int
    statusId: int


class UsuariosUpdate(UsuariosBase):
    id: int


class UsuariosQuery(ORMBaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = Field(default=None, max_length=45)
    username: Optional[str] = Field(default=None, max_length=45)
    apellidoPaterno: Optional[str] = Field(default=None, max_length=45)
    apellidoMaterno: Optional[str] = Field(default=None, max_length=45)
    telefono: Optional[str] = Field(default=None, max_length=45)
    correo: Optional[str] = Field(default=None, max_length=100)
    rolId: Optional[int] = None
    statusId: Optional[int] = None


class DispositivosBase(ORMBaseModel):
    id: Optional[int] = None
    codigo: Optional[str] = Field(default=None, max_length=100)
    producto: Optional[str] = Field(default=None, max_length=100)
    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)
    origen: Optional[str] = Field(default=None, max_length=100)
    foto: Optional[str] = None
    cantidad: Optional[int] = None
    observaciones: Optional[str] = Field(default=None, max_length=250)
    lugarId: Optional[int] = None
    pertenece: Optional[str] = Field(default=None, max_length=100)
    descompostura: Optional[str] = Field(default=None, max_length=100)
    costo: Optional[int] = None
    compra: Optional[str] = Field(default=None, max_length=100)
    proveedor: Optional[str] = Field(default=None, max_length=100)
    idMov: Optional[str] = Field(default=None, max_length=500)
    statusId: Optional[int] = None
    lugar: Optional[LugaresBase] = None
    status: Optional[StatusDevicesBase] = None
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None
    serie: Optional[str] = Field(default=None, max_length=100)
    accesorios: Optional[str] = Field(default=None, max_length=100)


class DispositivosCreate(DispositivosBase):
    codigo: str = Field(..., max_length=100)
    producto: str = Field(..., max_length=100)
    marca: str = Field(..., max_length=100)
    modelo: str = Field(..., max_length=100)
    cantidad: int
    lugarId: int
    statusId: int


class DispositivosUpdate(DispositivosBase):
    id: int


class DispositivosQuery(ORMBaseModel):
    id: Optional[int] = None
    codigo: Optional[str] = Field(default=None, max_length=100)
    producto: Optional[str] = Field(default=None, max_length=100)
    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)
    origen: Optional[str] = Field(default=None, max_length=100)
    foto: Optional[str] = None
    cantidad: Optional[int] = None
    observaciones: Optional[str] = Field(default=None, max_length=250)
    lugarId: Optional[int] = None
    statusId: Optional[int] = None
    pertenece: Optional[str] = Field(default=None, max_length=100)
    descompostura: Optional[str] = Field(default=None, max_length=100)
    costo: Optional[int] = None
    lugar: Optional[LugaresBase] = None
    status: Optional[StatusDevicesBase] = None
    compra: Optional[str] = Field(default=None, max_length=100)
    proveedor: Optional[str] = Field(default=None, max_length=100)
    idMov: Optional[str] = Field(default=None, max_length=500)
    serie: Optional[str] = Field(default=None, max_length=100)
    accesorios: Optional[str] = Field(default=None, max_length=100)


class DispositivosSomeFields(ORMBaseModel):
    id: Optional[int] = None
    codigo: Optional[str] = Field(default=None, max_length=100)
    producto: Optional[str] = Field(default=None, max_length=100)
    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)
    origen: Optional[str] = Field(default=None, max_length=100)
    foto: Optional[str] = None
    cantidad: Optional[int] = None
    observaciones: Optional[str] = Field(default=None, max_length=250)
    lugarId: Optional[int] = None
    pertenece: Optional[str] = Field(default=None, max_length=45)
    descompostura: Optional[str] = Field(default=None, max_length=100)
    costo: Optional[int] = None
    compra: Optional[str] = Field(default=None, max_length=100)
    proveedor: Optional[str] = Field(default=None, max_length=100)
    idMov: Optional[str] = Field(default=None, max_length=500)
    statusId: Optional[int] = None
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None
    serie: Optional[str] = Field(default=None, max_length=100)
    accesorios: Optional[str] = Field(default=None, max_length=100)
    lugar: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=100)


class DispositivosCantity(ORMBaseModel):
    TotalAmount: Optional[float] = None


class ReportesBase(ORMBaseModel):
    id: Optional[int] = None
    dispositivoId: Optional[int] = None
    usuarioId: Optional[int] = None
    comentarios: Optional[str] = None
    foto: Optional[str] = None
    dispositivo: Optional[DispositivosBase] = None
    usuario: Optional[UsuariosBase] = None
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None


class ReportesCreate(ReportesBase):
    dispositivoId: int
    usuarioId: int


class ReportesUpdate(ReportesBase):
    id: int


class ReportesQuery(ORMBaseModel):
    id: Optional[int] = None
    dispositivoId: Optional[int] = None
    usuarioId: Optional[int] = None
    comentarios: Optional[str] = None
    foto: Optional[str] = Field(default=None, max_length=500)
    fechaAltaRangoInicio: Optional[date] = None
    fechaAltaRangoFin: Optional[date] = None


class MovimientosBase(ORMBaseModel):
    id: Optional[int] = None
    dispositivoId: Optional[int] = None
    usuarioId: Optional[int] = None
    idMovimiento: Optional[str] = None
    tipoMovId: Optional[int] = None
    comentarios: Optional[str] = Field(default=None, max_length=500)
    foto: Optional[str] = None
    foto2: Optional[str] = None
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None
    LugarId: Optional[int] = None
    lugar: Optional[LugaresBase] = None
    dispositivo: Optional[DispositivosBase] = None
    tipoMovimiento: Optional[TipoMoveBase] = None
    usuario: Optional[UsuariosBase] = None
    cantidad_Actual: Optional[int] = None


class MovimientosCreate(MovimientosBase):
    dispositivoId: int
    usuarioId: int
    idMovimiento: str
    tipoMovId: int
    LugarId: int


class MovimientosUpdate(MovimientosBase):
    id: int
    dispositivoId: int
    usuarioId: int
    idMovimiento: str
    tipoMovId: int
    LugarId: int


class MovimientosQuery(ORMBaseModel):
    id: Optional[int] = None
    dispositivoId: Optional[int] = None
    usuarioId: Optional[int] = None
    idMovimiento: Optional[str] = None
    tipoMovId: Optional[int] = None
    LugarId: Optional[int] = None
    fechaAltaRangoInicio: Optional[date] = None
    fechaAltaRangoFin: Optional[date] = None


class MovimientosSomeFields(ORMBaseModel):
    id: Optional[int] = None
    codigo: Optional[str] = Field(default=None, max_length=100)
    producto: Optional[str] = Field(default=None, max_length=100)
    fechaAlta: Optional[datetime] = None
    idMovimiento: Optional[str] = Field(default=None, max_length=200)
    lugar: Optional[str] = Field(default=None, max_length=100)
    tipo: Optional[str] = Field(default=None, max_length=100)
    nombre: Optional[str] = Field(default=None, max_length=100)
    username: Optional[str] = Field(default=None, max_length=100)


class JobMovimientosBase(ORMBaseModel):
    id: Optional[int] = None
    idMovimiento: Optional[str] = None
    usuarioId: Optional[int] = None
    tipoMovId: Optional[int] = None
    LugarId: Optional[int] = None
    comentarios: Optional[str] = None
    estado: Optional[str] = None
    status: Optional[int] = None
    fechaAlta: Optional[datetime] = None
    fechaUltimaModificacion: Optional[datetime] = None


class JobMovimientosCreate(JobMovimientosBase):
    usuarioId: int
    tipoMovId: int
    LugarId: int
    status: int


class JobMovimientosUpdate(JobMovimientosBase):
    id: int