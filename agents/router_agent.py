from shared.state import State

def router(state: State):
    """Route messages to the appropriate agent based on message type."""
    message_type = state.get("message_type", "logical")  # if message type is not in state, default to logical
    if message_type == "emotional":
        return {"next": "therapist"}

    return {"next": "logical"} 