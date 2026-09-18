from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ToolCallInfo(BaseModel):
    """Una invocación de tool durante el turno, para que el frontend la muestre."""

    name: str
    input: dict[str, Any]
    result: str
    is_error: bool = False


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    tool_calls: list[ToolCallInfo] = []


class HealthResponse(BaseModel):
    status: str
    llm_backend: str
