from shared.state import State, GroupMember
from shared.llm import get_llm
from typing import Dict
from langchain_core.prompts import ChatPromptTemplate


def output_agent(state: State):
    """gets the top 3 restaurants based on the travel times and preferences, and returns the final suggestions in a table format"""

    final_suggestions = state["final_suggestions"]
    members = state["members"]
    preferences = state["preferences"]
    budget = state["budget"]

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
                "You are a helpful assistant that outputs the final suggestions in a table format. Include the following columns: Restaurant name as a link to the GoogleMaps link, Transportation fairness score, Travel times for each member, Cost Category",
            ),
            ("human", "The final suggestions are: {final_suggestions}"),
        ]
    )

    result = llm.invoke(prompt.format(final_suggestions=final_suggestions))
    print("FINAL Result:", result.content)

    return {
        "final_suggestions": final_suggestions,
    }
