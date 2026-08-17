#!/bin/bash
# Creates the app role: no superuser, no BYPASSRLS — otherwise Row-Level Security does not apply.
# Runs once on the first start of the Postgres container.
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE app LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE PASSWORD '${APP_DB_PASSWORD}';
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO app;
    GRANT USAGE ON SCHEMA public TO app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app;
EOSQL
