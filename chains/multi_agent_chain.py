from langgraph.graph import StateGraph, START, END

# import agents
from shared.state import State
from agents.input_agent import input_agent
from agents.restaurant_agent import restaurant_agent
from agents.transportation_agent import transportation_agent
from agents.output_agent import output_agent


def create_multi_agent_graph():
    """Create and return the multi-agent workflow graph."""
    # Define graph builder
    graph_builder = StateGraph(State)

    # add nodes
    graph_builder.add_node("input_agent", input_agent)
    graph_builder.add_node("restaurant_agent", restaurant_agent)
    graph_builder.add_node("transportation_agent", transportation_agent)
    graph_builder.add_node("output_agent", output_agent)

    # add edges
    graph_builder.add_edge(START, "input_agent")
    graph_builder.add_edge("input_agent", "restaurant_agent")
    graph_builder.add_edge("restaurant_agent", "transportation_agent")
    graph_builder.add_edge("transportation_agent", "output_agent")
    graph_builder.add_edge("output_agent", END)

    # #example for adding conditional edges
    # graph_builder.add_conditional_edges(
    #     "router",  # source
    #     lambda state: state.get("next"),  # function that returns the next node to go to based on the state
    #     {"therapist": "therapist", "logical": "logical"}  # conditional path map
    # )

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
