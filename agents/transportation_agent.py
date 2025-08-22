from shared.state import State, GroupMember
from shared.llm import get_llm


def get_candidate_restaurants(state: State):
    """Get candidate restaurants based on the user's preferences and budget."""
    members = state["members"]
    preferences = state["preferences"]
    budget = state["budget"]

    llm = get_llm()
    # Call Google Maps or Yelp API here
    # Stubbed version:
    # return [
    #     {"name": "Tofu Town", "cuisine": "Thai", "location": "789 Pine St"},
    #     {"name": "Masala Bay", "cuisine": "Indian", "location": "321 Curry Rd"}
    # ]
    pass