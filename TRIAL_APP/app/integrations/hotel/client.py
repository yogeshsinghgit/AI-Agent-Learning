from loguru import logger

from app.integrations.hotel.base import HotelProvider
from app.integrations.hotel.schemas import HotelQuery, HotelResult


class HotelClient:
    """
    Combined Agent and Service layer for the hotel search capability.
    Coordinates query processing and integrates with the external provider.
    """

    def __init__(self, provider: HotelProvider) -> None:
        self._provider = provider

    async def search_hotels(
        self,
        location: str,
        date_from: str,
        date_to: str,
        country: str | None = None,
        adults: int = 1,
        limit: int = 5,
    ) -> HotelResult:
        logger.info("Searching hotels near '{}'.", location)

        result = await self._provider.search_hotels(
            HotelQuery(
                location=location,
                country=country,
                date_from=date_from,
                date_to=date_to,
                adults=adults,
                limit=limit,
            )
        )

        logger.success("Found {} hotels near '{}'.", len(result.hotels), result.location)
        return result