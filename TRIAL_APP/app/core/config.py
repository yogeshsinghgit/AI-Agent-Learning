from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    ####################################################################
    # Application
    ####################################################################

    APP_NAME: str = "AI Travel Agent"

    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: str = Field(default="development")

    DEBUG: bool = True

    ####################################################################
    # Server
    ####################################################################

    HOST: str = "0.0.0.0"

    PORT: int = 8000

    ####################################################################
    # Groq
    ####################################################################

    GROQ_API_KEY: str
    LLM_PROVIDER: str = "groq"

    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"

    TEMPERATURE: float = 0.2

    MAX_TOKENS: int = 2048

    ####################################################################
    # OpenTripMap (Attractions)
    ####################################################################

    OPEN_TRIP_MAP_API: str 

    ####################################################################
    # PostgreSQL
    ####################################################################

    POSTGRES_HOST: str

    POSTGRES_PORT: int = 5432

    POSTGRES_DB: str

    POSTGRES_USER: str

    POSTGRES_PASSWORD: str

    ####################################################################
    # Redis
    ####################################################################

    REDIS_HOST: str

    REDIS_PORT: int = 6379

    REDIS_PASSWORD: str = ""

    ####################################################################
    # Logging
    ####################################################################

    LOG_LEVEL: str = "INFO"


    ##################################################################
    # External APIs and Config's
    ##################################################################
    # open meteo apis
    GEOCODING_URL: str 
    FORECAST_URL: str
    # open trip map api and constants
    GEONAME_URL: str
    RADIUS_URL: str

    DEFAULT_RADIUS_METERS : int 

    ####################################################################
    # Computed Properties
    ####################################################################

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return (
                f"redis://:{self.REDIS_PASSWORD}"
                f"@{self.REDIS_HOST}:{self.REDIS_PORT}"
            )

        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()