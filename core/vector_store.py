import os 
from langchain_chroma import Chroma 
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Defaults — used when no per-meeting paths are provided (e.g. CLI mode)
# ---------------------------------------------------------------------------
DEFAULT_CHROMA_DIR = "vector_db"
DEFAULT_COLLECTION = "meeting_transcript"
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name = EMBEDDING_MODEL,
        model_kwargs = {"device" : 'cpu'}
    )

def build_vector_store(
    transcript: str,
    persist_directory: str = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION,
) -> Chroma:
    """
    Build a Chroma vector store from a transcript string.

    Args:
        transcript:        The full meeting transcript.
        persist_directory: Where to save the Chroma files on disk.
                           Pass a per-meeting path (e.g. "data/jobs/<id>/chroma")
                           to keep meetings isolated.
        collection_name:   Chroma collection name — one per meeting.
    """
    print("Building vector Store")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
    )
    chunks = splitter.split_text(transcript)

    docs = [
        Document(page_content=chunk, metadata = {'chunk_index' : i})
        for i,chunk in enumerate(chunks)
    ]

    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents= docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )

    return vector_store



def load_vector_store(
    persist_directory: str = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION,
) -> Chroma:
    """Load an existing Chroma vector store from disk."""
    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function= embeddings,
        persist_directory=persist_directory
    )

    return vector_store

def get_retriever(vector_store : Chroma, k :int = 4):
    return vector_store.as_retriever(
        search_type = 'similarity',
        search_kwargs = {"k":k}
    )
