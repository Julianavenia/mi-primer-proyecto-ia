"""Dependencias de FastAPI: settings, cliente del agente y store de conversaciones.

Funciones separadas y sencillas de sustituir con `app.dependency_overrides` en
los tests — así los tests de la API pueden inyectar un `FakeAnthropicClient`
guionado sin levantar nada real.
"""

from functools import lru_cache
from typing import Annotated, Any

from anthropic.types import MessageParam
from fastapi import Depends, HTTPException

from mi_primer_proyecto_ia.agent.client import build_client
from mi_primer_proyecto_ia.config import Settings

ConversationStore = dict[str, list[MessageParam]]

_conversation_store: ConversationStore = {}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_llm_client(settings: Annotated[Settings, Depends(get_settings)]) -> Any:
    """Construye el cliente del agente (fake o real) a partir de `settings`.

    Reutiliza `agent/client.py::build_client`, sin duplicar la lógica de
    selección fake/real que ya vive ahí. Si `build_client` falla (ej. falta
    `ANTHROPIC_API_KEY` con `llm_backend="anthropic"`), se traduce aquí mismo
    a un 500 con un mensaje claro, en vez de dejar escapar un `RuntimeError`
    crudo desde la resolución de dependencias.
    """
    try:
        return build_client(settings)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def get_conversation_store() -> ConversationStore:
    return _conversation_store
