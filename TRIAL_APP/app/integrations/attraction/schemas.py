from pydantic import BaseModel, Field


class AttractionQuery(BaseModel):
    """Input to any AttractionProvider. Deliberately vendor-agnostic."""

    location: str = Field(
        description=(
            "The city or town name only — e.g. 'Delhi', 'Goa', 'Paris'. "
            "Do NOT include landmarks, directions, or qualifiers like "
            "'near X' or 'around Y'. If the user mentions a specific "
            "landmark, extract just the city it's in."
        )
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=30,
        description="Maximum number of attractions to return.",
    )


class Attraction(BaseModel):
    name: str
    category: str
    distance_meters: float | None = None


class AttractionResult(BaseModel):
    location: str
    attractions: list[Attraction]
