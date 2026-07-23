
from abc import ABC, abstractmethod

from app.integrations.hotel.schemas import HotelQuery, HotelResult

class HotelProvider(ABC):
    @abstractmethod
    async def search_hotels(self, query: HotelQuery) -> HotelResult: 
        ...