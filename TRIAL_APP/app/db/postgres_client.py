from psycopg import AsyncConnection
from psycopg.rows import dict_row

from app.core.config import settings


class PostgresClient:
    """
    Application wrapper around PostgreSQL.
    """

    def __init__(self) -> None:
        self._connection: AsyncConnection | None = None

    async def connect(self) -> None:

        if self._connection is not None:
            return

        self._connection = await AsyncConnection.connect(
            conninfo=settings.postgres_url.replace(
                "postgresql+asyncpg",
                "postgresql",
            ),
            row_factory=dict_row,
            autocommit=True,
        )

    async def disconnect(self) -> None:

        if self._connection is None:
            return

        await self._connection.close()

        self._connection = None

    @property
    def connection(self) -> AsyncConnection:

        if self._connection is None:
            raise RuntimeError(
                "PostgreSQL is not connected."
            )

        return self._connection