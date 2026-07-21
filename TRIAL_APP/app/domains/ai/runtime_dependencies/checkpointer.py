from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.db.postgres_client import PostgresClient


class CheckpointerClient:
    """
    Wrapper around LangGraph's PostgreSQL checkpointer.
    """

    def __init__(
        self,
        postgres: PostgresClient,
    ) -> None:
        self._postgres = postgres
        self._client: AsyncPostgresSaver | None = None

    async def connect(self) -> None:

        if self._client is not None:
            return

        self._client = AsyncPostgresSaver(
            self._postgres.connection,
        )

        # Creates checkpointer tables if they don't already exist.
        # setup() uses CREATE TABLE IF NOT EXISTS so it's safe to call every startup.
        await self._client.setup()

    async def disconnect(self) -> None:
        # AsyncPostgresSaver doesn't currently own the DB connection,
        # so there's nothing to close here.
        self._client = None

    @property
    def client(self) -> AsyncPostgresSaver:

        if self._client is None:
            raise RuntimeError(
                "Checkpointer is not initialized."
            )

        return self._client