"""MCP-Server mit denselben Tool-Funktionen wie das Backend (app/tools/*).

Nutzen: Claude Code / Claude Desktop beim Entwickeln, später Managed-Plattformen – ohne die
Tools neu zu schreiben.

Kontext: In Produktion kommt der Mandanten-/Nutzerkontext aus der Authentifizierung der
MCP-Verbindung (OAuth/Token). Für lokale Entwicklung aus MCP_TENANT_ID / MCP_USER_ID.

Start (stdio, z. B. in .mcp.json von Claude Code):
    uv run python -m app.mcp.server

Hinweis Aktualität: MCP-Python-SDK 2.x -> `from mcp.server.mcpserver import MCPServer`
(vorher `from mcp.server.fastmcp import FastMCP`). Bei SDK-Updates prüfen.
"""

from __future__ import annotations

from uuid import UUID

from mcp.server.mcpserver import MCPServer

from app.config import get_settings
from app.context import RequestContext
from app.tools import documents as document_tools

server = MCPServer(
    name="ai-app-tools",
    instructions="Werkzeuge der Anwendung: semantische Suche in den Dokumenten des Mandanten.",
)


def _context_from_env() -> RequestContext:
    s = get_settings()
    if not (s.mcp_tenant_id and s.mcp_user_id):
        raise RuntimeError("MCP_TENANT_ID und MCP_USER_ID setzen (nur Entwicklung).")
    return RequestContext(tenant_id=UUID(s.mcp_tenant_id), user_id=UUID(s.mcp_user_id))


@server.tool()
async def search_documents(query: str, limit: int = 5) -> list[dict]:
    """Semantische Suche in den Dokumenten des aktuellen Mandanten."""
    hits = await document_tools.search_documents(_context_from_env(), query, limit)
    return [hit.model_dump(mode="json") for hit in hits]


if __name__ == "__main__":
    server.run(transport="stdio")
