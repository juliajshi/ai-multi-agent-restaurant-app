from shared.state import State, GroupMember
from shared.llm import get_llm
from typing import Dict, Literal
from pydantic import BaseModel, Field


class InputResponse(BaseModel):
    members: list[GroupMember]
    preferences: str
    budget: int = Field(
        description="Budget per person in dollars, default to 25 if not specified"
    )


def input_agent(state: State):
    """Parse the user's input into a structured format of members, preferences, and budget."""
    last_message = state["messages"][-1]
    llm = get_llm()
    input_parser = llm.with_structured_output(InputResponse)

    result = input_parser.invoke(
        [
            {
                "role": "system",
                "content": """You are a helpful assistant that parses user input into a structured format.
    
    Extract the following information from the user's message:
    1. Members: List of people with their name, location, dietary preferences, and travel preferences (driving, walking, biking, etc. Assume driving if not specified)
    2. Preferences: short description of the group's preferences
    3. Budget: Budget per person in dollars (if not mentioned, use 25)
    
    Example input: "Annie is in Midtown NYC and likes cheap Thai and Indian food. Bob is in East Village and likes Thai and Japanese food and can walk. Charlie is in Soho, NYC and likes cheap Mexican food and can walk. "
    
    Example output:
    - Members: [{"name": "Annie", "location": "Midtown NYC", "diet": "none", "travel_preferences": ["driving", "walking"]}, {"name": "Bob", "location": "East Village", "diet": "none", "travel_preferences": ["walking"]}, {"name": "Charlie", "location": "Soho, NYC", "diet": "none", "travel_preferences": ["walking"]}]
    - Preferences: "Thai, Indian, or Japanese food"
    - Budget: 25
    """,
            },
            {"role": "user", "content": last_message.content},
        ]
    )

    return {
        "members": result.members,
        "preferences": result.preferences,
        "budget": result.budget,
    }
