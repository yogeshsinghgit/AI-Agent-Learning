import hashlib
import time

import httpx

from app.core.config import settings

from app.integrations.geocoding.client import GeocodingClient
from app.integrations.hotel.base import HotelProvider
from app.integrations.hotel.exceptions import HotelProviderError
from app.integrations.hotel.schemas import Hotel, HotelQuery, HotelResult


class HotelbedsHotelProvider(HotelProvider):
    """
    Adapter over Hotelbeds' Booking API (Apitude suite, free
    Evaluation Plan tier). Uses geolocation-based search so we can
    reuse the shared GeocodingClient instead of Hotelbeds' own
    destination-code lookup.
    https://developer.hotelbeds.com/
    """

    def __init__(
        self,
        api_key: str,
        secret: str,
        geocoding_client: GeocodingClient,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._secret = secret
        self._geocoding_client = geocoding_client
        self._client = client or httpx.AsyncClient(timeout=15.0)

    def _build_headers(self) -> dict:
        timestamp = str(int(time.time()))
        signature = hashlib.sha256(
            f"{self._api_key}{self._secret}{timestamp}".encode()
        ).hexdigest()

        return {
            "Api-key": self._api_key,
            "X-Signature": signature,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def search_hotels(self, query: HotelQuery) -> HotelResult:
        location = await self._geocoding_client.geocode(
            query.location, country=query.country
        )

        response = await self._client.post(
            settings.HOTEL_BEDS_HOTEL_SEARCH_URL,
            headers=self._build_headers(),
            json={
                "stay": {"checkIn": query.date_from, "checkOut": query.date_to},
                "occupancies": [{"rooms": 1, "adults": query.adults, "children": 0}],
                "geolocation": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "radius": 20,
                    "unit": "km",
                },
                "filter": {"maxHotels": query.limit},
            },
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = response.json().get("error", {}).get("message", str(exc))
            raise HotelProviderError(f"Hotelbeds search failed: {detail}") from exc

        results = response.json().get("hotels", {}).get("hotels", [])

        if not results:
            raise HotelProviderError(f"No hotels found near '{query.location}'.")

        hotels = [
            Hotel(
                name=item.get("name", "Unknown hotel"),
                rating=float(item["categoryName"].split()[0])
                    if item.get("categoryName", "").split()[:1]
                    and item["categoryName"].split()[0].replace(".", "").isdigit()
                    else None,
                price_per_night=float(item["minRate"]) if item.get("minRate") else None,
                currency=item.get("currency"),
                address=item.get("zoneName"),
            )
            for item in results[: query.limit]
        ]

        return HotelResult(location=location.name, hotels=hotels)