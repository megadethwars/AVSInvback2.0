#!/usr/bin/env python
"""Script para validar la app FastAPI y su documentación Swagger"""

from src.fastapi_app import app

print("✓ FastAPI app importada exitosamente")
print(f"✓ Título: {app.title}")
print(f"✓ Versión: {app.version}")
print(f"✓ Descripción: {app.description}")
print(f"\n✓ Total de rutas: {len(app.routes)}")
print("\nEndpoints disponibles:")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', ['MOUNT'])
        print(f"  {route.path} - {methods}")

print("\n✓ Swagger UI disponible en: /docs")
print("✓ ReDoc disponible en: /redoc")
print("✓ OpenAPI Schema disponible en: /openapi.json")
