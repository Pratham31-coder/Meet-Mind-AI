"""
Shared LLM factory functions.

Every module that needs a Groq model should import from here
instead of creating its own get_llm().  This keeps model names, API keys,
and temperatures in one place.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration — read once from environment variables
# ---------------------------------------------------------------------------

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def get_groq_llm(temperature: float = 0.3) -> ChatGroq:
    """
    Return a ChatGroq instance.
    Used by: extractor (structured JSON insights), rag_engine (Q&A).
    """
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
    )
