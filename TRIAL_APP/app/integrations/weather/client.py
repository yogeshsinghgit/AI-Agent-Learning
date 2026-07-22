from loguru import logger

from app.capabilities.weather.provider import WeatherProvider
from app.capabilities.weather.schemas import WeatherQuery, WeatherResult


class WeatherClient:
    """
    Combined Agent and Service layer for the weather capability.
    Coordinates query processing and integrates with the external provider.
    """

    def __init__(self, provider: WeatherProvider) -> None:
        self._provider = provider

    async def get_weather(self, location: str) -> WeatherResult:
        logger.info("Fetching weather for '{}'.", location)

        result = await self._provider.get_current_weather(
            WeatherQuery(location=location)
        )

        logger.success(
            "Weather fetched for '{}': {}°C, {}.",
            result.location,
            result.temperature_celsius,
            result.weather_description,
        )

        return result
