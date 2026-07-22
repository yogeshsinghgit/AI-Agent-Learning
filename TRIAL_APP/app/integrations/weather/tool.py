from datetime import date
from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.integrations.weather.client import WeatherClient
from app.integrations.weather.schemas import WeatherQuery


class WeatherToolInput(BaseModel):
    """
    Input schema for the weather tool.
    """

    location: str = Field(
        description="City or destination for which the weather forecast is required."
    )

    country: str | None = Field(
        default=None,
        description="Optional country name used to disambiguate locations."
    )

    date_from: date | None = Field(
        default=None,
        description="Start date of the weather forecast."
    )

    date_to: date | None = Field(
        default=None,
        description="End date of the weather forecast."
    )


class WeatherTool(BaseTool):
    """
    LangChain tool for retrieving weather forecasts.

    This tool delegates all business logic to WeatherClient and simply
    adapts it to LangChain's tool interface.
    """

    name: str = "weather_lookup"

    description: str = (
        "Get the weather forecast for a destination. "
        "Use this tool whenever weather conditions may affect travel planning, "
        "packing recommendations, or outdoor activities."
    )

    args_schema: Type[BaseModel] = WeatherToolInput

    client: WeatherClient

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError(
            "WeatherTool only supports asynchronous execution."
        )

    async def _arun(
        self,
        location: str,
        country: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> str:

        query = WeatherQuery(
            location=location,
            country=country,
            date_from=date_from,
            date_to=date_to,
        )

        result = await self.client.get_weather(query)

        return result.model_dump_json(indent=2)