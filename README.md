# API de Ventas (FastAPI + SQLite)

![API Banner](https://via.placeholder.com/800x200/1e40af/ffffff?text=FastAPI+%2B+SQLite+API)

## Descripción
API REST para gestionar clientes, productos, ventas y detalles de ventas. Incluye reportes de productos más vendidos y clientes con más ventas. La raíz `/` redirige a la documentación `/docs` (Swagger UI).

## Tecnologías
- FastAPI
- Uvicorn
- SQLAlchemy (ORM 2.x)
- SQLite
- Pydantic 2.x

## Requisitos y notas rápidas
- Python recomendado: 3.12 (Windows). Si usas 3.13 y tienes problemas de instalación, prueba con 3.12.
- La base de datos se crea como archivo `app.db` en el directorio del proyecto.
- Integridad referencial activada en SQLite (`PRAGMA foreign_keys=ON`).

## Instalación (Windows, sin entorno virtual)
Usa el launcher de Windows para asegurarte de usar Python 3.12.
```cmd
py -3.12 -m pip install -r requirements.txt
```

Si prefieres usar tu `pip` actual (bajo tu responsabilidad):
```cmd
pip install -r requirements.txt
```

## Ejecución
Inicia el servidor de desarrollo con recarga automática.
```cmd
py -3.12 -m uvicorn main:app --reload
```
Abre Swagger UI:
- http://127.0.0.1:8000/  (redirige a `/docs`)
- http://127.0.0.1:8000/docs

Para detener, presiona `Ctrl + C` en la terminal.

## Modelado
Tablas principales:
- `clientes`
- `productos`
- `ventas`
- `detalles_ventas`

Relaciones clave:
- `ventas.cliente_id -> clientes.id`
- `detalles_ventas.venta_id -> ventas.id`
- `detalles_ventas.producto_id -> productos.id`

`ventas.total` se recalcula automáticamente cuando se crean/actualizan/eliminan detalles.

## Endpoints

### Clientes
- POST `/clientes`
- GET `/clientes`
- GET `/clientes/{id}`
- PUT `/clientes/{id}`
- DELETE `/clientes/{id}`

### Productos
- POST `/productos`
- GET `/productos`
- GET `/productos/{id}`
- PUT `/productos/{id}`
- DELETE `/productos/{id}`

### Ventas
- POST `/ventas` (crea venta con lista de detalles)
- GET `/ventas`
- GET `/ventas/{id}`
- PUT `/ventas/{id}` (actualiza cabecera: p. ej. `cliente_id`)
- DELETE `/ventas/{id}`

Ejemplo cuerpo POST `/ventas`:
```json
{
  "cliente_id": 1,
  "detalles": [
    {"producto_id": 1, "precio": 1000, "descuento": 0, "cantidad": 2},
    {"producto_id": 2, "precio": 500, "descuento": 50, "cantidad": 1}
  ]
}
```

Ejemplo cuerpo PUT `/ventas/{id}` (solo cabecera, no modifica los detalles):
```json
{ "cliente_id": 2 }
```

### Detalles de Venta
- POST `/detalles` (crea un detalle suelto asociado a una venta)
- GET `/detalles`
- GET `/detalles/{id}`
- PUT `/detalles/{id}`
- DELETE `/detalles/{id}`
- GET `/ventas/{venta_id}/detalles` (lista detalles por venta)

Ejemplo cuerpo POST `/detalles` (creación standalone):
```json
{
  "venta_id": 1,
  "producto_id": 3,
  "precio": 1500,
  "descuento": 100,
  "cantidad": 2
}
```

Ejemplo cuerpo PUT `/detalles/{id}` (campos opcionales; al actualizar se recalcula el `total` de la venta):
```json
{
  "producto_id": 4,
  "precio": 1400,
  "descuento": 50,
  "cantidad": 3
}
```

### Reportes
- GET `/reportes/productos-mas-vendidos?limit=5`
- GET `/reportes/clientes-mas-ventas?limit=5`

Los reportes incluyen totales agregados (unidades y monto). Usa `limit` para limitar filas.

## Parámetros comunes
- `skip` y `limit` están disponibles en varios listados (por ejemplo, `/clientes`, `/productos`, `/ventas`, `/detalles`).

## Notas y buenas prácticas
- Los `UUID` se generan automáticamente en el backend y son informativos.
- `ventas.total` = suma de `(precio - descuento) * cantidad` de sus detalles.
- Si necesitas “resetear” la base, detén el servidor y elimina `app.db`.
  ```cmd
  del app.db
  ```
- Si usas otra versión de Python y aparece un error de compilación/instalación, vuelve a intentar con `py -3.12`.

## Checklist de verificación (tomado de la rúbrica)
- [ ] Exponer documentación Swagger en `/docs` (incluye todos los esquemas y endpoints)
- [ ] CRUD completo de `clientes` y `productos`
- [ ] CRUD completo de `ventas` (crear con detalles, obtener, actualizar cabecera, eliminar)
- [ ] CRUD completo de `detalles_ventas` (crear suelto, listar, obtener, actualizar, eliminar)
- [ ] Listado de detalles por venta (`/ventas/{venta_id}/detalles`)
- [ ] Recalcular `ventas.total` al crear/actualizar/eliminar detalles
- [ ] Reporte de productos más vendidos (`/reportes/productos-mas-vendidos`)
- [ ] Reporte de clientes con más ventas (`/reportes/clientes-mas-ventas`)
- [ ] Sin autenticación requerida
- [ ] Base URL `/` redirige a `/docs`

## Problemas comunes
- “No se encuentran imports” en VS Code: selecciona el intérprete Python 3.12 (barra de estado inferior izquierda) y/o reinicia la ventana.
- Error al instalar dependencias en 3.13: usa `py -3.12 -m pip install -r requirements.txt`.

## Licencia

![MIT License](https://via.placeholder.com/400x100/28a745/ffffff?text=MIT+License)

# Released under MIT License

Copyright (c) 2013 Mark Otto.

Copyright (c) 2017 Andrew Fong.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


