from abc import ABC, abstractmethod

from app.integrations.weather.schemas import WeatherQuery, WeatherResult


class WeatherProvider(ABC):
    """
    Port for weather service providers.

    Every weather provider (Open-Meteo, WeatherAPI, Tomorrow.io, etc.)
    must implement this interface and return a vendor-agnostic
    WeatherResult.
    """

    @abstractmethod
    async def get_weather(
        self,
        query: WeatherQuery,
    ) -> WeatherResult:
        """
        Fetch the weather forecast for the requested location and
        date range.

        If no date range is provided, the provider should default to
        today's forecast.
        """
        ...