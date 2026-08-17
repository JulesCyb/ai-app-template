"""Chat-Endpunkt im Vercel-AI-SDK-Format.

Ein Next.js-Frontend mit `useChat` (Vercel AI SDK) kann direkt gegen POST /api/chat sprechen –
PydanticAI übersetzt Nachrichten und Stream (inkl. Tool-Events). Siehe docs/frontend.md.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import Response
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

from app.agents.assistant import AssistantDeps, assistant
from app.deps import Context
from app.llm import get_model

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(request: Request, ctx: Context) -> Response:
    deps = AssistantDeps(ctx=ctx)
    return await VercelAIAdapter.dispatch_request(
        request,
        agent=assistant,
        deps=deps,
        model=get_model(deps.model_name),
        metadata=ctx.trace_attributes(),
        sdk_version=6,
    )
