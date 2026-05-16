# File: tests/test_profile_views.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_profile_views_list():
    response = client.get("/profile_views")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_profile_views_unauthorized():
    response = client.post("/profile_views", json={"name": "test"})
    # Expecting 401 since we have auth middleware
    assert response.status_code == 401
