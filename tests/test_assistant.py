"""Agent-Tests ohne Modellaufruf: TestModel ruft die Tools auf, wir prüfen den Kontextfluss."""

from app.agents.assistant import run_assistant, stream_assistant


async def test_tool_receives_tenant_context(deps, calls, test_model, ctx):
    output = await run_assistant("Was steht im Vertrag mit Musterkunde?", deps)
    assert output  # TestModel liefert eine deterministische Antwort
    assert calls, "search_documents wurde nicht aufgerufen"
    tenant_id, query, limit = calls[0]
    assert tenant_id == ctx.tenant_id
    assert 1 <= limit <= 20


async def test_stream_yields_text(deps, test_model):
    chunks: list[str] = []
    async with stream_assistant("Hallo", deps) as result:
        async for delta in result.stream_text(delta=True):
            chunks.append(delta)
    assert "".join(chunks)
