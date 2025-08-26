from shared.state import State
from shared.llm import get_llm
from typing import Dict, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class FollowupResponse(BaseModel):
    needs_new_search: bool = Field(
        description="Whether a new restaurant search is needed based on the followup question"
    )
    modified_preferences: str = Field(
        description="Updated preferences if changed, otherwise empty string"
    )
    modified_budget: str = Field(
        description="Updated budget if changed, otherwise empty string"
    )
    direct_answer: str = Field(
        description="Direct answer to the followup question if no new search is needed"
    )
    reasoning: str = Field(
        description="Explanation of why a new search is or isn't needed"
    )
    members_to_add: List[Dict] = Field(
        description="New members to add to the group if any are mentioned", default=[]
    )
    members_to_remove: List[str] = Field(
        description="Names of members to remove from the group if any are mentioned",
        default=[],
    )


def followup_agent(state: State):
    """Handle followup questions after initial restaurant recommendations."""

    # Get the current conversation context
    messages = state.get("messages", [])
    previous_recommendations = state.get("final_suggestions", "")

    # Get members from input agent (these might be new members to add)
    input_members = state.get("members", [])

    # Get existing members from conversation state (from previous interactions)
    # We need to access this from the persistent conversation state
    existing_members = []

    current_preferences = state.get("preferences", "")
    current_budget = state.get("budget", "")

    if not messages:
        # No followup needed if no previous messages
        return state

    last_message = messages[-1]
    # Handle both dict and LangChain message object formats
    if hasattr(last_message, "content"):
        user_question = last_message.content
    else:
        user_question = last_message.get("content", "")

    llm = get_llm()
    followup_parser = llm.with_structured_output(FollowupResponse)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a followup assistant for a restaurant recommendation system.
            
            Your job is to analyze user followup questions and determine if a new restaurant search is needed,
            or if you can provide a direct answer based on existing information.
            
                         SCENARIOS THAT NEED NEW SEARCH:
             - User wants to change preferences (cuisine, dietary restrictions)
             - User wants to change budget
             - User wants to add/remove group members
             - User wants restaurants in a different location/area
             - User wants to see more/different restaurant options
             
             SCENARIOS THAT DON'T NEED NEW SEARCH:
             - Questions about the recommended restaurants (hours, menu, phone number)
             - Questions about travel directions to a specific restaurant
             - General questions about the recommendations
             - Clarification about the scoring or selection process
             
             MEMBER MANAGEMENT:
             - If adding new members, extract their name, location, dietary preferences, and travel preferences
             - If removing members, note which members to remove by name
             - Format new members as: {"name": "Name", "location": "Location", "diet": "dietary restrictions or none", "travel_preferences": ["driving"]}
             
             If no new search is needed, provide a helpful direct answer based on the context.""",
            ),
            (
                "human",
                """Previous restaurant recommendations:
{previous_recommendations}

Current group members: {current_members}
Current preferences: {current_preferences}  
Current budget: {current_budget}

User's followup question: {user_question}

Analyze this followup question and determine the appropriate response.""",
            ),
        ]
    )

    result = followup_parser.invoke(
        prompt.format_messages(
            previous_recommendations=previous_recommendations,
            current_members=[member.get("name", "") for member in current_members],
            current_preferences=current_preferences,
            current_budget=current_budget,
            user_question=user_question,
        )
    )

    print(
        f"🤔 Followup analysis: {'New search needed' if result.needs_new_search else 'Direct answer'}"
    )
    print(f"📝 Reasoning: {result.reasoning}")

    # Update state based on the analysis
    updated_state = state.copy()

    if result.needs_new_search:
        # Update preferences and budget if changed
        if result.modified_preferences:
            updated_state["preferences"] = result.modified_preferences

        if result.modified_budget:
            updated_state["budget"] = result.modified_budget

        # Handle member changes - merge with existing members
        input_members = updated_state.get("members", [])  # New members from input_agent
        existing_members = updated_state.get(
            "_existing_members", []
        )  # Existing members from conversation state

        # Initialize current_members to prevent variable reference errors
        current_members = []

        if state.get("is_initial_request", True):
            # Initial request - use all members from input
            current_members = input_members
        else:
            # Followup request - merge new members with existing ones
            current_members = existing_members.copy()

            if input_members:
                new_member_names = [member.get("name", "") for member in input_members]
                print(
                    f"➕ Adding new members to existing group: {', '.join(new_member_names)}"
                )

                # Ensure new members have required fields
                for new_member in input_members:
                    if "travel_preferences" not in new_member:
                        new_member["travel_preferences"] = ["driving"]
                    if "diet" not in new_member:
                        new_member["diet"] = "none"
                    if "coordinates" not in new_member:
                        new_member["coordinates"] = []  # Will be geocoded later

                current_members.extend(input_members)

            print(
                f"👥 Total group: {[member.get('name', '') for member in current_members]}"
            )

        # Remove members if specified
        if result.members_to_remove:
            print(f"🚫 Removing members: {', '.join(result.members_to_remove)}")
            current_members = [
                member
                for member in current_members
                if member.get("name", "").lower()
                not in [name.lower() for name in result.members_to_remove]
            ]

        # Add new members if specified
        if result.members_to_add:
            new_member_names = [
                member.get("name", "") for member in result.members_to_add
            ]
            print(f"➕ Adding new members: {', '.join(new_member_names)}")

            # Ensure new members have all required fields
            for new_member in result.members_to_add:
                if "travel_preferences" not in new_member:
                    new_member["travel_preferences"] = ["driving"]
                if "diet" not in new_member:
                    new_member["diet"] = "none"
                if "coordinates" not in new_member:
                    new_member["coordinates"] = []  # Will be geocoded later

            current_members.extend(result.members_to_add)

        updated_state["members"] = current_members
        print(f"👥 Total group size: {len(current_members)} members")

        # Mark that we need a new search
        updated_state["needs_new_search"] = True
        updated_state["followup_response"] = (
            f"I understand you want to modify your search. {result.reasoning} Let me find new recommendations for you."
        )
    else:
        # Provide direct answer
        updated_state["needs_new_search"] = False
        updated_state["followup_response"] = result.direct_answer
        updated_state["final_suggestions"] = result.direct_answer

    return updated_state
