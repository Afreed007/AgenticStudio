"""Unit and integration tests for FastAPI REST and WebSocket endpoints."""

import time
import pytest
from fastapi.testclient import TestClient
from agentic_studio.api.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_start_run_and_status(tmp_path):
    workspace = str(tmp_path / "api_test_workspace")
    payload = {
        "prompt": "Build an in-memory key-value cache",
        "workspace": workspace,
        "mock_mode": True,
    }

    response = client.post("/api/runs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    run_id = data["run_id"]
    assert data["status"] in ("PENDING", "RUNNING")

    # Give background thread 3-4 seconds to execute the agency run
    time.sleep(3.5)

    # Fetch status
    status_resp = client.get(f"/api/runs/{run_id}")
    assert status_resp.status_code == 200
    run_data = status_resp.json()
    assert run_data["status"] == "SUCCESS"
    assert len(run_data["messages"]) > 0

    # List runs
    list_resp = client.get("/api/runs")
    assert list_resp.status_code == 200
    assert any(r["run_id"] == run_id for r in list_resp.json())

    # List generated files
    files_resp = client.get(f"/api/runs/{run_id}/files")
    assert files_resp.status_code == 200
    files = files_resp.json()
    assert "url_shortener/service.py" in files

    # Read file content
    content_resp = client.get(f"/api/runs/{run_id}/files/content?path=url_shortener/service.py")
    assert content_resp.status_code == 200
    assert "class URLShortener" in content_resp.json()["content"]
