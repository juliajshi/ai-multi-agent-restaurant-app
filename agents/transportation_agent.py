from shared.state import State, GroupMember
from shared.llm import get_llm
from typing import Dict, List
from pydantic import BaseModel, Field
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from tools.distance_matrix import get_distance_matrix


class Restaurant(BaseModel):
    name: str = Field(description="The name of the restaurant")
    transportation_fairness_score: float = Field(
        description="The score of how fair the transportation for all members for this restaurant"
    )
    travel_times: Dict[str, int] = Field(
        description="The travel times to this restaurant for each member"
    )


class RestaurantsAndScore(BaseModel):
    restaurants: List[Restaurant] = Field(
        description="The list of restaurants and their transportation fairness scores"
    )


def transportation_agent(state: State):
    """Get distance matrix between members and restaurants and rate how fair the distance is for each restaurant"""

    # get the members and restaurants
    members = state["members"]
    restaurants = state["candidate_restaurants"]

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
                - The score is a number between 0 and 100, where 0 is the travel times for each restaurant are the most different and 100 is where they are the most similar.
                - Explain why you gave the score you did for each restaurant.



                {format_instructions}
                """,
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = get_llm()
    tools = [get_distance_matrix]
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke(
        {
            "input": f"Score the restaurants provided by their transportation fairness score. The restaurants are: {restaurants}. The members are: {members}."
        }
    )

    try:
        raw_output = result.get("output")
        actual_text = raw_output[0]["text"]
        # Handle both possible response structures
        if (
            isinstance(raw_output, list)
            and len(raw_output) > 0
            and "text" in raw_output[0]
        ):
            # Structure: [{'text': '...', 'type': 'text', 'index': 0}]
            actual_text = raw_output[0]["text"]
        elif isinstance(raw_output, str):
            # Structure: direct string
            actual_text = raw_output
        else:
            # Fallback
            actual_text = str(raw_output)

        # print("Raw output from agent:", actual_text)

        structured_response = parser.parse(actual_text)
        print("Structured response:", structured_response)
        return {
            "final_suggestions": structured_response,
            "members": members,
        }
    except Exception as e:
        print(f"Could not parse structured output: {e}")
        # Fallback to raw output if parsing fails
