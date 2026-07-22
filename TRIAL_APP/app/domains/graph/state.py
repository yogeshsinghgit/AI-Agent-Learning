from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """
    Shared state flowing through the LangGraph execution.

    MessagesState already provides:
        - messages

    We extend it with application-specific state required by
    our workflow.

    # Stored as a plain dict (PlannerDecision.model_dump(mode="json")),
    # never as the Pydantic model itself. LangGraph's Postgres
    # checkpointer serializes state via msgpack, which only safely
    # round-trips primitives/dicts/lists — custom types (including
    # the PlannerIntent enum inside PlannerDecision) require an
    # unregistered-type fallback that LangGraph has flagged for
    # removal. Reconstruct the typed PlannerDecision where it's
    # actually needed (see chatbot_node.py) instead of persisting it.
    """
    pass
