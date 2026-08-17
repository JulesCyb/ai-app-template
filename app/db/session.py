"""Async-Engine und mandantengebundene Sessions.

tenant_session() öffnet eine Transaktion und setzt app.tenant_id / app.user_id per set_config
(is_local=true, gilt nur für diese Transaktion). Die RLS-Policies in migrations/ filtern damit.
Ohne gesetzten Kontext liefert current_setting(..., true) NULL -> die Policies blocken alles.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.context import RequestContext

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine, _session_factory
    if _engine is None:
        _engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _session_factory is not None
    return _session_factory


@asynccontextmanager
async def tenant_session(ctx: RequestContext) -> AsyncIterator[AsyncSession]:
    """Eine Transaktion im Kontext des Mandanten. Commit am Ende, Rollback bei Fehler."""
    async with get_session_factory()() as session:
        async with session.begin():
            await session.execute(
                text("SELECT set_config('app.tenant_id', :tid, true)"),
                {"tid": str(ctx.tenant_id)},
            )
            await session.execute(
                text("SELECT set_config('app.user_id', :uid, true)"),
                {"uid": str(ctx.user_id)},
            )
            yield session
