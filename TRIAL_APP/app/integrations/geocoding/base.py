from abc import ABC, abstractmethod

from app.integrations.geocoding.schemas import GeocodeQuery, GeocodeResult


class GeocodingProvider(ABC):
    """
    Port: anything that can resolve a place name to coordinates
    implements this. GeocodingClient depends only on this interface,
    never on a concrete vendor.
    """

    @abstractmethod
    async def geocode(self, query: GeocodeQuery) -> GeocodeResult:
        """Resolve a location name to coordinates."""