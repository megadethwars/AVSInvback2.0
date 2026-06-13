# Inventory API (AVSInvback 2.0)

API de inventario migrada de Flask a FastAPI con Pydantic para validación de esquemas y SQLAlchemy como ORM.

## Descripción

Este proyecto es una API REST para gestión de inventario que expone endpoints para:
- **Lugares**: catálogo de ubicaciones
- **Roles**: perfiles de usuario
- **Estatus**: estados de usuarios y dispositivos
- **Usuarios**: gestión de usuarios del sistema
- **Dispositivos**: inventario de dispositivos
- **Movimientos**: registro de movimientos de dispositivos
- **Reportes**: reporte de incidencias en dispositivos

### Arquitectura

- **Backend**: FastAPI (Python 3.13)
- **Base de datos**: SQL Server con PyMySQL/pymssql
- **ORM**: SQLAlchemy 2.0
- **Validación**: Pydantic v2
- **Servidor ASGI**: Uvicorn
- **Compatibilidad**: Monta la app Flask legacy con `WSGIMiddleware` para preservar endpoints heredados

## Requisitos

- Python 3.13 (recomendado)
- Virtual Environment (`venv`)
- SQL Server accesible en la red

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd AVSInvback2.0
```

### 2. Crear y activar el entorno virtual

#### En Windows (PowerShell):
```powershell
python -m venv venv3.0
.\venv3.0\Scripts\Activate.ps1
```

#### En Windows (CMD):
```cmd
python -m venv venv3.0
venv3.0\Scripts\activate.bat
```

#### En Linux/macOS:
```bash
python3 -m venv venv3.0
source venv3.0/bin/activate
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuración

### Variables de Entorno (`.env`)

Crear un archivo `.env` en la raíz con:

```env
# Base de datos
DATABASE_HOST=<servidor-sql-server>
DATABASE_USER=<usuario>
DATABASE_PASSWORD=<contraseña>
DATABASE_NAME=avsInventory

# API
DEBUG=True
ENVIRONMENT=local
```

### Archivo `src/config.py`

Configurar la URI de base de datos según el entorno:

```python
SQLALCHEMY_DATABASE_URI = "mssql+pymssql://usuario:contraseña@host/basedatos"
```

## Comandos de Arranque

### Desarrollo Local

Arrancar la app con **recarga automática** en el puerto 8000:

```bash
# Desde el entorno activado
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Producción Local

Arrancar sin recarga automática, con múltiples workers:

```bash
# Con 4 workers (ajustar según CPU)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Azure App Service (Linux)

#### Opción 1: Startup Command en App Service

En **Azure Portal**, configurar en **Configuration > General settings**:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

O en archivo `startup.sh` en la raíz:

```bash
#!/bin/bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Opción 2: Archivo `startup.txt`

Crear en la raíz:

```
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Luego en Azure portal:
```
Startup command: cat startup.txt | bash
```

#### Opción 3: Usando Gunicorn (recomendado para producción)

```bash
pip install gunicorn

# Startup command
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker main:app
```

## Verificación de Salud

Probar la API después del arranque:

```bash
# Health check
curl http://localhost:8000/health

# Respuesta esperada:
{"status":"ok"}
```

## Endpoints Disponibles

### Nuevos (FastAPI nativo)

- `GET /api/v1/lugares` - Listar lugares
- `GET /api/v1/lugares/{id}` - Obtener lugar por ID
- `GET /health` - Health check

### Heredados (Flask mounted)

Todos los endpoints originales siguen disponibles en sus rutas actuales, servidos a través de la app Flask montada con `WSGIMiddleware`.

## Estructura del Proyecto

```
AVSInvback2.0/
├── main.py                     # Entrypoint ASGI para App Service
├── app.py                      # Script de desarrollo (Uvicorn)
├── requirements.txt            # Dependencias del proyecto
├── runtime.txt                 # Versión de Python (3.13)
├── .env                        # Variables de entorno (no comitear)
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuración por entorno
│   ├── appinit.py             # Inicialización de Flask
│   ├── fastapi_app.py         # FastAPI entrypoint y rutas nuevas
│   ├── schemas.py             # Modelos Pydantic
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── LugaresModel.py
│   │   ├── UsuariosModel.py
│   │   ├── DispositivosModel.py
│   │   ├── MovimientosModel.py
│   │   ├── ReportesModel.py
│   │   └── ...
│   ├── controllers/           # Controladores Flask
│   │   ├── LugaresView.py
│   │   ├── UsuariosView.py
│   │   └── ...
│   └── shared/
│       └── returnCodes.py
├── migrationsDev/             # Migraciones Alembic
├── venv3.0/                   # Entorno virtual (nuevo)
└── .git/
```

## Migración a FastAPI + Pydantic

### Estado Actual

- ✅ **FastAPI**: Entrypoint establecido en `src/fastapi_app.py`
- ✅ **Pydantic**: Todos los esquemas definidos en `src/schemas.py` (migrados de Marshmallow)
- ⚙️ **Endpoints**: Nuevas rutas en FastAPI para `/api/v1/lugares`
- 🔄 **Legacy**: App Flask montada con `WSGIMiddleware` para preservar compatibilidad

### Siguientes Pasos de Migración

1. **Fase 1 (Completa)**: Migrar endpoints de catálogos (roles, estatus, lugares)
2. **Fase 2**: Migrar endpoints de usuarios y autenticación
3. **Fase 3**: Migrar endpoints de dispositivos y búsquedas
4. **Fase 4**: Migrar endpoints de movimientos y reportes

### Cómo Migrar un Endpoint

**Ejemplo: Crear un nuevo endpoint GET `/api/v1/roles` en FastAPI**

1. En `src/fastapi_app.py`, agregar:

```python
from .models.RolesModel import RolesModel
from .schemas import RolesBase

@app.get("/api/v1/roles", response_model=list[RolesBase])
async def get_roles() -> list[RolesBase]:
    roles = RolesModel.get_all_roles()
    return [RolesBase.model_validate(item) for item in roles]
```

2. Los modelos Pydantic ya existen en `schemas.py`:
   - `RolesBase` (lectura)
   - `RolesCreate` (create)
   - `RolesUpdate` (update)

3. Los modelos ORM no cambian (`RolesModel` sigue igual)

4. La validación y serialización ahora la hace Pydantic automáticamente

## Notas Importantes

### Python 3.13 Compatibility

Se removieron imports deprecated:
- `imp` → No compatible en Python 3.13 (eliminado de `src/appinit.py`)
- `telnetlib` → Removido de `src/controllers/TipoMovimientosView.py`

### pymssql en Python 3.13

- Versión mínima requerida: **2.3.13**
- Versiones anteriores (como 2.2.7) no compilan en Python 3.13 en Windows
- Ver `requirements.txt` para la versión actual

### Entorno Virtual Activo

El workspace actualmente usa **`venv3.0`** como entorno de desarrollo.

Para cambiar manualmente a un entorno diferente:

```bash
# Si usas venv1
.\venv1\Scripts\Activate.ps1
pip install -r requirements.txt

# Si usas venv3.0 (recomendado)
.\venv3.0\Scripts\Activate.ps1
```

## Solución de Problemas

### Error: `ModuleNotFoundError: No module named 'fastapi'`

Verificar que el entorno virtual está activado:

```bash
# En Windows
.\venv3.0\Scripts\Activate.ps1

# En Linux/macOS
source venv3.0/bin/activate
```

Reinstalar dependencias:

```bash
pip install -r requirements.txt
```

### Error de conexión a SQL Server

Verificar que:
1. SQL Server está ejecutándose
2. Las credenciales en `src/config.py` son correctas
3. El firewall permite la conexión en el puerto 1433

### Puerto 8000 ya en uso

Cambiar a otro puerto:

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Testing

Ejecutar tests (si existen):

```bash
pytest
```

## 📚 Documentación Interactiva

Una vez que la app está corriendo, acceder a:

### **Swagger UI (Recomendado)**
```
http://localhost:8000/docs
```
Interfaz interactiva completa para explorar, documentar y probar todos los endpoints.

### **ReDoc**
```
http://localhost:8000/redoc
```
Documentación en formato estático y responsive.

### **OpenAPI JSON Schema**
```
http://localhost:8000/openapi.json
```
Para importar en herramientas como Postman, Insomnia, etc.

### **Archivos de Documentación**

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentación detallada de endpoints, schemas y ejemplos
- [postman_collection.json](postman_collection.json) - Colección Postman para testing (importar en Postman)

## Deployment en Azure App Service

### Pasos

1. **Crear App Service** en Azure (Python 3.13, Linux recomendado)

2. **Configurar Startup Command**:
   ```
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Variables de entorno en Azure**:
   - `SQLALCHEMY_DATABASE_URI=mssql+pymssql://...`
   - Otras variables del `.env` local

4. **Deploy**:
   ```bash
   az webapp up --name <app-name> --resource-group <group>
   ```
   
   O desde Azure Portal: Conectar repo y habilitar CI/CD.

## Contribuciones

1. Crear rama: `git checkout -b feature/nueva-funcionalidad`
2. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
3. Push: `git push origin feature/nueva-funcionalidad`
4. Pull Request

## Licencia

Especificar licencia si aplica.

## Contacto

Contactar al equipo de desarrollo para soporte.
