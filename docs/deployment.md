# Deployment (Blueprint A)

## Lokal / ein Server (EU)

- `docker compose up -d` startet Postgres und die API; `--profile gateway` zusätzlich LiteLLM.
- Migrationen laufen beim API-Start (`alembic upgrade head`) mit `DATABASE_URL_MIGRATIONS`.
- Backups: `pg_dump` per Cron oder Anbieter-Snapshots; Objektspeicher (MinIO/Hetzner) für Dateien.
- Reverse Proxy mit TLS (Caddy/Traefik) vor die API.

## Langfuse (Tracing)

Langfuse v3 braucht ClickHouse, Redis/Valkey und MinIO. Die offizielle Compose-Datei aus
https://github.com/langfuse/langfuse verwenden (nicht nachbauen), im gleichen Docker-Netz starten
und `LANGFUSE_HOST` (z. B. `http://langfuse-web:3000`), `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`
setzen. Danach `uv sync --extra observability`.

## LiteLLM (Gateway)

`docker/litellm/config.yaml` pflegen; virtuelle Keys mit Budget pro Mandant über die LiteLLM-Admin-API.
Backend: `LITELLM_BASE_URL=http://litellm:4000`, `LITELLM_API_KEY=<virtueller Key>`,
`LLM_MODEL=openai:claude` (Name aus der Config).

## Skalierung / Umzug

- Mehr Last: API horizontal skalieren (stateless), Postgres separat betreiben (managed EU-Anbieter).
- Enterprise-Anforderungen: Agent-Logik auf Bedrock AgentCore / Azure Foundry umziehen (Blueprint C/D);
  Tools bleiben als MCP-Server nutzbar.
- Strenger Datenschutz: Modelle self-hosted (vLLM) hinter derselben Provider-Abstraktion (Blueprint E).
