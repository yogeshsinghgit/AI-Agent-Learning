from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.integrations.hotel.client import HotelClient
from app.integrations.hotel.exceptions import HotelProviderError
from app.integrations.geocoding.exceptions import GeocodingError


class HotelToolInput(BaseModel):
    location: str = Field(
        description="City name only, e.g. 'Goa', 'Delhi'. No landmarks or qualifiers."
    )
    country: str | None = Field(
        default=None,
        description="ISO 3166-1 alpha-2 code, e.g. 'IN'. Never the full country name.",
    )
    date_from: str = Field(description="Check-in date, YYYY-MM-DD.")
    date_to: str = Field(description="Check-out date, YYYY-MM-DD.")
    adults: int = Field(default=1, ge=1, description="Number of guests.")
    limit: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Maximum number of hotels to return.",
    )


class HotelToolOutput(BaseModel):
    location: str
    hotels: list[dict]


class HotelTool(BaseTool):
    """
    Class-based tool adapting AttractionClient to LangChain's tool
    interface. The client is injected at construction time (DI).
    """

    name: str = "hotels_search"
    description: str = (
        "Find hotels near a city or destination "
        "Always use this tool to find real hotels — do not rely on your own knowledge, as this returns verified, current data."
    )
    args_schema: Type[BaseModel] = HotelToolInput

    client: HotelClient

    model_config = {"arbitrary_types_allowed": True}

    def _run(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError("HotelTool only supports async execution.")

    async def _arun(
        self,
        location: str,
        date_from: str,
        date_to: str,
        country: str | None = None,
        adults: int = 1,
        limit: int = 5,
    ) -> str:
        try:
            result = await self.client.search_hotels(
                location=location,
                date_from=date_from,
                date_to=date_to,
                country=country,
                adults=adults,
                limit=limit,
            )
        except (HotelProviderError, GeocodingError) as exc:
            return f"Could not find hotels: {exc}"

        output = HotelToolOutput(
            location=result.location,
            hotels=[h.model_dump() for h in result.hotels],
        )
        return output.model_dump_json()
