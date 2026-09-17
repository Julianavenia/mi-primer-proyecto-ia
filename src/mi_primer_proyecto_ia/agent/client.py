from typing import Any

from mi_primer_proyecto_ia.agent.fake_client import FakeAnthropicClient
from mi_primer_proyecto_ia.config import Settings


def build_client(settings: Settings) -> Any:
    """Cliente síncrono para hablar con el modelo.

    Con `llm_backend="fake"` (default) devuelve un `FakeAnthropicClient` local,
    sin red ni API key. Con `llm_backend="anthropic"` construye el cliente real
    del SDK — solo entonces hace falta `ANTHROPIC_API_KEY`.
    """
    if settings.llm_backend == "fake":
        return FakeAnthropicClient()

    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY es obligatoria cuando LLM_BACKEND=anthropic. "
            "Defínela en .env, o vuelve a LLM_BACKEND=fake para trabajar en modo local."
        )
    from anthropic import Anthropic

    return Anthropic(api_key=settings.anthropic_api_key)


def build_async_client(settings: Settings) -> Any:
    """Cliente asíncrono. Usar siempre dentro de rutas `async` de FastAPI (fase 3+).

    Mismo criterio que `build_client`: fake por defecto, real solo con
    `llm_backend="anthropic"`.
    """
    if settings.llm_backend == "fake":
        return FakeAnthropicClient()

    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY es obligatoria cuando LLM_BACKEND=anthropic. "
            "Defínela en .env, o vuelve a LLM_BACKEND=fake para trabajar en modo local."
        )
    from anthropic import AsyncAnthropic

    return AsyncAnthropic(api_key=settings.anthropic_api_key)
