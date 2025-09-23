"""
Funciones CRUD y de reporte.

Este módulo encapsula la lógica de acceso a datos y generación de reportes para
mantener los endpoints (`main.py`) limpios. Cada función recibe una sesión de
SQLAlchemy (`Session`) inyectada por FastAPI a través de la dependencia `get_db`.

Diseño elegido:
- Cada operación devuelve el modelo ORM (cuando aplica) para que FastAPI lo
  serialice mediante los esquemas Pydantic configurados con `from_attributes`.
- Funciones de reportes retornan filas agregadas (tuplas nombradas) que luego
  se transforman en dict en las rutas.
"""

from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Cliente, Producto, Venta, DetalleVenta
from schemas import (
    ClienteCreate, ClienteUpdate,
    ProductoCreate, ProductoUpdate,
    VentaCreate, VentaUpdate,
    DetalleVentaCreateStandalone, DetalleVentaUpdate
)

# -------------------- Clientes --------------------

def create_cliente(db: Session, data: ClienteCreate) -> Cliente:
    """ Crear un nuevo cliente. """
    cliente = Cliente(
        uuid=str(uuid4()),
        nombre=data.nombre,
        email=data.email,
        rut=data.rut,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente

def get_cliente(db: Session, cliente_id: int) -> Optional[Cliente]:
    """ Obtener cliente por ID (o None si no existe). """
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()

def list_clientes(db: Session, skip: int = 0, limit: int = 100) -> List[Cliente]:
    """ Listar clientes con paginación simple (offset/limit). """
    return db.query(Cliente).offset(skip).limit(limit).all()

def update_cliente(db: Session, cliente_id: int, data: ClienteUpdate) -> Optional[Cliente]:
    """
    Actualizar parcialmente un cliente.

    Solo se modifican los campos presentes (exclude_unset). Si no existe, retorna None.
    """
    
    cliente = get_cliente(db, cliente_id)
    if not cliente:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return cliente

def delete_cliente(db: Session, cliente_id: int) -> bool:
    """ Eliminar un cliente. Devuelve True si se borró, False si no existía. """
    cliente = get_cliente(db, cliente_id)
    if not cliente:
        return False
    db.delete(cliente)
    db.commit()
    return True

# -------------------- Productos --------------------

def create_producto(db: Session, data: ProductoCreate) -> Producto:
    """ Crear producto. """
    producto = Producto(
        uuid=str(uuid4()),
        nombre=data.nombre,
        categoria=data.categoria,
        precio=data.precio,
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto

def get_producto(db: Session, producto_id: int) -> Optional[Producto]:
    """ Obtener producto por ID. """
    return db.query(Producto).filter(Producto.id == producto_id).first()

def list_productos(db: Session, skip: int = 0, limit: int = 100) -> List[Producto]:
    """ Listar productos con paginación simple. """
    return db.query(Producto).offset(skip).limit(limit).all()

def update_producto(db: Session, producto_id: int, data: ProductoUpdate) -> Optional[Producto]:
    """ Actualizar parcialmente un producto existente. """
    producto = get_producto(db, producto_id)
    if not producto:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(producto, field, value)
    db.commit()
    db.refresh(producto)
    return producto

def delete_producto(db: Session, producto_id: int) -> bool:
    """ Eliminar producto. True si se eliminó, False si no existía. """
    producto = get_producto(db, producto_id)
    if not producto:
        return False
    db.delete(producto)
    db.commit()
    return True

# -------------------- Ventas --------------------

def create_venta(db: Session, data: VentaCreate) -> Venta:
    """
    Crear una venta con sus detalles.

    Flujo:
    1. Se crea la cabecera (Venta) para obtener su ID.
    2. Se calculan subtotales de cada detalle: `(precio - descuento) * cantidad`.
    3. Se suman al total y se insertan los registros en `detalles_ventas`.
    """
    
    venta = Venta(
        uuid=str(uuid4()),
        cliente_id=data.cliente_id,
    )
    db.add(venta)
    db.flush()  # Obtenemos ID antes de crear detalles

    total = 0
    for det in data.detalles:
        subtotal = (det.precio - det.descuento) * det.cantidad
        total += subtotal
        detalle = DetalleVenta(
            uuid=str(uuid4()),
            producto_id=det.producto_id,
            venta_id=venta.id,
            precio=det.precio,
            descuento=det.descuento,
            cantidad=det.cantidad,
        )
        db.add(detalle)
    venta.total = total  # Se persiste al hacer commit

    db.commit()
    db.refresh(venta)
    return venta

def get_venta(db: Session, venta_id: int) -> Optional[Venta]:
    """ Obtener venta por ID. """
    return db.query(Venta).filter(Venta.id == venta_id).first()

def list_ventas(db: Session, skip: int = 0, limit: int = 100) -> List[Venta]:
    """ Listar ventas (sin filtros adicionales). """
    return db.query(Venta).offset(skip).limit(limit).all()

def delete_venta(db: Session, venta_id: int) -> bool:
    """ Eliminar venta (cascade elimina detalles). """
    venta = get_venta(db, venta_id)
    if not venta:
        return False
    db.delete(venta)
    db.commit()
    return True

def update_venta(db: Session, venta_id: int, data: VentaUpdate) -> Optional[Venta]:
    """Actualizar parcialmente la cabecera de una venta."""
    venta = get_venta(db, venta_id)
    if not venta:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(venta, field, value)
    db.commit()
    db.refresh(venta)
    return venta

# -------------------- Reportes --------------------

def productos_mas_vendidos(db: Session, limit: int = 10):
    """
    Ranking de productos ordenados por cantidad total vendida.
    
    También retorna el total de ingresos generados considerando descuentos.
    """
    
    q = (
        db.query(
            DetalleVenta.producto_id.label("producto_id"),
            Producto.nombre.label("nombre"),
            func.sum(DetalleVenta.cantidad).label("total_cantidad"),
            func.sum((DetalleVenta.precio - DetalleVenta.descuento) * DetalleVenta.cantidad).label("total_ingresos"),
        )
        .join(Producto, Producto.id == DetalleVenta.producto_id)
        .group_by(DetalleVenta.producto_id, Producto.nombre)
        .order_by(func.sum(DetalleVenta.cantidad).desc())
        .limit(limit)
    )
    return q.all()

def clientes_con_mas_ventas(db: Session, limit: int = 10):
    """ Ranking de clientes por número de ventas y monto total. """
    q = (
        db.query(
            Venta.cliente_id.label("cliente_id"),
            Cliente.nombre.label("nombre"),
            func.count(Venta.id).label("total_ventas"),
            func.sum(Venta.total).label("total_monto"),
        )
        .join(Cliente, Cliente.id == Venta.cliente_id)
        .group_by(Venta.cliente_id, Cliente.nombre)
        .order_by(func.count(Venta.id).desc())
        .limit(limit)
    )
    return q.all()

# -------------------- Detalles de venta --------------------

def _recalcular_total_venta(db: Session, venta_id: int) -> None:
    """Recalcula el total de una venta a partir de sus detalles."""
    suma = (
        db.query(
            func.coalesce(
                func.sum((DetalleVenta.precio - DetalleVenta.descuento) * DetalleVenta.cantidad),
                0,
            )
        )
        .filter(DetalleVenta.venta_id == venta_id)
        .scalar()
    )
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if venta:
        venta.total = int(suma or 0)
        db.flush()

def create_detalle(db: Session, data: DetalleVentaCreateStandalone) -> DetalleVenta:
    """Crear un detalle para una venta existente y actualizar el total."""
    detalle = DetalleVenta(
        uuid=str(uuid4()),
        producto_id=data.producto_id,
        venta_id=data.venta_id,
        precio=data.precio,
        descuento=data.descuento,
        cantidad=data.cantidad,
    )
    db.add(detalle)
    db.flush()
    _recalcular_total_venta(db, data.venta_id)
    db.commit()
    db.refresh(detalle)
    return detalle

def get_detalle(db: Session, detalle_id: int) -> Optional[DetalleVenta]:
    return db.query(DetalleVenta).filter(DetalleVenta.id == detalle_id).first()

def update_detalle(db: Session, detalle_id: int, data: DetalleVentaUpdate) -> Optional[DetalleVenta]:
    det = get_detalle(db, detalle_id)
    if not det:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(det, field, value)
    db.flush()
    _recalcular_total_venta(db, det.venta_id)
    db.commit()
    db.refresh(det)
    return det

def delete_detalle(db: Session, detalle_id: int) -> bool:
    det = get_detalle(db, detalle_id)
    if not det:
        return False
    venta_id = det.venta_id
    db.delete(det)
    db.flush()
    _recalcular_total_venta(db, venta_id)
    db.commit()
    return True

def list_detalles(db: Session, skip: int = 0, limit: int = 100) -> List[DetalleVenta]:
    return db.query(DetalleVenta).offset(skip).limit(limit).all()
