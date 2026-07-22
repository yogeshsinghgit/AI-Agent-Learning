from datetime import date as dt_date

from pydantic import BaseModel, Field, model_validator


class WeatherQuery(BaseModel):
    """
    Vendor-agnostic weather request.

    If no dates are provided, the provider will default the request to
    today's date and return a single-day forecast.
    """

    location: str = Field(
        description="City or destination name for which weather information is requested."
    )

    country: str | None = Field(
        default=None,
        description="Optional country name used to disambiguate locations with the same name."
    )

    date_from: dt_date | None = Field(
        default=None,
        description="Start date of the requested weather forecast."
    )

    date_to: dt_date | None = Field(
        default=None,
        description="End date of the requested weather forecast."
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "WeatherQuery":
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from > self.date_to
        ):
            raise ValueError(
                "'date_from' cannot be greater than 'date_to'."
            )

        return self


class DailyWeatherForecast(BaseModel):
    """
    Weather forecast for a single calendar day.
    """

    date: dt_date = Field(
        description="Forecast date."
    )

    minimum_temperature_celsius: float = Field(
        description="Minimum expected temperature in degrees Celsius."
    )

    maximum_temperature_celsius: float = Field(
        description="Maximum expected temperature in degrees Celsius."
    )

    weather_description: str = Field(
        description="Human-readable description of the expected weather conditions."
    )

    precipitation_probability: int | None = Field(
        default=None,
        description="Maximum probability of precipitation for the day as a percentage."
    )

    maximum_windspeed_kmh: float | None = Field(
        default=None,
        description="Maximum expected wind speed in kilometers per hour."
    )


class WeatherResult(BaseModel):
    """
    Vendor-agnostic weather response returned by all weather providers.
    """

    location: str = Field(
        description="Resolved location name."
    )

    latitude: float = Field(
        description="Latitude of the resolved location."
    )

    longitude: float = Field(
        description="Longitude of the resolved location."
    )

    forecasts: list[DailyWeatherForecast] = Field(
        description="Daily weather forecast for the requested date range."
    )