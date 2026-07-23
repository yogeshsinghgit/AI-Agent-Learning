from dataclasses import dataclass

from app.domains.ai.runtime_dependencies.checkpointer import CheckpointerClient
from app.domains.ai.llms.client import LLMClient
from app.core.config import settings
from app.db.redis_client import RedisClient

from app.domains.ai.runtime_dependencies.graph_context import GraphContext


from app.integrations.geocoding.providers.open_meteo import OpenMeteoGeocodingProvider
from app.integrations.geocoding.client import GeocodingClient

from app.integrations.weather.providers.open_meteo import OpenMeteoWeatherProvider
from app.integrations.weather.client import WeatherClient
from app.integrations.weather.tool import WeatherTool

from app.integrations.attraction.client import AttractionClient
from app.integrations.attraction.tool import AttractionTool
from app.integrations.attraction.providers.open_trip_map import OpenTripMapAttractionProvider

from app.integrations.hotel.client import HotelClient
from app.integrations.hotel.tool import HotelTool
from app.integrations.hotel.providers.hotel_beds import HotelbedsHotelProvider


@dataclass(slots=True, frozen=True)
class AgentRuntime:
    """
    Shared runtime dependencies for all AI agents.
    """

    llm: LLMClient
    checkpointer: CheckpointerClient
    redis: RedisClient

    def create_graph_context(self) -> GraphContext:
        """
        Build the execution context passed to LangGraph nodes.
        """

        # instantiate geocode dependencies
        geocode_provider = OpenMeteoGeocodingProvider()
        geocoding_client = GeocodingClient(provider=geocode_provider)

        # Instantiate weather dependencies
        provider = OpenMeteoWeatherProvider(geocoding_client=geocoding_client)
        client = WeatherClient(provider=provider)
        weather_tool = WeatherTool(client=client)

        # Instantiate attraction dependencies
        provider = OpenTripMapAttractionProvider(
            api_key=settings.OPEN_TRIP_MAP_API, 
            geocoding_client=geocoding_client
        )
        client = AttractionClient(provider=provider)
        attraction_tool = AttractionTool(client=client)

        # Instantiate Hotel search dependencies

        provider = HotelbedsHotelProvider(
            api_key=settings.HOTELBEDS_API_KEY,
            secret=settings.HOTELBEDS_SECRET,
            geocoding_client=geocoding_client
        )
        client = HotelClient(provider)
        hotel_tool = HotelTool(client = client)

        tools = [weather_tool, attraction_tool, hotel_tool]

        tool_registry = {
            weather_tool.name: weather_tool,
            attraction_tool.name: attraction_tool,
            hotel_tool.name: hotel_tool
            }

        return GraphContext(
            llm=self.llm.client,
            redis=self.redis.client,
            tools=tools,
            tool_registry=tool_registry,
        )
