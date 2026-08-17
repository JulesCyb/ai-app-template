"""Repository-Schicht: der einzige Weg zu den Daten.

Die Session kommt aus tenant_session(ctx) und ist damit mandantengebunden; RLS filtert in der DB.
tenant_id wird beim Schreiben trotzdem explizit aus dem Kontext gesetzt (WITH CHECK der Policy
lehnt alles andere ab).
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.context import RequestContext
from app.db.models import Document


class DocumentHit(BaseModel):
    id: UUID
    title: str
    snippet: str
    score: float


class DocumentRepository:
    async def add(
        self,
        session: AsyncSession,
        ctx: RequestContext,
        *,
        title: str,
        content: str,
        embedding: list[float] | None,
        metadata: dict | None = None,
    ) -> Document:
        doc = Document(
            tenant_id=ctx.tenant_id,
            title=title,
            content=content,
            embedding=embedding,
            metadata_=metadata or {},
        )
        session.add(doc)
        await session.flush()
        return doc

    async def search(
        self,
        session: AsyncSession,
        embedding: list[float],
        *,
        limit: int = 5,
        snippet_chars: int = 400,
    ) -> list[DocumentHit]:
        distance = Document.embedding.cosine_distance(embedding).label("distance")
        stmt = (
            select(Document, distance)
            .where(Document.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )
        rows = (await session.execute(stmt)).all()
        return [
            DocumentHit(
                id=doc.id,
                title=doc.title,
                snippet=doc.content[:snippet_chars],
                score=1.0 - float(dist),
            )
            for doc, dist in rows
        ]
