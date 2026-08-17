"""Der Standard-Agent: PydanticAI mit Tools, Kontext über deps.

- Kein Modell fest verdrahtet: get_model() liefert es zur Laufzeit (Provider-Abstraktion, ggf. pro
  Mandant). Tests überschreiben mit TestModel/FunctionModel – kein echter Modellaufruf.
- Tools sind dünne Wrapper um app/tools/*, die den Kontext aus ctx.deps holen.
- LangGraph erst, wenn ein Ablauf zur Zustandsmaschine wird (Checkpoints, Human-in-the-Loop) –
  dann als eigenes Modul, mit ADR.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.result import StreamedRunResult

from app.context import RequestContext
from app.llm import get_model
from app.repositories.documents import DocumentHit
from app.tools import documents as document_tools

SearchFn = Callable[[RequestContext, str, int], Awaitable[list[DocumentHit]]]


@dataclass
class AssistantDeps:
    ctx: RequestContext
    # Injizierbar, damit Tests ohne Datenbank und Embeddings laufen (None = echte Suche).
    search: SearchFn | None = None
    model_name: str | None = None  # z. B. aus tenants.settings["model"]

    def __post_init__(self) -> None:
        if self.search is None:
            self.search = document_tools.search_documents


INSTRUCTIONS = (
    "Du bist der Assistent dieser Anwendung. Beantworte Fragen auf Basis der Dokumente des "
    "Nutzers. Nutze search_documents, bevor du Fakten behauptest, und nenne die Titel der "
    "Dokumente, auf die du dich stützt. Wenn nichts Passendes gefunden wird, sag das klar."
)

assistant: Agent[AssistantDeps, str] = Agent(
    deps_type=AssistantDeps,
    instructions=INSTRUCTIONS,
    name="assistant",
    retries=2,
)


@assistant.tool
async def search_documents(
    ctx: RunContext[AssistantDeps], query: str, limit: int = 5
) -> list[DocumentHit]:
    """Durchsucht die Dokumente des aktuellen Nutzers semantisch.

    Args:
        query: Suchanfrage in natürlicher Sprache.
        limit: Maximale Trefferzahl (1–20).
    """
    assert ctx.deps.search is not None
    return await ctx.deps.search(ctx.deps.ctx, query, limit)


async def run_assistant(prompt: str, deps: AssistantDeps) -> str:
    result = await assistant.run(
        prompt,
        deps=deps,
        model=get_model(deps.model_name),
        metadata=deps.ctx.trace_attributes(),
    )
    return result.output


def stream_assistant(prompt: str, deps: AssistantDeps):
    """Async-Contextmanager mit StreamedRunResult; im Route-Handler mit `async with` verwenden."""
    return assistant.run_stream(
        prompt,
        deps=deps,
        model=get_model(deps.model_name),
        metadata=deps.ctx.trace_attributes(),
    )


__all__ = ["AssistantDeps", "StreamedRunResult", "assistant", "run_assistant", "stream_assistant"]
