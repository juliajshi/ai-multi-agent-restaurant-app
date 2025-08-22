from shared.state import State
from shared.llm import get_llm

def logical_agent(state: State):
    """Provide logical, fact-based responses."""
    last_message = state["messages"][-1]
    llm = get_llm()

    messages = [
        {"role": "system",
         "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]} 