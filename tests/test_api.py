"""API-Tests über ASGI, Auth im dev-headers-Modus, Suche und Modell ersetzt."""

from __future__ import annotations

import uuid

import httpx
import pytest

from app.agents import assistant as assistant_module
from app.main import app


@pytest.fixture
def client(monkeypatch, fake_search, test_model):
    # Suche ohne DB: AssistantDeps löst den Default zur Laufzeit auf -> Fake einsetzen.
    monkeypatch.setattr(assistant_module.document_tools, "search_documents", fake_search)
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_health(client):
    async with client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_run_requires_dev_headers(client):
    async with client:
        response = await client.post("/agents/assistant/run", json={"prompt": "Hi"})
    assert response.status_code == 401


async def test_run_with_context(client, calls):
    tenant_id, user_id = uuid.uuid4(), uuid.uuid4()
    async with client:
        response = await client.post(
            "/agents/assistant/run",
            json={"prompt": "Was steht im Vertrag?"},
            headers={"X-Tenant-Id": str(tenant_id), "X-User-Id": str(user_id)},
        )
    assert response.status_code == 200, response.text
    assert response.json()["output"]
    assert calls and calls[0][0] == tenant_id
