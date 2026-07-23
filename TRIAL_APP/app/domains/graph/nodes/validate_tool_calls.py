from loguru import logger
from langchain_core.messages import AIMessage, ToolMessage

from app.domains.graph.state import AgentState
from app.domains.graph.utils.tool_requirements import TOOL_REQUIREMENTS


class ValidateToolCallsNode:
    """
    Runs after the agent proposes tool calls, before ToolNode executes
    them. Blocks any call whose required trip_preferences fields
    aren't filled yet — deterministically, not by prompt instruction.

    Blocked calls get a synthetic ToolMessage explaining what's
    missing, so the agent's next turn can react to it (e.g. ask the
    user) instead of the call silently failing or never happening.
    """

    async def __call__(self, state: AgentState) -> dict:
        last_message: AIMessage = state["messages"][-1]
        preferences = state.get("trip_preferences", {}) or {}

        allowed_calls = []
        rejection_messages = []

        for call in last_message.tool_calls:
            required = TOOL_REQUIREMENTS.get(call["name"], [])
            missing = [f for f in required if not preferences.get(f)]

            if missing:
                logger.info(
                    "ValidateToolCallsNode: Blocking '{}' — missing {}.",
                    call["name"],
                    missing,
                )
                rejection_messages.append(
                    ToolMessage(
                        content=(
                            f"Cannot run {call['name']} yet — missing "
                            f"required info: {', '.join(missing)}. Ask "
                            "the user for these before retrying."
                        ),
                        tool_call_id=call["id"],
                    )
                )
            else:
                allowed_calls.append(call)

        # Replace the last message with the same id, but only the
        # allowed tool_calls — this updates it in place via
        # add_messages' id-matching, rather than appending a duplicate.
        updated_message = AIMessage(
            content=last_message.content,
            tool_calls=allowed_calls,
            id=last_message.id,
        )

        return {"messages": [updated_message, *rejection_messages]}


def should_execute_tools(state: AgentState) -> str:
    """
    After validation, route to the tools node only if any tool calls
    survived. If all were blocked, go straight back to the agent so
    it can react to the rejection messages (e.g. ask for missing info).
    """
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return "agent"