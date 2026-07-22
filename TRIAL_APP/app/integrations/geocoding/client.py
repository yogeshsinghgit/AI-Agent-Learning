from loguru import logger

from app.integrations.geocoding.base import GeocodingProvider
from app.integrations.geocoding.exceptions import GeocodingError
from app.integrations.geocoding.schemas import GeocodeQuery, GeocodeResult


class GeocodingClient:
    """
    Thin wrapper around a GeocodingProvider. Shared by weather,
    attraction, and any future capability that needs to resolve a
    place name to coordinates.
    """

    def __init__(self, provider: GeocodingProvider) -> None:
        self._provider = provider

    async def geocode(
        self,
        location: str,
        country: str | None = None,
    ) -> GeocodeResult:
        logger.info("Geocoding '{}'.", location)

        result = await self._provider.geocode(
            GeocodeQuery(location=location, country=country)
        )

        logger.success(
            "Geocoded '{}' -> ({}, {}) [{}].",
            location,
            result.latitude,
            result.longitude,
            result.country,
        )

        return result