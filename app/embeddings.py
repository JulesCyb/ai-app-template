"""Embeddings über einen OpenAI-kompatiblen Endpunkt (direkt oder über LiteLLM).

Dimension muss zur Spalte documents.embedding passen (Migration 0001: 1536).
"""

from __future__ import annotations

from openai import AsyncOpenAI

from app.config import get_settings


def _client() -> AsyncOpenAI:
    s = get_settings()
    if s.litellm_base_url:
        return AsyncOpenAI(base_url=s.litellm_base_url, api_key=s.litellm_api_key or "litellm")
    return AsyncOpenAI(api_key=s.openai_api_key)


async def embed(text: str) -> list[float]:
    s = get_settings()
    response = await _client().embeddings.create(
        model=s.embedding_model, input=text, dimensions=s.embedding_dimensions
    )
    return list(response.data[0].embedding)
