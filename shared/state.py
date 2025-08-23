from typing_extensions import TypedDict, List, Dict
from typing import Annotated
from langgraph.graph.message import add_messages

# class State(TypedDict):
#     """Shared state definition for the multi-agent workflow."""
#     messages: Annotated[list, add_messages]  # messages is type list, has to be annotated with add_messages
#     message_type: str | None
#     next: str | None 

class GroupMember(TypedDict):
    name: str
    location: str
    diet: str

class State(TypedDict):
    messages: Annotated[list, add_messages]  # Add messages for input parsing
    members: List[GroupMember]
    preferences: List[str]
    budget: int
    candidate_restaurants: List[Dict]  # Output from Restaurant Agent
    travel_times: Dict[str, Dict[str, int]]  # person -> restaurant -> time
    final_suggestions: List[Dict]
    member_coordinates: List[Dict]