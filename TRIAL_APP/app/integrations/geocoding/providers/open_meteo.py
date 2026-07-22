import httpx

from app.core.config import settings
from app.integrations.geocoding.base import GeocodingProvider
from app.integrations.geocoding.exceptions import GeocodingError
from app.integrations.geocoding.schemas import GeocodeQuery, GeocodeResult


class OpenMeteoGeocodingProvider(GeocodingProvider):
    """
    Adapter over Open-Meteo's free geocoding API. No API key required.
    https://open-meteo.com/en/docs/geocoding-api
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0)

    async def geocode(self, query: GeocodeQuery) -> GeocodeResult:
        params = {"name": query.location, "count": 1}

        if query.country:
            params["countryCode"] = query.country

        response = await self._client.get(settings.GEOCODING_URL, params=params)
        response.raise_for_status()

        results = response.json().get("results")

        if not results:
            raise GeocodingError(
                f"No location found for '{query.location}'."
            )

        match = results[0]

        return GeocodeResult(
            name=match["name"],
            country=match.get("country"),
            latitude=match["latitude"],
            longitude=match["longitude"],
        )