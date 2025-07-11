import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "ChoibenAssist AI Backend"
    assert response.json()["status"] == "running"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()


def test_detailed_health_check():
    """Test detailed health check endpoint"""
    response = client.get("/api/health/detailed")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "dependencies" in response.json()
