from pydantic import BaseModel, Field

class HotelQuery(BaseModel):
    """Input to any HotelProvider. Vendor-agnostic."""
    location: str = Field(description="City name only, e.g. 'Delhi'.")
    country: str | None = Field(default=None, description="ISO 3166-1 alpha-2 code, e.g. 'IN'.")
    date_from: str = Field(description="YYYY-MM-DD.")
    date_to: str = Field(description="YYYY-MM-DD.")
    adults: int = Field(default=1, description="Number of guests.")
    limit: int = Field(default=5, description="Max results to return.")

class Hotel(BaseModel):
    name: str
    rating: float | None = None
    price_per_night: float | None = None
    currency: str | None = None
    address: str | None = None

class HotelResult(BaseModel):
    location: str
    hotels: list[Hotel]