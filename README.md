# ai-app-template

Grundgerüst für Apps mit KI-Agenten – Blueprint A aus dem Claude-Code-Skill `ai-app-architecture`:
**Agent-Backend als API** (FastAPI + PydanticAI), **PostgreSQL + pgvector mit Row-Level Security**,
**MCP-Server** für die Tools, **Langfuse**-Tracing, **LiteLLM** als optionales Modell-Gateway,
Docker Compose. Mandantenfähig ab Tag 1, ohne dass es beim ersten Mandanten stört.

Stand: 2026-08 (PydanticAI 2.x, MCP-SDK 2.x, FastAPI 0.14x). Vor dem Ableiten `uv lock --upgrade`
und die Modellnamen in `.env.example` / `docker/litellm/config.yaml` aktualisieren.

## Was drin ist

| Baustein | Datei | Zweck |
|---|---|---|
| Kontext-Objekt | `app/context.py` | `tenant_id`, `user_id`, Rollen – wird überall durchgereicht |
| Auth (dev) | `app/deps.py` | `X-Tenant-Id`/`X-User-Id`-Header lokal; JWT-Stelle vorbereitet |
| Mandanten-Session | `app/db/session.py` | `set_config('app.tenant_id', …)` pro Transaktion |
| Schema + RLS | `migrations/versions/0001_initial.py` | tenants, users, documents(vector 1536), Policies, Grants |
| App-Rolle | `docker/postgres/01-init.sh` | `app` ohne Superuser/BYPASSRLS – sonst greift RLS nicht |
| Repository | `app/repositories/documents.py` | einziger Weg zur DB, Vektorsuche |
| Tools | `app/tools/documents.py` | Suche mit Kontext, gemeinsam für Agent und MCP |
| Agent | `app/agents/assistant.py` | PydanticAI-Agent, Modell zur Laufzeit, Tracing-Metadaten |
| API | `app/api/` | `/agents/assistant/run`, `/agents/assistant/stream` (SSE), `/api/chat` (Vercel AI SDK) |
| MCP-Server | `app/mcp/server.py` | dieselben Tools für Claude Code / Claude Desktop |
| Modelle | `app/llm.py`, `app/embeddings.py` | Provider-Abstraktion, LiteLLM-Option |
| Tracing | `app/observability.py` | Langfuse über OTel (optional) |
| Tests | `tests/` | Unit (TestModel, ohne DB) + echter RLS-Test mit eingebettetem Postgres |

## Schnellstart

```bash
uv sync --group dbtest              # dbtest nur, wenn du den echten RLS-Test willst
cp .env.example .env                # Keys und Modellnamen eintragen
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/seed.py "Mein Mandant" me@example.com   # gibt Tenant-/User-ID aus
uv run uvicorn app.main:app --reload
```

Aufruf (dev-headers):

```bash
curl -X POST localhost:8000/agents/assistant/run \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-Id: <TENANT>' -H 'X-User-Id: <USER>' \
  -d '{"prompt": "Was steht in meinen Dokumenten zu Kündigungsfristen?"}'
```

Tests: `uv run pytest` (der RLS-Test wird übersprungen, wenn `pgserver` fehlt).

## Projekt ableiten – Checkliste

1. Repo kopieren (`degit` oder Clone ohne `.git`), Name in `pyproject.toml`, `CLAUDE.md`, `.env.example` ersetzen.
2. `docs/adr/0001-architektur.md` schreiben (Vorlage `docs/adr/adr-template.md`; Beispiel im Skill).
3. `LLM_MODEL`, `EMBEDDING_MODEL` (Dimension = Migration!) und ggf. LiteLLM-Config setzen.
4. Fachtabellen als neue Migration – Checkliste im `script.py.mako` beachten.
5. Tools in `app/tools/`, MCP-Server erweitern, Agent-Instruktionen anpassen.
6. Frontend nach `docs/frontend.md`, Mobile-App nach `docs/mobile.md`; Deployment nach `docs/deployment.md`.
7. `AUTH_MODE=jwt` implementieren, bevor irgendetwas öffentlich erreichbar ist.

## Bewusst nicht enthalten

- Kein Frontend im Repo (schnelllebig; `docs/frontend.md` beschreibt den Anschluss).
- Kein LangGraph – erst, wenn ein Agent eine Zustandsmaschine braucht (dann als eigenes Modul, mit ADR).
- Keine Langfuse-Compose-Datei – die offizielle von Langfuse einbinden (`docs/deployment.md`).
- Kein Onboarding/Billing für Mandanten – kommt mit dem zweiten Kunden (`references/mandanten.md` im Skill).
