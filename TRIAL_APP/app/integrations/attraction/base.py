from abc import ABC, abstractmethod

from app.integrations.attraction.schemas import AttractionQuery, AttractionResult


class AttractionProvider(ABC):
    """
    Port: anything that can list tourist attractions near a place
    implements this. AttractionClient depends only on this interface,
    never on a concrete vendor.
    """

    @abstractmethod
    async def search_attractions(self, query: AttractionQuery) -> AttractionResult:
        """Return nearby tourist attractions for the given location."""
