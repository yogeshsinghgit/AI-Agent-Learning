from pydantic import BaseModel, Field


class GeocodeQuery(BaseModel):
    """Input to any GeocodingProvider. Vendor-agnostic."""

    location: str = Field(
        description="Place name to resolve, e.g. 'Delhi' or 'Goa'."
    )
    country: str | None = Field(
        default=None,
        description=(
            "Optional ISO country code (e.g. 'IN', 'FR') to disambiguate "
            "places that share a name across countries."
        ),
    )


class GeocodeResult(BaseModel):
    """
    Output from any GeocodingProvider.

    Every adapter must map its vendor-specific response into this
    shape. Nothing above the geocoding layer ever sees vendor-specific
    fields.
    """

    name: str
    country: str | None = None
    latitude: float
    longitude: float