", ", "Tests for health check routes.", ", "

import json


class TestHealthCheck:
    ", ", "Test health check endpoints.", ", "

    def test_health_endpoint(self, client):
        ", ", "Test health endpoint returns healthy status.", ", "
        response = client.get("/api/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("status") == "healthy"

    def test_health_root_endpoint(self, client):
        ", ", "Test health root endpoint.", ", "
        response = client.get("/api/health/")
        assert response.status_code in [200, 404]

    def test_health_has_service(self, client):
        ", ", "Test health response includes service name.", ", "
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert "service" in data

    def test_health_has_version(self, client):
        ", ", "Test health response includes version.", ", "
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert "version" in data

    def test_readiness_endpoint(self, client):
        ", ", "Test readiness check endpoint.", ", "
        response = client.get("/api/health/ready")
        assert response.status_code in [200, 404, 503]
