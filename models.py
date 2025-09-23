"""
Modelos ORM para la aplicación de ventas.

Cada clase representa una tabla en la base de datos SQLite. Se definen relaciones
bidireccionales para facilitar el acceso a datos asociados (por ejemplo `cliente.ventas`
ó `venta.detalles`). Las marcas de tiempo se gestionan con valores por defecto y
`onupdate` para `modified_at`.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Cliente(Base):
    """
    Tabla de clientes.

    Campos clave:
    - `uuid`: identificador externo (no incremental) útil para exponer públicamente.
    - `rut` y `email` marcados como únicos para evitar duplicados.
    """
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    rut = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación 1:N (un cliente tiene muchas ventas)
    ventas = relationship("Venta", back_populates="cliente", cascade="all, delete-orphan")


class Producto(Base):
    """ Tabla de productos disponibles para la venta. """
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    categoria = Column(String, index=True)
    precio = Column(Integer, nullable=False)  # Precio base unitario
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con detalles de ventas en que aparece este producto
    detalles = relationship("DetalleVenta", back_populates="producto")


class Venta(Base):
    """
    Tabla de ventas (cabecera).

    Almacena el total calculado y la referencia al cliente. Los detalles
    se encuentran en la tabla `detalles_ventas`.
    """
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    total = Column(Integer, default=0)  # Se actualizará al crear los detalles
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    cliente = relationship("Cliente", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")


class DetalleVenta(Base):
    """
    Detalle de cada producto incluido en una venta.

    Guarda el precio aplicado (que puede ser diferente al precio actual del
    producto para mantener historicidad), un posible descuento unitario y la
    cantidad. Permite recrear exactamente el valor de la venta en su momento.
    """
    __tablename__ = "detalles_ventas"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    precio = Column(Integer, nullable=False)
    descuento = Column(Integer, default=0)
    cantidad = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    producto = relationship("Producto", back_populates="detalles")
    venta = relationship("Venta", back_populates="detalles")
