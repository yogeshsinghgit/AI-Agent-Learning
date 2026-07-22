from dataclasses import dataclass

from app.domains.ai.runtime_dependencies.checkpointer import CheckpointerClient
from app.domains.ai.llms.client import LLMClient
from app.core.config import settings
from app.db.redis_client import RedisClient

from app.domains.ai.runtime_dependencies.graph_context import GraphContext
from app.integrations.weather.providers.open_meteo import OpenMeteoWeatherProvider
from app.integrations.weather.client import WeatherClient
from app.integrations.weather.tool import WeatherTool


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
        # Instantiate weather dependencies
        provider = OpenMeteoWeatherProvider()
        client = WeatherClient(provider=provider)
        weather_tool = WeatherTool(client=client)

        tools = [weather_tool]
        tool_registry = {weather_tool.name: weather_tool}

        return GraphContext(
            llm=self.llm.client,
            redis=self.redis.client,
            tools=tools,
            tool_registry=tool_registry,
        )
