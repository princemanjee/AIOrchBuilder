# File: tests/test_contact_messages.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_contact_messages_list():
    response = client.get("/contact_messages")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_contact_messages_unauthorized():
    response = client.post("/contact_messages", json={"name": "test"})
    # Expecting 401 since we have auth middleware
    assert response.status_code == 401
