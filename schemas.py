"""Esquemas Pydantic (serialización / validación).

Se separan los modelos de entrada (Create / Update) de los de salida (Out) para
controlar qué campos expone la API y cuáles se reciben del cliente. Las clases
`Base` agrupan atributos comunes.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# --------- Cliente ---------
class ClienteBase(BaseModel):
    """Campos compartidos entre creación y lectura de un cliente."""
    nombre: str
    email: EmailStr
    rut: str

class ClienteCreate(ClienteBase):
    """Modelo de entrada para crear un cliente.
    (No incluye campos autogenerados como `id`, `uuid` o timestamps.)
    """
    pass

class ClienteUpdate(BaseModel):
    """Modelo de entrada para actualización parcial (PUT o PATCH)."""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rut: Optional[str] = None

class ClienteOut(ClienteBase):
    """Representación de salida de un cliente."""
    id: int
    uuid: str
    created_at: datetime
    modified_at: datetime
    class Config:
        from_attributes = True  # Permite crear a partir de modelos ORM

# --------- Producto ---------
class ProductoBase(BaseModel):
    """Campos comunes de un producto."""
    nombre: str
    categoria: Optional[str] = None
    precio: int

class ProductoCreate(ProductoBase):
    """Entrada para crear producto."""
    pass

class ProductoUpdate(BaseModel):
    """Entrada para actualizar parcialmente un producto."""
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[int] = None

class ProductoOut(ProductoBase):
    """Salida de producto con metadatos."""
    id: int
    uuid: str
    created_at: datetime
    modified_at: datetime
    class Config:
        from_attributes = True

# --------- Venta y Detalle ---------
class DetalleVentaBase(BaseModel):
    """Campos básicos que describen un detalle de venta."""
    producto_id: int
    precio: int
    descuento: int = 0
    cantidad: int = 1

class DetalleVentaCreate(DetalleVentaBase):
    """Entrada para crear un detalle dentro de una venta."""
    pass

class DetalleVentaCreateStandalone(DetalleVentaBase):
    """Entrada para crear un detalle fuera del flujo de creación de venta.

    Requiere referenciar una venta existente mediante `venta_id`.
    """
    venta_id: int

class DetalleVentaUpdate(BaseModel):
    """Entrada para actualizar parcialmente un detalle de venta."""
    precio: Optional[int] = None
    descuento: Optional[int] = None
    cantidad: Optional[int] = None

class DetalleVentaOut(DetalleVentaBase):
    """Salida de un detalle con identificadores y timestamps."""
    id: int
    uuid: str
    venta_id: int
    created_at: datetime
    modified_at: datetime
    class Config:
        from_attributes = True

class VentaBase(BaseModel):
    """Campos base de una venta (cabecera)."""
    cliente_id: int

class VentaCreate(VentaBase):
    """Entrada para crear una venta completa con sus detalles."""
    detalles: List[DetalleVentaCreate]

class VentaUpdate(BaseModel):
    """Actualización parcial de la cabecera de una venta."""
    cliente_id: Optional[int] = None

class VentaOut(VentaBase):
    """Salida de venta incluyendo detalles ya calculados."""
    id: int
    uuid: str
    fecha: datetime
    total: int
    created_at: datetime
    modified_at: datetime
    detalles: List[DetalleVentaOut] = []
    class Config:
        from_attributes = True

# --------- Reportes ---------
class ProductoMasVendido(BaseModel):
    """Fila de reporte para el ranking de productos más vendidos."""
    producto_id: int
    nombre: str
    total_cantidad: int
    total_ingresos: int

class ClienteConMasVentas(BaseModel):
    """Fila de reporte para clientes con mayor número de ventas."""
    cliente_id: int
    nombre: str
    total_ventas: int  # número de ventas
    total_monto: int   # suma de los totales de ventas
