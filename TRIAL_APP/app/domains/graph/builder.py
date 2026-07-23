from typing import Any
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import trim_messages
from loguru import logger

from app.domains.ai.runtime_dependencies.graph_context import GraphContext

from app.domains.graph.nodes.preferences import ExtractPreferencesNode
from app.domains.graph.nodes.validate_tool_calls import (
    ValidateToolCallsNode,
    should_execute_tools
)
from app.domains.ai.utils.token_counter_helper import token_counter
from app.domains.graph.state import AgentState, REQUIRED_TRIP_FIELDS


import datetime
from langchain_core.messages import SystemMessage


class AgentNode:
    """
    Node that runs the agent model bound with tools.
    """

    def __init__(self, context: GraphContext) -> None:
        self._context = context
        # Bind the tools in context to the LLM client
        self._model = context.llm.bind_tools(context.tools)

    async def __call__(self, state: AgentState) -> dict:
        logger.info("AgentNode: Running model...")
        
        # Inject system prompt with the current date so the LLM can resolve relative dates (e.g. tomorrow, next week)
        today = datetime.date.today().isoformat()
        preferences = state.get("trip_preferences", {}) or {}
        missing = [f for f in REQUIRED_TRIP_FIELDS if not preferences.get(f)]

        if not preferences:
            trip_instruction = ""

        elif missing:
            trip_instruction = (
                f"""
                Trip preferences collected so far:
                {preferences}

                Missing:
                {missing}

                Do NOT ask for all missing fields immediately.

                First answer every part of the user's request that can be
                completed with the currently available information.

                Only ask for additional information when it is required to
                perform the next requested action or tool call.

                For example:

                - Listing attractions only requires a destination.
                - Weather requires travel dates.
                - Hotel search requires travel dates.
                - Full itinerary planning requires complete trip details.
                """
            )
        else:
            trip_instruction = (
                f"Trip preferences are complete: {preferences}. Use the "
                "weather and attraction tools to plan based on real data, "
                "not just your own knowledge."
            )

        system_message = SystemMessage(
            content=(
                "You are a helpful travel assistant. "
                f"Today's date is {today}. Use this date as the reference for "
                "any relative date requests (e.g. tomorrow, next week, "
                "yesterday). "
                f"{trip_instruction} "
                "When planning a trip that spans multiple days, use both the "
                "weather tool and the attraction tool to base your itinerary "
                "on real, current data rather than general knowledge."
            )
        )
        trimmed = trim_messages(
            state["messages"],
            max_tokens=4000,          # tune to your model's context window
            strategy="last",           # keep most recent messages
            token_counter=token_counter,  # uses the model's own tokenizer
            include_system=True,
            start_on="human",          # avoid cutting mid tool-call/response pair
        )
        messages = [system_message] + list(trimmed)
        
        response = await self._model.ainvoke(messages)
        return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """
    Determine whether to route to tools or finish.
    """
    last_message = state["messages"][-1]
    logger.info(f"Last Message : {last_message}")
    if getattr(last_message, "tool_calls", None):
        logger.info("should_continue: Routing to tools node")
        return "tools"
    logger.info("should_continue: Routing to end")
    return END


def build_graph(context: GraphContext, checkpointer: Any) -> Any:
    """
    Build the compiled state graph for the agent.
    """
    logger.info("Building Agent State Graph...")
    workflow = StateGraph(AgentState)

    # Add agent node and tool execution node
    workflow.add_node("extract_preferences", ExtractPreferencesNode(context))
    workflow.add_node("agent", AgentNode(context))
    workflow.add_node("validate_tool_calls", ValidateToolCallsNode())
    workflow.add_node("tools", ToolNode(context.tools))

    # Add routing
    workflow.add_edge(START, "extract_preferences")
    workflow.add_edge("extract_preferences", "agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "validate_tool_calls",
            END: END,
        },
    )

    workflow.add_conditional_edges(
        "validate_tool_calls",
        should_execute_tools,
        {
            "tools": "tools",
            "agent": "agent",
        },
    )
    
    workflow.add_edge("tools", "agent")

    # Compile the graph with checkpointer
    logger.success("Graph compiled successfully with checkpointer.")
    return workflow.compile(checkpointer=checkpointer)
