# Documentación de API - Inventory API 2.0

## 📚 Acceso a la Documentación Interactiva

Una vez que la API está corriendo, accede a:

### **Swagger UI (Interfaz Interactiva Recomendada)**
```
http://localhost:8000/docs
```

Características:
- 🔍 Explorador visual de endpoints
- 📝 Prueba de requests/responses
- 📋 Esquemas completos de datos
- 🧪 "Try it out" para testing directo

### **ReDoc (Documentación Estática)**
```
http://localhost:8000/redoc
```

Características:
- 📖 Formato de documentación clara
- 🔎 Búsqueda de endpoints
- 📱 Diseño responsive

### **JSON OpenAPI Schema**
```
http://localhost:8000/openapi.json
```

Para usar en herramientas externas como Postman, Insomnia, etc.

---

## 🔌 Endpoints de la API

### **System**

#### Health Check
```http
GET /health
```

**Descripción:** Verifica el estado de la API

**Response:**
```json
{
  "status": "ok"
}
```

---

### **Lugares (Catálogo de Ubicaciones)**

#### Listar todos los lugares
```http
GET /api/v1/lugares
```

**Descripción:** Obtiene la lista completa de ubicaciones/lugares

**Response (200):**
```json
[
  {
    "id": 1,
    "lugar": "Almacén Principal",
    "fechaAlta": "2024-01-15T10:30:00",
    "fechaUltimaModificacion": "2024-06-10T14:20:00",
    "activo": true
  },
  {
    "id": 2,
    "lugar": "Oficina Central",
    "fechaAlta": "2024-02-20T09:15:00",
    "fechaUltimaModificacion": "2024-06-12T11:45:00",
    "activo": true
  }
]
```

---

#### Obtener lugar por ID
```http
GET /api/v1/lugares/{id}
```

**Parámetros:**
- `id` (path, requerido): ID del lugar a consultar

**Response (200):**
```json
{
  "id": 1,
  "lugar": "Almacén Principal",
  "fechaAlta": "2024-01-15T10:30:00",
  "fechaUltimaModificacion": "2024-06-10T14:20:00",
  "activo": true
}
```

**Errores:**
- `404 TPM-4`: Lugar no encontrado

---

#### Crear nuevo lugar
```http
POST /api/v1/lugares
Content-Type: application/json
```

**Request Body:**
```json
{
  "lugar": "Nuevo Almacén"
}
```

**Response (201):**
```json
{
  "id": 3,
  "lugar": "Nuevo Almacén",
  "fechaAlta": "2024-06-13T10:30:00",
  "fechaUltimaModificacion": "2024-06-13T10:30:00",
  "activo": true
}
```

**Errores:**
- `400`: Datos inválidos
- `501`: Endpoint en desarrollo

---

#### Actualizar lugar
```http
PUT /api/v1/lugares/{id}
Content-Type: application/json
```

**Parámetros:**
- `id` (path, requerido): ID del lugar a actualizar

**Request Body:**
```json
{
  "lugar": "Almacén Actualizado",
  "activo": true
}
```

**Response (200):**
```json
{
  "id": 1,
  "lugar": "Almacén Actualizado",
  "fechaAlta": "2024-01-15T10:30:00",
  "fechaUltimaModificacion": "2024-06-13T15:45:00",
  "activo": true
}
```

**Errores:**
- `404`: Lugar no encontrado
- `501`: Endpoint en desarrollo

---

#### Eliminar lugar
```http
DELETE /api/v1/lugares/{id}
```

**Parámetros:**
- `id` (path, requerido): ID del lugar a eliminar

**Response (204):** Sin contenido (éxito)

**Errores:**
- `404`: Lugar no encontrado
- `501`: Endpoint en desarrollo

---

## 🔐 Seguridad & CORS

Configuración actual:
- **CORS**: Habilitado para todos los orígenes (`*`)
- **Métodos**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Todos permitidos

Para producción, ajustar en `src/fastapi_app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mi-dominio.com"],  # Especificar dominios
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

## 📋 Esquemas de Datos

### LugaresBase
```json
{
  "id": null,
  "lugar": "string (max 100)",
  "fechaAlta": null,
  "fechaUltimaModificacion": null,
  "activo": null
}
```

### LugaresCreate
```json
{
  "lugar": "string (max 100, requerido)"
}
```

### LugaresUpdate
```json
{
  "id": null,
  "lugar": "string (max 100)",
  "fechaAlta": null,
  "fechaUltimaModificacion": null,
  "activo": null
}
```

---

## 🧪 Ejemplos de Testing

### Con cURL

```bash
# Health check
curl -X GET http://localhost:8000/health

# Listar lugares
curl -X GET http://localhost:8000/api/v1/lugares

# Obtener lugar por ID
curl -X GET http://localhost:8000/api/v1/lugares/1

# Crear lugar (cuando esté implementado)
curl -X POST http://localhost:8000/api/v1/lugares \
  -H "Content-Type: application/json" \
  -d '{"lugar": "Nuevo Almacén"}'
```

### Con Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())  # {"status": "ok"}

# Listar lugares
response = requests.get(f"{BASE_URL}/api/v1/lugares")
lugares = response.json()
print(lugares)

# Obtener lugar específico
response = requests.get(f"{BASE_URL}/api/v1/lugares/1")
lugar = response.json()
print(lugar)

# Crear lugar (cuando esté implementado)
nuevo_lugar = {"lugar": "Nuevo Almacén"}
response = requests.post(f"{BASE_URL}/api/v1/lugares", json=nuevo_lugar)
if response.status_code == 201:
    resultado = response.json()
    print(f"Lugar creado: {resultado}")
```

### Con Postman

1. Importar OpenAPI Schema:
   - `File > Import > URL`
   - Pegar: `http://localhost:8000/openapi.json`

2. O crear request manualmente:
   - **Method**: GET
   - **URL**: `http://localhost:8000/api/v1/lugares`
   - **Headers**: `Content-Type: application/json`

---

## 📊 Códigos de Respuesta HTTP

| Código | Significado | Ejemplo |
|--------|-------------|---------|
| 200 | OK - Request exitoso | GET /api/v1/lugares |
| 201 | Created - Recurso creado | POST /api/v1/lugares |
| 204 | No Content - Eliminado exitosamente | DELETE /api/v1/lugares/{id} |
| 400 | Bad Request - Datos inválidos | JSON malformado |
| 404 | Not Found - Recurso no existe | GET /api/v1/lugares/999 |
| 500 | Server Error - Error interno | Fallo de BD |
| 501 | Not Implemented - Endpoint en desarrollo | Rutas aún sin código |

---

## 🚀 Próximos Pasos

Los siguientes endpoints a documentar y migrar:

1. **Roles** - `/api/v1/roles`
2. **Estatus Usuarios** - `/api/v1/estatus-usuarios`
3. **Usuarios** - `/api/v1/usuarios`
4. **Dispositivos** - `/api/v1/dispositivos`
5. **Movimientos** - `/api/v1/movimientos`
6. **Reportes** - `/api/v1/reportes`

---

## 📞 Soporte

Para preguntas sobre la API:
- Ver documentación interactiva: `http://localhost:8000/docs`
- Contactar al equipo de desarrollo
