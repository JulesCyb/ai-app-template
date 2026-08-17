"""FastAPI-Dependencies: Kontext aus dem Request, mandantengebundene DB-Session.

AUTH_MODE=dev-headers liest X-Tenant-Id / X-User-Id / X-Roles aus den Headern – NUR für lokale
Entwicklung. Vor Produktion AUTH_MODE=jwt implementieren (OIDC-Token prüfen, Claims -> Kontext).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.context import RequestContext
from app.db.session import tenant_session


async def get_context(
    settings: Annotated[Settings, Depends(get_settings)],
    x_tenant_id: Annotated[str | None, Header()] = None,
    x_user_id: Annotated[str | None, Header()] = None,
    x_roles: Annotated[str | None, Header()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> RequestContext:
    if settings.auth_mode == "dev-headers":
        if not x_tenant_id or not x_user_id:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "X-Tenant-Id und X-User-Id fehlen (AUTH_MODE=dev-headers)",
            )
        try:
            tenant_id, user_id = UUID(x_tenant_id), UUID(x_user_id)
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ungültige UUID im Header") from exc
        roles = frozenset(r.strip() for r in (x_roles or "").split(",") if r.strip())
        return RequestContext(tenant_id=tenant_id, user_id=user_id, roles=roles)

    # AUTH_MODE=jwt: Bearer-Token prüfen (Signatur, Aussteller, Ablauf) und Claims lesen.
    # Bewusst nicht "irgendwie" implementiert – falsche Auth ist schlimmer als keine.
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        "AUTH_MODE=jwt ist noch nicht implementiert (siehe app/deps.py)",
    )


Context = Annotated[RequestContext, Depends(get_context)]


async def get_session(ctx: Context) -> AsyncIterator[AsyncSession]:
    async with tenant_session(ctx) as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]
