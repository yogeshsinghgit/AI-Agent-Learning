from loguru import logger

from app.domains.ai.runtime_dependencies.graph_context import GraphContext
from app.domains.graph.state import AgentState, TripPreferences


class ExtractPreferencesNode:
    """
    Runs before the agent node. Scans the conversation so far and
    pulls out any trip-planning details the user has provided,
    merging them into existing state rather than overwriting it.
    """

    def __init__(self, context: GraphContext) -> None:
        self._extractor = context.llm.with_structured_output(TripPreferences)

    async def __call__(self, state: AgentState) -> dict:
        logger.info("ExtractPreferencesNode: Extracting trip preferences...")

        extracted = await self._extractor.ainvoke(state["messages"])

        existing = state.get("trip_preferences", {}) or {}
        merged = {
            **existing,
            **{k: v for k, v in extracted.items() if v},
        }

        logger.info("ExtractPreferencesNode: Merged preferences: {}", merged)

        return {"trip_preferences": merged}