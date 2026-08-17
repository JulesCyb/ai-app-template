"""Echter Isolationstest gegen PostgreSQL + pgvector (Paket `pgserver`, `uv sync --group dbtest`).

Prüft, was die Unit-Tests nicht können: dass die RLS-Policies aus der Migration greifen, wenn die
App als Rolle `app` (kein Superuser, NOBYPASSRLS) arbeitet.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import uuid
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pgserver = pytest.importorskip("pgserver")

DIM = 1536


def _vec(seed: float) -> str:
    values = [0.0] * DIM
    values[0] = 1.0
    values[1] = seed
    return "[" + ",".join(f"{v:.3f}" for v in values) + "]"


@pytest.fixture(scope="module")
def database_urls():
    pgdata = tempfile.mkdtemp(prefix="pgdata-")
    server = pgserver.get_server(pgdata)
    sockdir = parse_qs(urlparse(server.get_uri()).query)["host"][0]
    server.psql(
        "CREATE ROLE app LOGIN NOSUPERUSER NOBYPASSRLS; "
        "GRANT USAGE ON SCHEMA public TO app; "
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE "
        "ON TABLES TO app;"
    )
    urls = {
        "migrations": f"postgresql+asyncpg://postgres@/postgres?host={sockdir}",
        "app": f"postgresql+asyncpg://app@/postgres?host={sockdir}",
    }
    env = {**os.environ, "DATABASE_URL_MIGRATIONS": urls["migrations"], "DATABASE_URL": urls["app"]}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"], check=True, env=env, timeout=120
    )
    yield urls
    server.cleanup()


@pytest.fixture
def app_settings(database_urls, monkeypatch):
    from app import config
    from app.db import session as db_session

    monkeypatch.setenv("DATABASE_URL", database_urls["app"])
    monkeypatch.setenv("DATABASE_URL_MIGRATIONS", database_urls["migrations"])
    config.get_settings.cache_clear()
    db_session._engine = None
    db_session._session_factory = None
    yield
    config.get_settings.cache_clear()
    db_session._engine = None
    db_session._session_factory = None


async def _seed(url: str) -> tuple[uuid.UUID, uuid.UUID]:
    """Zwei Mandanten mit je einem Dokument – als Owner, weil ohne Kontext RLS alles blockt."""
    engine = create_async_engine(url)
    tenant_a, tenant_b = uuid.uuid4(), uuid.uuid4()
    async with engine.begin() as conn:
        for tenant_id, name, seed in ((tenant_a, "A", 0.1), (tenant_b, "B", 0.9)):
            await conn.execute(
                text("INSERT INTO tenants (id, name) VALUES (:id, :name)"),
                {"id": tenant_id, "name": name},
            )
            await conn.execute(
                text(
                    "INSERT INTO documents (tenant_id, title, content, embedding) "
                    "VALUES (:tid, :title, :content, CAST(:emb AS vector))"
                ),
                {
                    "tid": tenant_id,
                    "title": f"Dokument {name}",
                    "content": f"Inhalt von Mandant {name}",
                    "emb": _vec(seed),
                },
            )
    await engine.dispose()
    return tenant_a, tenant_b


async def test_search_sees_only_own_tenant(app_settings, database_urls):
    from app.context import RequestContext
    from app.db.session import tenant_session
    from app.repositories.documents import DocumentRepository

    tenant_a, tenant_b = await _seed(database_urls["migrations"])
    query = [0.0] * DIM
    query[0] = 1.0

    ctx_a = RequestContext(tenant_id=tenant_a, user_id=uuid.uuid4())
    async with tenant_session(ctx_a) as session:
        hits = await DocumentRepository().search(session, query, limit=10)
    assert [h.title for h in hits] == ["Dokument A"]

    ctx_b = RequestContext(tenant_id=tenant_b, user_id=uuid.uuid4())
    async with tenant_session(ctx_b) as session:
        hits = await DocumentRepository().search(session, query, limit=10)
    assert [h.title for h in hits] == ["Dokument B"]


async def test_insert_for_other_tenant_is_rejected(app_settings, database_urls):
    from sqlalchemy.exc import DBAPIError

    from app.context import RequestContext
    from app.db.session import tenant_session

    tenant_a, tenant_b = await _seed(database_urls["migrations"])
    ctx_a = RequestContext(tenant_id=tenant_a, user_id=uuid.uuid4())
    with pytest.raises(DBAPIError):
        async with tenant_session(ctx_a) as session:
            await session.execute(
                text(
                    "INSERT INTO documents (tenant_id, title, content) "
                    "VALUES (:tid, 'fremd', 'darf nicht')"
                ),
                {"tid": tenant_b},
            )


async def test_no_context_means_no_rows(app_settings, database_urls):
    """Ohne set_config liefert current_setting NULL -> Policy blockt alles (App-Rolle)."""
    await _seed(database_urls["migrations"])
    engine = create_async_engine(database_urls["app"])
    async with engine.connect() as conn:
        count = (await conn.execute(text("SELECT count(*) FROM documents"))).scalar_one()
    await engine.dispose()
    assert count == 0
