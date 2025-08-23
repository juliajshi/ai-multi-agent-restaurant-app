from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

# from tools.geocoding import geocode_address

# Import agents
# from agents.classifier_agent import classify_message
# from agents.router_agent   import router
# from agents.therapist_agent import therapist_agent
# from agents.logical_agent import logical_agent

from shared.state import State
from agents.input_agent import input_agent
from agents.restaurant_agent import restaurant_agent

# from agents.transportation_agent import transportation_agent
# # from agents.scoring_agent import compute_scores
# from agents.output_agent import generate_output


def create_multi_agent_graph():
    """Create and return the multi-agent workflow graph."""
    # Define graph builder
    graph_builder = StateGraph(State)

    # Add nodes (agents)
    # graph_builder.add_node("input_classifier", classify_message)
    # graph_builder.add_node("router", router)
    # graph_builder.add_node("therapist", therapist_agent)
    # graph_builder.add_node("logical", logical_agent)
    graph_builder.add_node("input_agent", input_agent)
    graph_builder.add_node("restaurant_agent", restaurant_agent)
    # graph_builder.add_node("transportation_agent", transportation_agent)
    # # graph_builder.add_node("scoring_agent", compute_scores)
    # graph_builder.add_node("output_agent", generate_output)

    # Add edges
    # graph_builder.add_edge(START, "classifier")
    # graph_builder.add_edge("classifier", "router")

    # # Add conditional edges
    # graph_builder.add_conditional_edges(
    #     "router",  # source
    #     lambda state: state.get("next"),  # function that returns the next node to go to based on the state
    #     {"therapist": "therapist", "logical": "logical"}  # conditional path map
    # )

    # graph_builder.add_edge("therapist", END)
    # graph_builder.add_edge("logical", END)

    graph_builder.add_edge(START, "input_agent")
    graph_builder.add_edge("input_agent", "restaurant_agent")
    graph_builder.add_edge("restaurant_agent", END)
    # graph_builder.add_edge("restaurant_agent", "routing_agent")
    # graph_builder.add_edge("routing_agent", "output_agent")
    # graph_builder.add_edge("output_agent", END)

    # Compile and return the graph
    return graph_builder.compile()


def run_multi_agent_workflow():
    """Run the multi-agent workflow with user interaction."""
    graph = create_multi_agent_graph()
    state = {
        "messages": [],
        "members": [],
        "preferences": [],
        "budget": 0,
        "candidate_restaurants": [],
        "travel_times": {},
        "final_suggestions": [],
        "member_coordinates": [],
    }  # initial State

    print("Multi-Agent Workflow Started! (Type 'exit' to quit)")

    # while True:
    # user_input = input("Enter a message: ")
    user_input = "Annie is in Midtown NYC and likes cheap Thai and Indian food. Bob is in East Village and likes Thai and Japanese food. Charlie is in Soho, NYC and likes cheap Mexican food. "
    if user_input == "exit":
        print("Goodbye!")
        # break

    # Add user input to messages
    state["messages"] = state.get("messages", []) + [
        {"role": "user", "content": user_input}
    ]

    # Invoke graph with state
    state = graph.invoke(state)

    # Print the assistant's response
    if state.get("messages") and len(state["messages"]) > 0:
        last_message = state["messages"][-1]
        print(f"\n{last_message.content}\n")
        print("-" * 50)
