"""Embeddings via an OpenAI-compatible endpoint (direct or through LiteLLM).

The dimension must match the documents.embedding column (migration 0001: 1536).
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
