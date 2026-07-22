from typing import Any
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.core.constants import DEFAULT_THREAD_ID
from app.domains.dependencies.providers import get_graph
from app.domains.api.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="The message to send to the travel agent."
    )
    thread_id: str = Field(
        default=DEFAULT_THREAD_ID,
        description="Optional thread ID to maintain conversational memory."
    )


class ChatResponse(BaseModel):
    response: str = Field(
        ...,
        description="The natural language response from the travel agent."
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    graph: Any = Depends(get_graph),
) -> ChatResponse:
    """
    Main chat route to communicate with the travel agent.
    Supports session continuity by specifying a custom thread_id.
    """
    chat_service = ChatService(graph=graph)
    response_content = await chat_service.send_message(
        message=request.message,
        thread_id=request.thread_id,
    )
    return ChatResponse(response=response_content)


@router.get("/test-llm")
async def test_llm(request: Request):
    llm = request.app.state.app_state.llm.client
    response = await llm.ainvoke("Say hello in 5 words.")
    return {"response": response.content}