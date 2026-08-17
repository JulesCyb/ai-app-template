# Deployment (blueprint A)

## Local / a single server (EU)

- `docker compose up -d` starts Postgres and the API; `--profile gateway` adds LiteLLM.
- Migrations run at API startup (`alembic upgrade head`) using `DATABASE_URL_MIGRATIONS`.
- Backups: `pg_dump` via cron or provider snapshots; object storage (MinIO/Hetzner) for files.
- Put a reverse proxy with TLS (Caddy/Traefik) in front of the API.

## Langfuse (tracing)

Langfuse v3 needs ClickHouse, Redis/Valkey, and MinIO. Use the official compose file from
https://github.com/langfuse/langfuse (do not rebuild it), start it on the same Docker network,
and set `LANGFUSE_HOST` (e.g. `http://langfuse-web:3000`), `LANGFUSE_PUBLIC_KEY`,
`LANGFUSE_SECRET_KEY`. Then `uv sync --extra observability`.

## LiteLLM (gateway)

Maintain `docker/litellm/config.yaml`; virtual keys with per-tenant budgets via the LiteLLM admin
API. Backend: `LITELLM_BASE_URL=http://litellm:4000`, `LITELLM_API_KEY=<virtual key>`,
`LLM_MODEL=openai:claude` (the name from the config).

## Scaling / relocation

- More load: scale the API horizontally (it is stateless), run Postgres separately (a managed EU provider).
- Enterprise requirements: move the agent logic to Bedrock AgentCore / Azure Foundry (blueprint C/D);
  the tools remain usable as MCP servers.
- Strict data protection: self-host the models (vLLM) behind the same provider abstraction (blueprint E).
