from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from redis.asyncio import Redis


from app.domains.ai.runtime_dependencies.runtime import AgentRuntime
from app.domains.graph.builder import build_graph

from app.core.config import settings
from app.core.logging import configure_logging
from app.domains.dependencies.app_state import AppState

from app.db.postgres_client import PostgresClient
from app.db.redis_client import RedisClient
from app.domains.ai.runtime_dependencies.checkpointer import CheckpointerClient
from app.domains.ai.llms.client import LLMClient




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize and dispose application resources.
    """

    configure_logging()

    logger.info("Starting AI Travel Agent...")

    app_state = AppState()

    try:

        app_state.postgres = PostgresClient()
        await app_state.postgres.connect()
        logger.success("Postgres Connected")

        logger.info("Connecting to Redis...")
        app_state.redis = RedisClient()
        await app_state.redis.connect()
        logger.success("Redis connected successfully.")

        app_state.llm = LLMClient()
        await app_state.llm.connect()
        logger.success("LLM Connected")

        app_state.checkpointer = CheckpointerClient(
            postgres=app_state.postgres
        )
        await app_state.checkpointer.connect()
        logger.success("Checkpointer Ready")

        # app_state.travel_agent = TravelAgent(
        #     llm=app_state.llm.client,
        #     checkpointer=app_state.checkpointer.client,
        # )
        # logger.success("Travel agent initialized.")
        runtime = AgentRuntime(
            llm=app_state.llm,
            checkpointer=app_state.checkpointer,
            redis=app_state.redis,
        )

        graph_context = runtime.create_graph_context()
        app_state.graph = build_graph(
            context=graph_context,
            checkpointer=app_state.checkpointer.client,
        )

        app.state.app_state = app_state

        logger.success("Application startup completed.")

        yield

    except Exception as exc:
        logger.exception(f"Application startup failed: {exc}")
        raise

    finally:
        logger.info("Shutting down application...")

        if app_state.checkpointer is not None:
            await app_state.checkpointer.disconnect()

        if app_state.llm is not None:
            await app_state.llm.disconnect()

        if app_state.redis is not None:
            await app_state.redis.disconnect()

        if app_state.postgres is not None:
            await app_state.postgres.disconnect()

        logger.success("Application shutdown completed.")