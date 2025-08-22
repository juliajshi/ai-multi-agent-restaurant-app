from typing import Literal
from pydantic import BaseModel, Field
from shared.state import State
from shared.llm import get_llm

# Type for structured output parser, kind of like a schema for the output
class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional (therapist) or logical response."
    )

def classify_message(state: State):
    """Classify the user's message as either emotional or logical."""
    last_message = state["messages"][-1]  # user's last message
    llm = get_llm()
    classifier_llm = llm.with_structured_output(MessageClassifier)  # llm that matches the MessageClassifier schema/pydantic model

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}  # updates state with message type 