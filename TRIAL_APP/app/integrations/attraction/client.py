from loguru import logger

from app.integrations.attraction.base import AttractionProvider
from app.integrations.attraction.schemas import AttractionQuery, AttractionResult


class AttractionClient:
    """
    Combined Agent and Service layer for the attraction capability.
    Coordinates query processing and integrates with the external provider.
    """

    def __init__(self, provider: AttractionProvider) -> None:
        self._provider = provider

    async def search_attractions(
        self,
        location: str,
        limit: int = 10,
    ) -> AttractionResult:
        logger.info("Searching attractions near '{}'.", location)

        result = await self._provider.search_attractions(
            AttractionQuery(location=location, limit=limit)
        )

        logger.success(
            "Found {} attractions near '{}'.",
            len(result.attractions),
            result.location,
        )

        return result
