"""Agent tests without a model call: TestModel invokes the tools; we verify the context flow."""

from app.agents.assistant import run_assistant, stream_assistant


async def test_tool_receives_tenant_context(deps, calls, test_model, ctx):
    output = await run_assistant("What does the Acme contract say?", deps)
    assert output  # TestModel returns a deterministic answer
    assert calls, "search_documents was not called"
    tenant_id, query, limit = calls[0]
    assert tenant_id == ctx.tenant_id
    assert 1 <= limit <= 20


async def test_stream_yields_text(deps, test_model):
    chunks: list[str] = []
    async with stream_assistant("Hello", deps) as result:
        async for delta in result.stream_text(delta=True):
            chunks.append(delta)
    assert "".join(chunks)
