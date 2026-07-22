from datetime import date
from typing import Any

import httpx
from loguru import logger

from app.core.config import settings
from app.core.weather_codes import _WEATHER_CODES

from app.integrations.weather.exceptions import WeatherProviderError
from app.integrations.weather.providers.base import WeatherProvider
from app.integrations.weather.schemas import (
    DailyWeatherForecast,
    WeatherQuery,
    WeatherResult,
)



class OpenMeteoWeatherProvider(WeatherProvider):
    """
    Open-Meteo weather provider.

    Responsibilities:
        - Resolve a location into coordinates.
        - Fetch forecast data.
        - Map Open-Meteo responses into vendor-agnostic models.
    """

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0)

    async def get_weather(
        self,
        query: WeatherQuery,
    ) -> WeatherResult:

        logger.info(
            "Fetching weather forecast for '{}'.",
            query.location,
        )

        location = await self._geocode(query)

        start_date = query.date_from or date.today()
        end_date = query.date_to or start_date

        forecast = await self._get_forecast(
            latitude=location["latitude"],
            longitude=location["longitude"],
            start_date=start_date,
            end_date=end_date,
        )

        result = self._map_weather(
            location=location,
            forecast=forecast,
        )

        logger.success(
            "Weather forecast fetched successfully for '{}'.",
            result.location,
        )

        return result

    async def aclose(self) -> None:
        """
        Close the underlying HTTP client.
        """
        await self._client.aclose()

    async def _geocode(
        self,
        query: WeatherQuery,
    ) -> dict[str, Any]:

        params = {
            "name": query.location,
            "count": 1,
        }

        try:
            response = await self._client.get(
                settings.GEOCODING_URL,
                params=params,
            )
            response.raise_for_status()

        except httpx.HTTPError as exc:
            logger.exception(
                "Failed to geocode location '{}'.",
                query.location,
            )
            raise WeatherProviderError(
                "Unable to resolve the requested location."
            ) from exc

        results = response.json().get("results")

        if not results:
            raise WeatherProviderError(
                f"No location found for '{query.location}'."
            )

        return results[0]

    async def _get_forecast(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> dict[str, Any]:

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "auto",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "weather_code",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                ]
            ),
        }

        logger.info(
            "Sending forecast request to Open-Meteo: URL={}, params={}",
            settings.FORECAST_URL,
            params,
        )

        try:
            response = await self._client.get(
                settings.FORECAST_URL,
                params=params,
            )

            if response.status_code != 200:
                logger.error(
                    "Open-Meteo request failed with status {}: {}",
                    response.status_code,
                    response.text,
                )

            response.raise_for_status()

        except httpx.HTTPError as exc:
            logger.exception(
                "Failed to fetch forecast from Open-Meteo with params: {}",
                params,
            )
            raise WeatherProviderError(
                "Unable to fetch weather forecast."
            ) from exc

        return response.json()

    def _map_weather(
        self,
        *,
        location: dict[str, Any],
        forecast: dict[str, Any],
    ) -> WeatherResult:

        daily = forecast["daily"]

        forecasts: list[DailyWeatherForecast] = []

        for index, forecast_date in enumerate(daily["time"]):
            forecasts.append(
                DailyWeatherForecast(
                    date=forecast_date,
                    minimum_temperature_celsius=daily["temperature_2m_min"][index],
                    maximum_temperature_celsius=daily["temperature_2m_max"][index],
                    weather_description=_WEATHER_CODES.get(
                        daily["weather_code"][index],
                        "Unknown",
                    ),
                    precipitation_probability=daily[
                        "precipitation_probability_max"
                    ][index],
                    maximum_windspeed_kmh=daily[
                        "wind_speed_10m_max"
                    ][index],
                )
            )

        return WeatherResult(
            location=location["name"],
            latitude=location["latitude"],
            longitude=location["longitude"],
            forecasts=forecasts,
        )