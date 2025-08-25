import os
import requests
from shared.state import State, GroupMember
from typing import List, Dict
from collections import Counter
from shared.llm import get_llm
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from tools.google_places import search_places_nearby
from pydantic import BaseModel, Field
from shared.parsing import parse_structured_output


class Restaurant(BaseModel):
    """A single restaurant recommendation"""

    name: str = Field(description="Name of the restaurant")
    coordinates: List[float] = Field(description="coordinates of the restaurant")
    rating: float = Field(description="Average rating (1-5 stars)")
    user_ratings_total: int = Field(description="Total number of reviews")
    cuisine_types: List[str] = Field(description="Types of cuisine served")
    price_level: str = Field(
        description="Price level (PRICE_LEVEL_INEXPENSIVE, PRICE_LEVEL_MODERATE, etc.)"
    )
    recommendation_reason: str = Field(
        description="Why this restaurant is recommended for the group"
    )


class RestaurantResponse(BaseModel):
    """Structured restaurant recommendations for a group"""

    top_recommendations: List[Restaurant] = Field(
        description="List of recommended restaurants ranked by suitability"
    )


def geolocate_members_and_get_center(members: List[GroupMember]) -> List[Dict]:
    """Get member coordinates from Google Geocode API based on member locations."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return [{"error": "Google Maps API key not found"}]

    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

    member_coordinates = []
    for member in members:

        geocode_params = {"address": member["location"], "key": api_key}
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_data = geocode_response.json()

        if geocode_data.get("results"):
            location = geocode_data["results"][0]["geometry"]["location"]
            member_coordinates.append(
                {"name": member["name"], "lat": location["lat"], "lng": location["lng"]}
            )
            member["coordinates"] = [location["lat"], location["lng"]]
        else:
            print(
                f"Warning: Could not geocode {member['name']}'s location: {member['location']}. Geocode data: {geocode_data}"
            )

    center_lat = sum(coord["lat"] for coord in member_coordinates) / len(
        member_coordinates
    )
    center_lng = sum(coord["lng"] for coord in member_coordinates) / len(
        member_coordinates
    )

    return center_lat, center_lng


def restaurant_agent(state: State):
    """Get candidate restaurants based on the user's preferences and budget."""

    center_lat, center_lng = geolocate_members_and_get_center(state["members"])

    parser = PydanticOutputParser(pydantic_object=RestaurantResponse)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
            You are a restaurant recommendation specialist that helps groups find the perfect dining experience.
            Your goal is to analyze restaurant options and provide fair, well-reasoned recommendations.
            
            INSTRUCTIONS:
            1. Use the search_places_nearby tool to find restaurants near the center location
            3. Match restaurant options to the top 3 most frequent stated cuisine preferences
            4. Respect the specified budget constraints
            5. Prioritize restaurants with good ratings and reviews
            6. Provide clear reasoning for your recommendations
            
            When making recommendations:
            - Rank restaurants by how well they satisfy the group's collective needs
            - Consider factors like cuisine match, location fairness, price level, and ratings
            - Explain why each recommendation works well for the group
            - Provide specific reasoning for distance fairness and preference matching
            
            {format_instructions}
            """,
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = get_llm()
    tools = [search_places_nearby]
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    result = agent_executor.invoke(
        {
            "input": f"Find restaurants for a group with the most frequent from the following preferences: {state['preferences']}, budget: {state['budget']}, center location: ({center_lat:.4f}, {center_lng:.4f}). Search for restaurants using the tool and recommend the top 3 that best serve this group."
        }
    )

    structured_response = parse_structured_output(result, parser)
    candidate_restaurants = (
        structured_response.top_recommendations
        if structured_response is not None
        else []
    )
    return {
        "candidate_restaurants": candidate_restaurants,
        "members": state["members"],
        "preferences": state["preferences"],
        "budget": state["budget"],
    }
