from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    """Shared state definition for the multi-agent workflow."""
    messages: Annotated[list, add_messages]  # messages is type list, has to be annotated with add_messages
    message_type: str | None
    next: str | None 