# ai-app-template

Grundgerüst für ein KI-Agent-Backend als API: FastAPI + PydanticAI, PostgreSQL 17 + pgvector mit
Row-Level Security, MCP-Server für die Tools, Langfuse-Tracing, Docker Compose. Mandantenfähig ab
Tag 1 (Blueprint A des Skills `ai-app-architecture`). Beim Ableiten eines Projekts: Namen ersetzen,
`docs/adr/0001-architektur.md` schreiben, diese Datei ausdünnen.

Architekturentscheidungen stehen in `docs/adr/`. Bei Widerspruch zwischen dieser Datei und einem
ADR gilt das ADR – dann diese Datei nachziehen.

## Stack (Blueprint A)

- Backend/API: FastAPI, Python 3.12, `uv`
- Agent-Logik: PydanticAI (`app/agents/assistant.py`); LangGraph nur mit ADR-Begründung
- Modelle: `LLM_MODEL` im Format `<provider>:<model>`, optional über LiteLLM-Gateway (`app/llm.py`)
- Daten: PostgreSQL 17 + pgvector, RLS an, App-Rolle `app` (kein Superuser)
- Observability: Langfuse über OTel (`app/observability.py`, optional `logfire`)
- Frontend: keins im Repo – Next.js + Vercel AI SDK gegen `POST /api/chat`, siehe `docs/frontend.md`; Mobile-App als weiterer Client, siehe `docs/mobile.md`
- Betrieb: Docker Compose (`docker-compose.yml`), EU-Standort

## Kommandos

```bash
uv sync                                   # Umgebung (+ --extra observability, --group dbtest)
docker compose up -d postgres             # Datenbank lokal
uv run alembic upgrade head               # Migrationen (Owner-Rolle, DATABASE_URL_MIGRATIONS)
uv run python scripts/seed.py "Mein Mandant" me@example.com   # erster Mandant + Nutzer
uv run uvicorn app.main:app --reload      # API lokal, http://localhost:8000/docs
uv run pytest                             # Tests (müssen vor jedem Commit grün sein)
uv run pytest tests/test_rls_integration.py   # echter RLS-Test (braucht: uv sync --group dbtest)
uv run ruff check . && uv run ruff format .
uv run python -m app.mcp.server           # MCP-Server (stdio) für Claude Code/Desktop
```

Immer `uv run <cmd>`, nie ein globales `python`/`pip`.

## Architekturregeln – nicht verhandelbar

1. **Kontext-Objekt**: `RequestContext(tenant_id, user_id, roles)` entsteht in `app/deps.py` und wird
   durch jeden Request, Agent-Lauf, jedes Tool und jeden Job gereicht. Kein globaler Zustand.
2. **Jede neue Tabelle** hat `tenant_id uuid NOT NULL REFERENCES tenants(id)`, einen Index darauf,
   `ENABLE`/`FORCE ROW LEVEL SECURITY` und eine Policy `tenant_id = current_setting('app.tenant_id',
   true)::uuid` (USING und WITH CHECK) plus GRANT an Rolle `app`. Vorlage: `migrations/versions/0001_initial.py`.
3. **DB-Zugriff nur über Repositories** (`app/repositories/`) mit Sessions aus `tenant_session(ctx)`.
   Die App verbindet sich als `app` (kein Superuser, `NOBYPASSRLS`); Migrationen und Seed mit
   `DATABASE_URL_MIGRATIONS`.
4. **Agents greifen auf Daten nur über Tools zu** (`app/tools/`), die den Kontext prüfen und nur das
   Nötige zurückgeben. Nie DB-Verbindung oder Zugangsdaten ans Modell. Schreibende Tools brauchen
   eine Bestätigung im Ablauf.
5. **Integrationen als MCP-Server** (`app/mcp/server.py`) mit denselben Funktionen aus `app/tools/`.
6. **Modelle über `app/llm.py`**, Modellname aus Konfiguration bzw. `tenants.settings["model"]`.
7. **Jeder Agent-Lauf wird getract** (Langfuse/OTel) mit `tenant_id`, `user_id`, `request_id`
   (`RequestContext.trace_attributes()` als `metadata`).
8. **Cache-Schlüssel** enthalten die `tenant_id`.
9. **Keine Secrets im Repo**; `.env.example` pflegen.
10. **Neuer Agent?** Erst prüfen, ob ein Modellaufruf mit Structured Output reicht. PydanticAI-Agent
    mit Tools ist der Default; LangGraph nur mit ADR (Zustandsmaschine, Checkpoints, Human-in-the-Loop).

## Konventionen

- Type-Hints überall, Pydantic-Modelle für Ein-/Ausgaben, `ruff` (Zeilenlänge 100).
- Agent-Tests mit `TestModel`/`FunctionModel` (`tests/conftest.py`), kein echter Modellaufruf.
- Für jede Repository-Funktion ein Test mit zweitem Mandanten (Muster: `tests/test_rls_integration.py`).
- `AUTH_MODE=dev-headers` ist nur für lokal; vor Produktion JWT/OIDC in `app/deps.py`.
- Neue Entscheidung mit Tragweite → ADR in `docs/adr/` (Vorlage dort).

## Verzeichnisse

```
app/main.py           App-Factory, CORS, Router
app/config.py         Settings (prozessweit; Mandantenspezifisches in tenants.settings)
app/context.py        RequestContext
app/deps.py           Kontext aus Request, mandantengebundene Session
app/db/               Engine, tenant_session(), Modelle
app/repositories/     Datenzugriff (einziger Weg zur DB)
app/tools/            Tool-Funktionen (Agent + MCP)
app/agents/           PydanticAI-Agents
app/api/              Router: /health, /agents/assistant/{run,stream}, /api/chat
app/mcp/server.py     MCP-Server (stdio)
app/llm.py            Provider-Abstraktion; app/embeddings.py; app/observability.py
migrations/           Alembic (async), 0001_initial.py als Vorlage
tests/                pytest; RLS-Integrationstest mit pgserver
docker/               Postgres-Init (App-Rolle), LiteLLM-Config
docs/                 adr/, frontend.md, mobile.md, deployment.md
scripts/seed.py       erster Mandant + Nutzer
```

## Nicht anfassen ohne Rücksprache

- RLS-Policies, Rollen und Rechte in `migrations/` und `docker/postgres/01-init.sh`
- `app/context.py`, `app/deps.py`, `app/db/session.py`
