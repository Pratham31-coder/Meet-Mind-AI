from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from core.llm import get_groq_llm
from tenacity import retry, stop_after_attempt, wait_exponential

class ActionItem(BaseModel):
    task: str = Field(description="The task to be completed")
    owner: str = Field(description="The person responsible for the task. If unknown, leave empty.", default="")
    deadline: str = Field(description="The deadline for the task. If unknown, leave empty.", default="")
    status: str = Field(description="Status of the task", default="open")

class MeetingInsights(BaseModel):
    title: str = Field(description="A concise, catchy title for the meeting (max 6 words)")
    summary: str = Field(description="A comprehensive 2-3 paragraph summary of the meeting")
    action_items: list[ActionItem] = Field(description="List of action items.")
    key_decisions: list[str] = Field(description="List of key decisions made.")
    open_questions: list[str] = Field(description="List of unresolved questions or topics needing follow-up.")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_all_insights(transcript: str) -> MeetingInsights:
    """
    Extracts title, summary, actions, decisions, and questions in ONE single LLM call.
    Uses Groq Structured Output to guarantee the Pydantic schema is populated.
    """
    llm = get_groq_llm().with_structured_output(MeetingInsights)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert executive assistant. Analyze the following meeting transcript and extract the title, summary, action items, key decisions, and open questions perfectly formatted."),
        ("human", "Meeting Transcript:\n\n{text}")
    ])
    
    chain = prompt | llm
    
    # Gemini 1.5 Flash has a 1M token context window, so we can pass the whole transcript
    return chain.invoke({"text": transcript})