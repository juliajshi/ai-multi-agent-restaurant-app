from langgraph.graph import StateGraph, START, END

# import agents
from shared.state import State
from agents.input_agent import input_agent
from agents.restaurant_agent import restaurant_agent
from agents.transportation_agent import transportation_agent
from agents.output_agent import output_agent
from langchain.schema import AIMessage


def create_multi_agent_graph():
    """Create and return the multi-agent workflow graph."""
    graph_builder = StateGraph(State)

    graph_builder.add_node("input_agent", input_agent)
    graph_builder.add_node("restaurant_agent", restaurant_agent)
    graph_builder.add_node("transportation_agent", transportation_agent)
    graph_builder.add_node("output_agent", output_agent)

    graph_builder.add_edge(START, "input_agent")
    graph_builder.add_edge("input_agent", "restaurant_agent")
    graph_builder.add_edge("restaurant_agent", "transportation_agent")
    graph_builder.add_edge("transportation_agent", "output_agent")
    graph_builder.add_edge("output_agent", END)

    return graph_builder.compile()


def run_restaurant_choosing_chain():
    """Run the multi-agent workflow with user interaction."""
    graph = create_multi_agent_graph()
    state = {
        "messages": [],
        "members": [],
        "preferences": [],
        "budget": 0,
        "candidate_restaurants": [],
        "travel_times": {},
        "transportation_scores": [],
        "final_suggestions": [],
        "travel_preferences": [],
    }  # initial State

    print("\nAI Assistant for Group Dining! (Type 'exit' to quit)")
    print("\nEnter your input in the following format:")
    print(
        "Annie is in midtown, NYC and likes cheap Thai and Indian food and will walk. Bob is in East Village, NYC and likes Japanese and Thai food of cheap to midrange price. Charlie is in SOHO, NYC and likes cheap Mexican food."
        "\n"
    )

    # while True:
    user_input = input("Enter a message: ")
    print()
    # if user_input == "":
    #     print("Please enter a valid input")
    #     continue

    # if user_input.lower() == "exit":
    #     print("Goodbye!")
    #     break

    # Add user input to messages
    state["messages"] = state.get("messages", []) + [
        {"role": "user", "content": user_input}
    ]

    # Invoke graph with state
    state = graph.invoke(state)

    # Print the assistant's response
    if state.get("messages") and len(state["messages"]) > 0:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage):
            content = last_message.content
            print(content)
        print("-" * 50)

    # print(state.get("final_suggestions"))
    # print("-" * 50)
