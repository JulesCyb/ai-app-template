"""Tool functions for documents — a shared module for agent tools AND the MCP server.

Rule: a tool receives the context, opens its own tenant-bound session, goes through the
repository, and returns only what is needed (a snippet, not the full text). Everything returned
here ends up in the prompt sent to the model provider.
"""

from __future__ import annotations

from app.context import RequestContext
from app.db.session import tenant_session
from app.embeddings import embed
from app.repositories.documents import DocumentHit, DocumentRepository


async def search_documents(ctx: RequestContext, query: str, limit: int = 5) -> list[DocumentHit]:
    """Semantic search in the tenant's documents (RLS filters in the DB)."""
    limit = max(1, min(limit, 20))
    embedding = await embed(query)
    async with tenant_session(ctx) as session:
        return await DocumentRepository().search(session, embedding, limit=limit)
