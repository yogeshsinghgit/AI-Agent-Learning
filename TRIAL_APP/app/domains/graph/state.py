from typing import TypedDict
from langgraph.graph import MessagesState


REQUIRED_TRIP_FIELDS = ["destination", "date_from", "date_to",]
MAX_TOOL_ATTEMPTS_PER_TURN = 4

class TripPreferences(TypedDict, total=False):
    """
    Trip-planning details collected incrementally from the
    conversation. All fields start unset and get filled in as the
    user provides them across turns.
    """

    destination: str | None  # City or place name only, e.g. 'Delhi'
    country: str | None      # ISO country code preferred, e.g. 'IN'
    date_from: str | None    # YYYY-MM-DD
    date_to: str | None      # YYYY-MM-DD
    preferences: str | None  # Free-text, e.g. 'budget travel', 'family-friendly'


class AgentState(MessagesState):
    """
    Shared state flowing through the LangGraph execution.

    MessagesState already provides:
        - messages (with the add_messages reducer)

    Extended with application-specific state required by our
    workflow.

    Note: trip_preferences has no reducer, so any node that updates
    it must merge with the existing dict itself (read old state,
    merge in newly extracted values, return the full merged dict) —
    otherwise returning a partial dict will overwrite previously
    collected fields.
    """

    trip_preferences: TripPreferences
    tool_attempts: int  # reset each turn by ExtractPreferencesNode