""" 
Punto de entrada de la API.

Este módulo crea la aplicación FastAPI, inicializa las tablas
y define las rutas para CRUD y reportes.
No se implementa autenticación según los requisitos de la consigna.

Swagger/OpenAPI se expone automáticamente en `/docs` y Redoc en `/redoc`.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from database import Base, engine, get_db
import models
import crud
import schemas

# Crear tablas al iniciar la aplicación.
# En un entorno productivo se usarían migraciones (Alembic), pero aquí basta.

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Ventas", version="1.0.0", description="CRUD de clientes, productos y ventas con reportes básicos.")

# Ruta raíz: redirige a la documentación
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# ---------------------- Clientes ----------------------

@app.post("/clientes", response_model=schemas.ClienteOut, status_code=status.HTTP_201_CREATED, summary="Crear cliente")
def crear_cliente(data: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """ Crea un nuevo cliente. """
    return crud.create_cliente(db, data)

@app.get("/clientes", response_model=List[schemas.ClienteOut], summary="Listar clientes")
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ Lista clientes con paginación simple usando `skip` y `limit`. """
    return crud.list_clientes(db, skip, limit)

@app.get("/clientes/{cliente_id}", response_model=schemas.ClienteOut, summary="Obtener cliente")
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """ Devuelve un cliente por su identificador interno. """
    cliente = crud.get_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{cliente_id}", response_model=schemas.ClienteOut, summary="Actualizar cliente")
def actualizar_cliente(cliente_id: int, data: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    """ Actualiza parcialmente un cliente (solo campos enviados). """
    cliente = crud.update_cliente(db, cliente_id, data)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar cliente")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """ Elimina un cliente si existe. """
    ok = crud.delete_cliente(db, cliente_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return None

# ---------------------- Productos ----------------------

@app.post("/productos", response_model=schemas.ProductoOut, status_code=status.HTTP_201_CREATED, summary="Crear producto")
def crear_producto(data: schemas.ProductoCreate, db: Session = Depends(get_db)):
    """ Crea un nuevo producto. """
    return crud.create_producto(db, data)

@app.get("/productos", response_model=List[schemas.ProductoOut], summary="Listar productos")
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ Lista productos con paginación simple usando `skip` y `limit`. """
    return crud.list_productos(db, skip, limit)

@app.get("/productos/{producto_id}", response_model=schemas.ProductoOut, summary="Obtener producto")
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """ Devuelve un producto por su identificador interno. """
    producto = crud.get_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.put("/productos/{producto_id}", response_model=schemas.ProductoOut, summary="Actualizar producto")
def actualizar_producto(producto_id: int, data: schemas.ProductoUpdate, db: Session = Depends(get_db)):
    """ Actualiza parcialmente un producto (solo campos enviados). """
    producto = crud.update_producto(db, producto_id, data)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar producto")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """ Elimina un producto si existe. """
    ok = crud.delete_producto(db, producto_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None

# ---------------------- Ventas ----------------------

@app.post("/ventas", response_model=schemas.VentaOut, status_code=status.HTTP_201_CREATED, summary="Crear venta")
def crear_venta(data: schemas.VentaCreate, db: Session = Depends(get_db)):
    """ Crea una nueva venta. """
    return crud.create_venta(db, data)

@app.get("/ventas", response_model=List[schemas.VentaOut], summary="Listar ventas")
def listar_ventas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ Lista ventas con paginación simple usando `skip` y `limit`. """
    return crud.list_ventas(db, skip, limit)

@app.get("/ventas/{venta_id}", response_model=schemas.VentaOut, summary="Obtener venta")
def obtener_venta(venta_id: int, db: Session = Depends(get_db)):
    """ Devuelve una venta por su identificador interno. """
    venta = crud.get_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@app.delete("/ventas/{venta_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar venta")
def eliminar_venta(venta_id: int, db: Session = Depends(get_db)):
    """ Elimina una venta si existe. """
    ok = crud.delete_venta(db, venta_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return None

@app.put("/ventas/{venta_id}", response_model=schemas.VentaOut, summary="Actualizar cabecera de venta")
def actualizar_venta(venta_id: int, data: schemas.VentaUpdate, db: Session = Depends(get_db)):
    venta = crud.update_venta(db, venta_id, data)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

# ---------------------- Detalles de ventas ----------------------

@app.post("/detalles", response_model=schemas.DetalleVentaOut, status_code=status.HTTP_201_CREATED, summary="Crear detalle (venta existente)")
def crear_detalle(data: schemas.DetalleVentaCreateStandalone, db: Session = Depends(get_db)):
    return crud.create_detalle(db, data)

@app.get("/detalles/{detalle_id}", response_model=schemas.DetalleVentaOut, summary="Obtener detalle")
def obtener_detalle(detalle_id: int, db: Session = Depends(get_db)):
    det = crud.get_detalle(db, detalle_id)
    if not det:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return det

@app.put("/detalles/{detalle_id}", response_model=schemas.DetalleVentaOut, summary="Actualizar detalle")
def actualizar_detalle(detalle_id: int, data: schemas.DetalleVentaUpdate, db: Session = Depends(get_db)):
    det = crud.update_detalle(db, detalle_id, data)
    if not det:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return det

@app.delete("/detalles/{detalle_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar detalle")
def eliminar_detalle(detalle_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_detalle(db, detalle_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Detalle no encontrado")
    return None

@app.get("/detalles", response_model=List[schemas.DetalleVentaOut], summary="Listar detalles")
def listar_detalles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_detalles(db, skip, limit)

@app.get("/ventas/{venta_id}/detalles", response_model=List[schemas.DetalleVentaOut], summary="Listar detalles por venta")
def listar_detalles_por_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = crud.get_venta(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    # devolver detalles asociados
    return venta.detalles

# ---------------------- Reportes ----------------------

@app.get("/reportes/productos-mas-vendidos", summary="Ranking de productos más vendidos")
def reporte_productos(limit: int = 10, db: Session = Depends(get_db)):
    """ Devuelve un ranking de los productos más vendidos. """
    rows = crud.productos_mas_vendidos(db, limit)
    return [
        {
            "producto_id": r.producto_id,
            "nombre": r.nombre,
            "total_cantidad": r.total_cantidad,
            "total_ingresos": r.total_ingresos,
        }
        for r in rows
    ]

@app.get("/reportes/clientes-mas-ventas", summary="Ranking de clientes con más ventas")
def reporte_clientes(limit: int = 10, db: Session = Depends(get_db)):
    """ Devuelve un ranking de los clientes con más ventas. """
    rows = crud.clientes_con_mas_ventas(db, limit)
    return [
        {
            "cliente_id": r.cliente_id,
            "nombre": r.nombre,
            "total_ventas": r.total_ventas,
            "total_monto": r.total_monto,
        }
        for r in rows
    ]
