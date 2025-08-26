from langgraph.graph import StateGraph, START, END

# import agents
from shared.state import State
from agents.input_agent import input_agent
from agents.restaurant_agent import restaurant_agent
from agents.transportation_agent import transportation_agent
from agents.output_agent import output_agent
from agents.followup_agent import followup_agent
from langchain.schema import AIMessage

from langchain_core.runnables.history import RunnableWithMessageHistory


def should_do_new_search(state: State) -> str:
    """Determine if we should do a new search or handle as followup."""
    # Check if this is an initial request or if followup determined new search is needed
    if state.get("is_initial_request", True) or state.get("needs_new_search", False):
        return "restaurant_agent"
    else:
        return "followup_response"


def followup_response_node(state: State):
    """Final node for followup responses that don't need new search."""
    from langchain.schema import AIMessage

    return {
        **state,
        "final_suggestions": state.get("followup_response", ""),
        "messages": state.get("messages", [])
        + [AIMessage(content=state.get("followup_response", ""))],
    }


def create_multi_agent_graph():
    """Create and return the multi-agent workflow graph with followup handling."""
    graph_builder = StateGraph(State)

    # Add all nodes
    graph_builder.add_node("input_agent", input_agent)
    graph_builder.add_node("followup_agent", followup_agent)
    graph_builder.add_node("restaurant_agent", restaurant_agent)
    graph_builder.add_node("transportation_agent", transportation_agent)
    graph_builder.add_node("output_agent", output_agent)
    graph_builder.add_node("followup_response", followup_response_node)

    # Initial flow
    graph_builder.add_edge(START, "input_agent")
    graph_builder.add_edge("input_agent", "followup_agent")

    # Conditional routing based on whether new search is needed
    graph_builder.add_conditional_edges(
        "followup_agent",
        should_do_new_search,
        {
            "restaurant_agent": "restaurant_agent",
            "followup_response": "followup_response",
        },
    )

    # Full search flow
    graph_builder.add_edge("restaurant_agent", "transportation_agent")
    graph_builder.add_edge("transportation_agent", "output_agent")

    # End points
    graph_builder.add_edge("output_agent", END)
    graph_builder.add_edge("followup_response", END)

    return graph_builder.compile()


def run_restaurant_choosing_chain():
    """Run the multi-agent workflow with user interaction and followup handling."""
    graph = create_multi_agent_graph()

    # Persistent state that maintains conversation context
    conversation_state = {
        "messages": [],
        "members": [],
        "preferences": "",
        "budget": "",
        "candidate_restaurants": [],
        "transportation_scores": [],
        "final_suggestions": "",
        "needs_new_search": False,
        "followup_response": "",
        "is_initial_request": True,
    }

    print("\nAI Assistant for Group Dining! (Type 'exit' to quit)")
    print("\nEnter your input in the following format:")
    print(
        "Annie is in midtown, NYC and likes cheap Thai and Indian food and will walk. Bob is in East Village, NYC and likes Japanese and Thai food of cheap to midrange price. Charlie is in SOHO, NYC and likes cheap Mexican food."
    )
    print("\n💬 After I provide recommendations, feel free to ask followup questions!")
    print(
        "Examples: 'What about Italian instead?', 'Add Sarah to the group', 'What are the hours for the first restaurant?'"
    )
    print("-" * 50)

    while True:
        user_input = input("\nEnter a message: ")
        print()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if user_input.strip() == "":
            print("Please enter a valid input")
            continue

        try:
            # Create fresh state for this interaction but preserve context
            current_state = conversation_state.copy()

            # Add current user input
            from langchain.schema import HumanMessage

            current_state["messages"] = current_state.get("messages", []) + [
                HumanMessage(content=user_input)
            ]

            # Pass existing members to the followup agent via special field
            if not current_state.get("is_initial_request", True):
                current_state["_existing_members"] = conversation_state.get(
                    "members", []
                )

            # Invoke graph with state
            result_state = graph.invoke(current_state)

            # Update conversation state with results
            conversation_state.update(result_state)
            conversation_state["is_initial_request"] = (
                False  # Mark subsequent requests as followups
            )

            # Print the response
            if result_state.get("final_suggestions"):
                print("🍽️ Response:")
                print(result_state["final_suggestions"])
                print("-" * 50)

            # Show what type of response this was
            if result_state.get("needs_new_search"):
                print("🔄 Performed new restaurant search")
            elif not result_state.get("is_initial_request", True):
                print("💬 Provided followup response")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Please try again with a different input.")
            print("-" * 50)
