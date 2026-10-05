from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from core.llm import get_groq_llm
from core.vector_store import build_vector_store, load_vector_store, get_retriever
from tenacity import retry, stop_after_attempt, wait_exponential


def format_docs(docs):
    """Format retrieved documents into a single context string."""
    return "\n\n".join([doc.page_content for doc in docs])


def _build_chain(retriever, llm):
    """
    Internal helper — wires the LCEL RAG pipeline.

    The chain structure:
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    # Full LCEL RAG pipeline
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def build_rag_chain(
    transcript: str,
    persist_directory: str = "vector_db",
    collection_name: str = "meeting_transcript",
):
    """
    Build a new vector store from a transcript, then return a ready-to-use
    LCEL RAG chain.

    Args:
        transcript:        Full meeting transcript text.
        persist_directory: Chroma storage path (per-meeting).
        collection_name:   Chroma collection name (per-meeting).
    """
    vector_store = build_vector_store(
        transcript,
        persist_directory=persist_directory,
        collection_name=collection_name,
    )
    retriever = get_retriever(vector_store, k=4)
    llm = get_groq_llm()
    return _build_chain(retriever, llm)


def load_rag_chain(
    persist_directory: str = "vector_db",
    collection_name: str = "meeting_transcript",
):
    """
    Load an existing vector store from disk and return a RAG chain.

    Args:
        persist_directory: Where the Chroma files are stored.
        collection_name:   The collection to load.
    """
    vector_store = load_vector_store(
        persist_directory=persist_directory,
        collection_name=collection_name,
    )
    retriever = get_retriever(vector_store, k=4)
    llm = get_groq_llm()
    return _build_chain(retriever, llm)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def ask_question(rag_chain, question: str) -> str:
    """Send a question through the RAG chain and return the answer."""
    answer = rag_chain.invoke(question)
    return answer