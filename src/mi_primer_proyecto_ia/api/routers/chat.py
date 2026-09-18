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
from mi_primer_proyecto_ia.api.schemas import ChatRequest, ChatResponse
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

    try:
        reply = await run_in_threadpool(
            run_agent_turn, client, settings, history, request.message
        )
    except ToolIterationLimitError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(reply=reply, conversation_id=conversation_id)
