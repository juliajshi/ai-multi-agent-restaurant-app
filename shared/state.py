from typing_extensions import TypedDict, List, Dict
from typing import Annotated
from langgraph.graph.message import add_messages


class GroupMember(TypedDict):
    name: str
    location: str
    diet: str
    coordinates: List[float]
    travel_preferences: List[str]


class State(TypedDict):
    messages: Annotated[list, add_messages]
    members: List[GroupMember]
    preferences: str
    budget: str
    candidate_restaurants: List[Dict]
    final_suggestions: str
    transportation_scores: List[Dict]
