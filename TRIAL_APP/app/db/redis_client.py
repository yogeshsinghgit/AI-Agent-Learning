from redis.asyncio import Redis

from app.core.config import settings


class RedisClient:
    """
    Application wrapper around Redis.
    """

    def __init__(self) -> None:
        self._client: Redis | None = None

    async def connect(self) -> None:

        if self._client is not None:
            return

        self._client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

        await self._client.ping()

    async def disconnect(self) -> None:

        if self._client is None:
            return

        await self._client.close()

        self._client = None

    @property
    def client(self) -> Redis:

        if self._client is None:
            raise RuntimeError(
                "Redis is not connected."
            )

        return self._client