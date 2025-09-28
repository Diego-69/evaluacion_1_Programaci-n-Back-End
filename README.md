# API de Ventas (FastAPI + SQLite)

![Banner API de Ventas](https://via.placeholder.com/800x200/1e40af/ffffff?text=API+de+Ventas)

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

## Tutorial paso a paso: Cómo usar el CRUD

### Paso 1: Iniciar el servidor
```cmd
py -3.12 -m uvicorn main:app --reload
```
Abre http://127.0.0.1:8000/docs en tu navegador.

### Paso 2: Crear un Cliente
1. En Swagger UI, busca `POST /clientes`
2. Haz clic en "Try it out"
3. Pega este JSON y ejecuta:
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "rut": "12345678-9"
}
```
4. **Resultado esperado:** Cliente creado con `id: 1`

### Paso 3: Crear Productos
Repite con `POST /productos` usando estos ejemplos:

**Producto 1:**
```json
{
  "nombre": "Mouse Gamer",
  "categoria": "Periféricos",
  "precio": 15000
}
```

**Producto 2:**
```json
{
  "nombre": "Teclado Mecánico",
  "categoria": "Periféricos",
  "precio": 25000
}
```

### Paso 4: Crear una Venta con Detalles
Usa `POST /ventas` con este JSON:
```json
{
  "cliente_id": 1,
  "detalles": [
    {"producto_id": 1, "precio": 15000, "descuento": 0, "cantidad": 2},
    {"producto_id": 2, "precio": 25000, "descuento": 2000, "cantidad": 1}
  ]
}
```
**El sistema calculará automáticamente:** `total = (15000 × 2) + (23000 × 1) = 53000`

### Paso 5: Verificar la Venta
1. Usa `GET /ventas/1` para ver la venta completa
2. Usa `GET /ventas/1/detalles` para ver solo los detalles
3. **Verifica que el total sea 53000**

### Paso 6: Actualizar Información
**Modificar cliente:**
```json
{
  "nombre": "Juan Carlos Pérez",
  "email": "juancarlos@example.com"
}
```

**Modificar cantidad en un detalle (PUT /detalles/1):**
```json
{
  "cantidad": 3
}
```
**¡Ve a `GET /ventas/1` y verifica que el total cambió automáticamente!**

### Paso 7: Probar los Reportes
1. `GET /reportes/productos-mas-vendidos?limit=5`
2. `GET /reportes/clientes-mas-ventas?limit=5`

### Paso 8: Crear Detalles Independientes
Usa `POST /detalles` para añadir un producto más a la venta:
```json
{
  "venta_id": 1,
  "producto_id": 1,
  "precio": 15000,
  "descuento": 1000,
  "cantidad": 1
}
```
**El total de la venta se actualizará automáticamente.**

### Paso 9: Eliminar y Verificar
1. `DELETE /detalles/3` (elimina el último detalle creado)
2. `GET /ventas/1` → Verifica que el total se recalculó
3. Intenta `DELETE /clientes/1` → **Fallará porque tiene ventas asociadas** (integridad referencial)

### ✅ Checklist de pruebas completadas:
- [ ] Cliente creado y actualizado
- [ ] Productos creados y listados
- [ ] Venta creada con múltiples detalles
- [ ] Total calculado automáticamente
- [ ] Detalles modificados y total recalculado
- [ ] Reportes funcionando
- [ ] Eliminación con validación de integridad

### 🎯 **¡Felicidades! Has probado todo el CRUD funcional.**

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

Publicado bajo la MIT License.

# Released under MIT License

Copyright (c) 2013 Mark Otto.

Copyright (c) 2017 Andrew Fong.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


