"""Tool-Funktionen für Dokumente – gemeinsames Modul für Agent-Tools UND MCP-Server.

Regel: Ein Tool bekommt den Kontext, öffnet selbst eine mandantengebundene Session, geht über das
Repository und gibt nur das Nötige zurück (Snippet statt Volltext). Alles, was hier zurückkommt,
landet im Prompt beim Modellanbieter.
"""

from __future__ import annotations

from app.context import RequestContext
from app.db.session import tenant_session
from app.embeddings import embed
from app.repositories.documents import DocumentHit, DocumentRepository


async def search_documents(ctx: RequestContext, query: str, limit: int = 5) -> list[DocumentHit]:
    """Semantische Suche in den Dokumenten des Mandanten (RLS filtert in der DB)."""
    limit = max(1, min(limit, 20))
    embedding = await embed(query)
    async with tenant_session(ctx) as session:
        return await DocumentRepository().search(session, embedding, limit=limit)
