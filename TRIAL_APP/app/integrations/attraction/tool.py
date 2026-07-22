from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.integrations.attraction.client import AttractionClient
from app.integrations.attraction.exceptions import AttractionProviderError


class AttractionToolInput(BaseModel):
    location: str = Field(
        description="City or destination to find tourist attractions in, e.g. 'Goa'."
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=30,
        description="Maximum number of attractions to return.",
    )


class AttractionToolOutput(BaseModel):
    location: str
    attractions: list[dict]


class AttractionTool(BaseTool):
    """
    Class-based tool adapting AttractionClient to LangChain's tool
    interface. The client is injected at construction time (DI).
    """

    name: str = "attraction_search"
    description: str = (
        "Find tourist attractions, landmarks, and points of interest "
        "near a city or destination."
    )
    args_schema: Type[BaseModel] = AttractionToolInput

    client: AttractionClient

    model_config = {"arbitrary_types_allowed": True}

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("AttractionTool only supports async execution.")

    async def _arun(self, location: str, limit: int = 10) -> str:
        try:
            result = await self.client.search_attractions(location, limit)
        except AttractionProviderError as exc:
            # Goes back to the LLM as a ToolMessage — it can now
            # apologize, ask the user to clarify, or retry with a
            # cleaner location string instead of crashing the request.
            return f"Could not find attractions: {exc}"

        output = AttractionToolOutput(
            location=result.location,
            attractions=[a.model_dump() for a in result.attractions],
        )

        return output.model_dump_json()
