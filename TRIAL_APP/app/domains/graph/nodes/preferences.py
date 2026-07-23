from loguru import logger
from langchain_core.messages import trim_messages
from app.domains.ai.runtime_dependencies.graph_context import GraphContext
from app.domains.graph.state import AgentState, TripPreferences
from app.domains.ai.utils.token_counter_helper import token_counter


class ExtractPreferencesNode:
    """
    Runs before the agent node. Scans the conversation so far and
    pulls out any trip-planning details the user has provided,
    merging them into existing state rather than overwriting it.
    """

    def __init__(self, context: GraphContext) -> None:
        self._context = context
        self._extractor = context.llm.with_structured_output(TripPreferences)

    async def __call__(self, state: AgentState) -> dict:
        logger.info("ExtractPreferencesNode: Extracting trip preferences...")

        trimmed = trim_messages(
            state["messages"],
            max_tokens=4000,          # tune to your model's context window
            strategy="last",           # keep most recent messages
            token_counter=token_counter,  # uses the model's own tokenizer
            include_system=True,
            start_on="human",          # avoid cutting mid tool-call/response pair
        )
        messages = list(trimmed)

        extracted = await self._extractor.ainvoke(messages)

        existing = state.get("trip_preferences", {}) or {}
        merged = {
            **existing,
            **{k: v for k, v in extracted.items() if v},
        }

        logger.info("ExtractPreferencesNode: Merged preferences: {}", merged)

        return {"trip_preferences": merged}