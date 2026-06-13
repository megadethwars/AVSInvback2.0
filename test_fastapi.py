#!/usr/bin/env python
"""Test script para verificar que Flask context funciona en FastAPI"""

import sys
sys.path.insert(0, '.')

from src.fastapi_app import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=" * 60)
print("Testing FastAPI with Flask-SQLAlchemy context...")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing /health endpoint...")
response = client.get("/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 2: Get lugares
print("\n2. Testing /api/v1/lugares endpoint...")
try:
    response = client.get("/api/v1/lugares")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        lugares = response.json()
        print(f"   Lugares encontrados: {len(lugares)}")
        if lugares:
            print(f"   Primer lugar: {lugares[0]}")
    else:
        print(f"   Error: {response.json()}")
except Exception as e:
    print(f"   Error: {str(e)}")

print("\n" + "=" * 60)
print("✓ Tests completados")
print("=" * 60)
