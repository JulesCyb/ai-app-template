"""Agent-Endpunkte: einmalige Antwort und Text-Stream (SSE).

Für eine Vercel-AI-SDK-Chat-UI siehe app/api/chat.py.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.assistant import AssistantDeps, run_assistant, stream_assistant
from app.deps import Context

router = APIRouter(prefix="/agents", tags=["agents"])


class RunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)


class RunResponse(BaseModel):
    output: str


@router.post("/assistant/run", response_model=RunResponse)
async def run(body: RunRequest, ctx: Context) -> RunResponse:
    output = await run_assistant(body.prompt, AssistantDeps(ctx=ctx))
    return RunResponse(output=output)


@router.post("/assistant/stream")
async def stream(body: RunRequest, ctx: Context) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        async with stream_assistant(body.prompt, AssistantDeps(ctx=ctx)) as result:
            async for delta in result.stream_text(delta=True):
                yield f"data: {delta}\n\n"
        yield "event: done\ndata: \n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
