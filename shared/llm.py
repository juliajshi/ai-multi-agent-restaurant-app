from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Load environment variables once
load_dotenv()

# Create a single LLM instance that all agents can use
llm = init_chat_model(model="claude-3-haiku-20240307")

def get_llm():
    """Get the shared LLM instance."""
    return llm 