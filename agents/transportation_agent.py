from shared.state import State, GroupMember
from shared.llm import get_llm
from typing import Dict, List
from pydantic import BaseModel, Field
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from tools.compute_route_matrix import get_compute_route_matrix
from shared.parsing import parse_structured_output


class Restaurant(BaseModel):
    name: str = Field(description="The name of the restaurant")
    transportation_score: float = Field(
        description="The score of how fair the transportation for all members for this restaurant"
    )
    travel_times: Dict[str, int] = Field(
        description="The travel times to this restaurant for each member (in minutes)"
    )


class RestaurantsAndScore(BaseModel):
    restaurants: List[Restaurant] = Field(
        description="The list of restaurants and their transportation fairness scores"
    )


def transportation_agent(state: State):
    """Get distance matrix between members and restaurants and rate how fair the distance is for each restaurant"""

    members = state["members"]
    restaurants = state["candidate_restaurants"]
    preferences = state["preferences"]
    budget = state["budget"]

    name_and_coords = [
        {
            "name": member["name"],
            "coordinates": member["coordinates"],
            "travel_preferences": member["travel_preferences"],
        }
        for member in members
    ]

    restaurant_name_coords = [
        (restaurant.name, restaurant.coordinates) for restaurant in restaurants
    ]

    parser = PydanticOutputParser(pydantic_object=RestaurantsAndScore)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a transportation fairness specialist that helps groups find the perfect dining experience.

                INSTRUCTIONS:
                Your goal is to analyze restaurant options and give a score for how fair the transportation is for each restaurant.
                
                1. Compute the transportation times for each member to get to each restaurant using the get_distance_matrix tool.
                2. Compute the transportation fairness score for each restaurant based on the travel times for each member.

                When scoring:
                - The score is a number between 0 and 100, where 0 means travel times are very unfair (big differences) and 100 means they are very fair (similar times)
                - Consider both absolute travel times and relative fairness between members
                - Lower average travel time is better, but fairness (similarity) is most important

                {format_instructions}
                """,
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = get_llm()
    tools = [get_compute_route_matrix]
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    result = agent_executor.invoke(
        {
            "input": f"Score the restaurants provided by their transportation fairness score. The restaurants are {restaurant_name_coords}. Members and their locations are in {name_and_coords}, for now, use DRIVE as the travel mode. Use the get_compute_route_matrix tool to get the travel times from each member's location to all of the restaurant locations. The travel times are in minutes."
        }
    )

    structured_response = parse_structured_output(result, parser)
    transportation_scores = (
        structured_response.restaurants if structured_response is not None else []
    )
    return {
        "transportation_scores": transportation_scores,
        "members": members,
        "preferences": preferences,
        "budget": budget,
        "candidate_restaurants": restaurants,
    }
