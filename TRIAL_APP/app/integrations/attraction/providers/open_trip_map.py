import httpx

from app.core.config import settings

from app.integrations.geocoding.client import GeocodingClient
from app.integrations.attraction.exceptions import AttractionProviderError
from app.integrations.attraction.base import AttractionProvider
from app.integrations.attraction.schemas import Attraction, AttractionQuery, AttractionResult



class OpenTripMapAttractionProvider(AttractionProvider):
    """
    Adapter over the OpenTripMap API (free tier, requires a free API
    key from https://dev.opentripmap.org/product).
    """

    def __init__(
        self,
        api_key: str,
        geocoding_client: GeocodingClient,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._geocoding_client = geocoding_client
        self._client = client or httpx.AsyncClient(timeout=10.0)

    async def search_attractions(self, query: AttractionQuery) -> AttractionResult:
        coordinates = await self._geocoding_client.geocode(query.location)

        attractions = await self._search_radius(
            latitude=coordinates.latitude,
            longitude=coordinates.longitude,
            limit=query.limit,
        )

        return AttractionResult(
            # location=coordinates.get("name", query.location),
            location= coordinates.name,
            attractions=attractions,
        )

    async def _search_radius(
        self,
        latitude: float,
        longitude: float,
        limit: int,
    ) -> list[Attraction]:
        response = await self._client.get(
            settings.RADIUS_URL,
            params={
                "radius": settings.DEFAULT_RADIUS_METERS,
                "lat": latitude,
                "lon": longitude,
                "limit": limit,
                "rate": 2,
                "format": "json",
                "apikey": self._api_key,
            },
        )
        response.raise_for_status()

        return [
            Attraction(
                name=item.get("name") or "Unnamed attraction",
                category=(item.get("kinds") or "").split(",")[0] or "general",
                distance_meters=item.get("dist"),
            )
            for item in response.json()
            if item.get("name")
        ]
