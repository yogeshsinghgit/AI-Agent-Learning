

import time
import httpx

from app.integrations.geocoding.client import GeocodingClient
from app.integrations.hotel.base import HotelProvider
from app.integrations.hotel.exceptions import HotelProviderError
from app.integrations.hotel.schemas import Hotel, HotelQuery, HotelResult

AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
HOTEL_LIST_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
HOTEL_OFFERS_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"


class AmadeusHotelProvider(HotelProvider):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        geocoding_client: GeocodingClient,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_secret = api_secret
        self._geocoding_client = geocoding_client
        self._client = client or httpx.AsyncClient(timeout=15.0)
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    async def _get_token(self) -> str:
        # Reuse the cached token until ~60s before expiry
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token

        response = await self._client.post(
            AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._api_key,
                "client_secret": self._api_secret,
            },
        )
        response.raise_for_status()
        data = response.json()

        self._token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"]
        return self._token

    async def search_hotels(self, query: HotelQuery) -> HotelResult:
        token = await self._get_token()
        headers = {"Authorization": f"Bearer {token}"}

        location = await self._geocoding_client.geocode(query.location, country=query.country)

        # Amadeus needs an IATA city code, not lat/lon — a separate
        # lookup step, distinct from weather/attraction's geocoding.
        city_code = await self._resolve_city_code(query.location, headers)

        hotel_ids = await self._get_hotel_ids(city_code, headers, limit=query.limit)

        if not hotel_ids:
            raise HotelProviderError(f"No hotels found near '{query.location}'.")

        offers = await self._get_offers(hotel_ids, query, headers)

        return HotelResult(location=location.name, hotels=offers)

    async def _resolve_city_code(self, location: str, headers: dict) -> str:
        response = await self._client.get(
            "https://test.api.amadeus.com/v1/reference-data/locations",
            params={"keyword": location, "subType": "CITY"},
            headers=headers,
        )
        response.raise_for_status()
        results = response.json().get("data")

        if not results:
            raise HotelProviderError(f"No city code found for '{location}'.")

        return results[0]["iataCode"]

    async def _get_hotel_ids(self, city_code: str, headers: dict, limit: int) -> list[str]:
        response = await self._client.get(
            HOTEL_LIST_URL,
            params={"cityCode": city_code},
            headers=headers,
        )
        response.raise_for_status()
        return [h["hotelId"] for h in response.json().get("data", [])[:limit]]

    async def _get_offers(self, hotel_ids: list[str], query: HotelQuery, headers: dict) -> list[Hotel]:
        response = await self._client.get(
            HOTEL_OFFERS_URL,
            params={
                "hotelIds": ",".join(hotel_ids),
                "checkInDate": query.check_in,
                "checkOutDate": query.check_out,
                "adults": query.adults,
            },
            headers=headers,
        )
        response.raise_for_status()

        hotels = []
        for entry in response.json().get("data", []):
            info = entry["hotel"]
            offer = entry.get("offers", [{}])[0]
            price = offer.get("price", {})
            hotels.append(
                Hotel(
                    name=info.get("name", "Unknown hotel"),
                    price_per_night=float(price["total"]) if price.get("total") else None,
                    currency=price.get("currency"),
                    address=", ".join(info.get("address", {}).get("lines", [])) or None,
                )
            )
        return hotels