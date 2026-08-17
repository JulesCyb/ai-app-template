"""Creates the first tenant and user and prints the IDs for .env / dev headers.

Deliberately runs with DATABASE_URL_MIGRATIONS (owner/superuser), because without a tenant
context the RLS policies would block every write.

    uv run python scripts/seed.py "My Tenant" me@example.com
"""

from __future__ import annotations

import asyncio
import sys
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings


async def main(tenant_name: str, email: str) -> None:
    engine = create_async_engine(get_settings().database_url_migrations)
    tenant_id, user_id = uuid.uuid4(), uuid.uuid4()
    async with engine.begin() as conn:
        await conn.execute(
            text("INSERT INTO tenants (id, name) VALUES (:id, :name)"),
            {"id": tenant_id, "name": tenant_name},
        )
        await conn.execute(
            text(
                "INSERT INTO users (id, tenant_id, email, role) "
                "VALUES (:id, :tenant_id, :email, 'admin')"
            ),
            {"id": user_id, "tenant_id": tenant_id, "email": email},
        )
    await engine.dispose()
    print(f"MCP_TENANT_ID={tenant_id}\nMCP_USER_ID={user_id}")
    print(f"\ncurl -H 'X-Tenant-Id: {tenant_id}' -H 'X-User-Id: {user_id}' ...")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/seed.py <tenant name> <email>")
    asyncio.run(main(sys.argv[1], sys.argv[2]))
