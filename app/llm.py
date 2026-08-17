"""Provider-Abstraktion für Sprachmodelle.

Modellname im PydanticAI-Format "<provider>:<model>" (LLM_MODEL). Ist LITELLM_BASE_URL gesetzt,
läuft alles über das LiteLLM-Gateway (OpenAI-kompatibel) – Anbieterwechsel = Konfigzeile.
Pro Mandant kann tenants.settings["model"] den Standard überschreiben (model_name-Argument).
"""

from __future__ import annotations

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import get_settings


def get_model(model_name: str | None = None) -> Model | str:
    s = get_settings()
    name = model_name or s.llm_model
    if s.litellm_base_url:
        # Über das Gateway: nur der Modellname aus litellm/config.yaml, ohne Provider-Präfix.
        bare = name.split(":", 1)[1] if ":" in name else name
        provider = OpenAIProvider(
            base_url=s.litellm_base_url, api_key=s.litellm_api_key or "litellm"
        )
        return OpenAIChatModel(bare, provider=provider)
    return name
