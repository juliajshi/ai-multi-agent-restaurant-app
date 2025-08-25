from shared.state import State, GroupMember
from shared.llm import get_llm
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate


def output_agent(state: State):
    """gets the top 3 restaurants based on the travel times and preferences, and returns the final suggestions in a table format"""

    transportation_scores = state["transportation_scores"]
    members = state["members"]
    preferences = state["preferences"]
    budget = state["budget"]
    restaurant_data = state["candidate_restaurants"]

    # output final suggestions in a table format, with the following columns:
    # - Restaurant name with link to GoogleMaps link
    # - Transportation fairness score
    # - Travel times for each member
    # - Cost Category

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that outputs the final suggestions in a table format that can be shown in the terminal. Format the table to be readable with equal spacing for each column. Include the following columns: Restaurant name as a link to the GoogleMaps link, rating, number of reviews, cuisine type, price level ($, $$, $$$, $$$$), Travel times for each member (in minutes)). Make sure to include the link to the GoogleMaps link for each restaurant (use the format https://www.google.com/maps/search/the restaurant name with spaces replaced with +).",
            ),
            (
                "human",
                "Pick the top 3 restaurants based on the transportation scores and restaurant data. The transportation scores are available in: {transportation_scores} and the restaurant data is: {restaurant_data}",
            ),
        ]
    )

    result = llm.invoke(
        prompt.format(
            transportation_scores=transportation_scores, restaurant_data=restaurant_data
        )
    )

    return {
        "transportation_scores": transportation_scores,
        "members": members,
        "preferences": preferences,
        "budget": budget,
        "candidate_restaurants": restaurant_data,
        "final_suggestions": result.content,
        "messages": [
            {
                "role": "assistant",
                "content": result.content,
            }
        ],
    }
