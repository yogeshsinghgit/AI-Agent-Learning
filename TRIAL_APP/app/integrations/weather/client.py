from loguru import logger

from app.integrations.weather.providers.base import WeatherProvider
from app.integrations.weather.schemas import WeatherQuery, WeatherResult


class WeatherClient:
    """
    Combined Agent and Service layer for the weather capability.
    Coordinates query processing and integrates with the external provider.
    """

    def __init__(self, provider: WeatherProvider) -> None:
        self._provider = provider

    async def get_weather(self, query: WeatherQuery | str) -> WeatherResult:
        if isinstance(query, str):
            query = WeatherQuery(location=query)

        logger.info("Fetching weather for '{}'.", query.location)

        result = await self._provider.get_weather(query)

        temp_info = ""
        if result.forecasts:
            first = result.forecasts[0]
            temp_info = f" Min: {first.minimum_temperature_celsius}°C, Max: {first.maximum_temperature_celsius}°C, {first.weather_description}"

        logger.success(
            "Weather fetched for '{}':{}",
            result.location,
            temp_info,
        )

        return result
