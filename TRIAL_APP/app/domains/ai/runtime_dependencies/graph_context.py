from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from redis.asyncio import Redis



@dataclass(slots=True, frozen=True)
class GraphContext:
    """
    Dependencies required during graph execution.

    This object is injected into every LangGraph node so that node
    signatures remain stable as new dependencies are introduced.
    """

    llm: BaseChatModel
    redis: Redis
    # tools: list[BaseTool]
    # tool_registry: dict[str, BaseTool]