import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from mi_primer_proyecto_ia.agent.loop import ToolIterationLimitError, run_agent_turn
from mi_primer_proyecto_ia.api.deps import (
    ConversationStore,
    get_conversation_store,
    get_llm_client,
    get_settings,
)
from mi_primer_proyecto_ia.api.schemas import ChatRequest, ChatResponse, ToolCallInfo
from mi_primer_proyecto_ia.config import Settings

router = APIRouter()


@router.post("/chat")
async def post_chat(
    request: ChatRequest,
    client: Annotated[Any, Depends(get_llm_client)],
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[ConversationStore, Depends(get_conversation_store)],
) -> ChatResponse:
    conversation_id = request.conversation_id or str(uuid.uuid4())
    history = store.setdefault(conversation_id, [])
    history_len_before = len(history)

    try:
        reply = await run_in_threadpool(
            run_agent_turn, client, settings, history, request.message
        )
    except ToolIterationLimitError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    tool_calls = _extract_tool_calls(history[history_len_before:])
    return ChatResponse(reply=reply, conversation_id=conversation_id, tool_calls=tool_calls)


def _extract_tool_calls(new_messages: list[Any]) -> list[ToolCallInfo]:
    """Reconstruye qué tools se invocaron en este turno a partir de `history`.

    No toca `agent/loop.py`: solo lee los mensajes que el loop ya escribió
    (bloques `tool_use` del asistente, emparejados por `tool_use_id` con los
    `tool_result` que el propio loop generó al ejecutar la tool).
    """
    pending: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for message in new_messages:
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "tool_result":
                    call = pending.get(block.get("tool_use_id"))
                    if call is not None:
                        call["result"] = str(block.get("content"))
                        call["is_error"] = bool(block.get("is_error", False))
                continue
            if getattr(block, "type", None) == "tool_use":
                pending[block.id] = {
                    "name": block.name,
                    "input": block.input,
                    "result": "",
                    "is_error": False,
                }
                order.append(block.id)

    return [ToolCallInfo(**pending[tool_use_id]) for tool_use_id in order]
