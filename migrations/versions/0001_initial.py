"""Grundschema: tenants, users, documents (pgvector) mit Row-Level Security.

Revision ID: 0001
Revises:
Create Date: 2026-08-17

Rollen: Migrationen laufen als Owner (DATABASE_URL_MIGRATIONS). Die App verbindet sich als
Rolle `app` (kein Superuser, NOBYPASSRLS – angelegt in docker/postgres/01-init.sh). Superuser
umgehen RLS immer; deshalb darf die App nie als Superuser laufen.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TENANT_TABLES = ("users", "documents")


def _rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {table}_tenant_isolation ON {table}
            USING      (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute(
        """
        CREATE TABLE tenants (
            id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name        varchar(200) NOT NULL,
            settings    jsonb NOT NULL DEFAULT '{}'::jsonb,
            created_at  timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenants FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY tenants_self_only ON tenants
            USING (id = current_setting('app.tenant_id', true)::uuid)
        """
    )

    op.execute(
        """
        CREATE TABLE users (
            id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            email       varchar(320) NOT NULL,
            role        varchar(50) NOT NULL DEFAULT 'member',
            created_at  timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, email)
        )
        """
    )
    op.execute("CREATE INDEX users_tenant_idx ON users (tenant_id)")

    op.execute(
        """
        CREATE TABLE documents (
            id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            title       varchar(500) NOT NULL,
            content     text NOT NULL,
            embedding   vector(1536),
            metadata    jsonb NOT NULL DEFAULT '{}'::jsonb,
            created_at  timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX documents_tenant_idx ON documents (tenant_id)")
    # Vektor-Index erst ab einigen zehntausend Zeilen nötig; dann z. B.:
    # CREATE INDEX documents_embedding_idx ON documents USING hnsw (embedding vector_cosine_ops)

    for table in TENANT_TABLES:
        _rls(table)

    # Rechte für die App-Rolle (existiert nur, wenn 01-init.sh gelaufen ist – sonst überspringen).
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app') THEN
                GRANT SELECT, INSERT, UPDATE, DELETE ON tenants, users, documents TO app;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS documents")
    op.execute("DROP TABLE IF EXISTS users")
    op.execute("DROP TABLE IF EXISTS tenants")
