"""
Known place names that Open-Meteo's free geocoder resolves
incorrectly or not at all (states/regions rather than cities,
ambiguous short names, etc.). Checked before every geocode call.
Add to this as you discover more through testing.
"""

REGION_ALIASES: dict[str, str] = {
    "goa": "Panaji",
}


def resolve_alias(location: str) -> str:
    return REGION_ALIASES.get(location.strip().lower(), location)