from dataclasses import dataclass

from app.domains.ai.runtime_dependencies.checkpointer import CheckpointerClient
from app.db.postgres_client import PostgresClient
from app.db.redis_client import RedisClient
from app.domains.ai.llms.client import LLMClient

@dataclass(slots=True)
class AppState:
    """
    Stores long-lived application resources.

    All shared dependencies should be initialized once during
    application startup and accessed through this object.
    """

    redis: RedisClient | None = None

    postgres: PostgresClient | None = None

    llm: LLMClient | None = None

    checkpointer: CheckpointerClient | None = None

    # Future additions:
    # postgres_pool: AsyncConnectionPool | None = None
    # checkpointer: AsyncPostgresSaver | None = None
    # llm: ChatGroq | None = None
    # weather_client: WeatherClient | None = None



    