import uuid
import re
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db import get_db
from backend.app.schemas.meetings import MeetingCreateYouTube, MeetingOut, TranscriptOut, SummaryOut, ChatRequest, ChatResponse
from backend.app.services import meeting_service
from backend.app.services.pipeline import run_pipeline_background
from core.rag_engine import load_rag_chain, ask_question

router = APIRouter()

@router.post("/upload", response_model=MeetingOut, status_code=status.HTTP_202_ACCEPTED)
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    language: Annotated[str, Form()] = "english",
    db: Session = Depends(get_db)
):
    """Upload a video file for processing."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    if not file.content_type or not (file.content_type.startswith("audio/") or file.content_type.startswith("video/")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only audio and video are allowed.")
        
    MAX_FILE_SIZE = 500 * 1024 * 1024 # 500 MB
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 500MB)")
        
    # Generate a unique ID for this upload
    meeting_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1] if "." in file.filename else "mp4"
    file_path = settings.data_dir / "uploads" / f"{meeting_id}.{extension}"
    
    # Save the file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Create DB record (we force the ID to match our generated one so the file matches the DB record)
    meeting = meeting_service.create_meeting(
        db=db,
        source_type="upload",
        source_ref=file_path.as_posix(),
        language=language,
        title=file.filename
    )
    # Update the generated ID to match the file
    meeting.id = meeting_id
    db.commit()
    db.refresh(meeting)
    
    # Trigger background pipeline
    background_tasks.add_task(run_pipeline_background, meeting.id)
    
    return meeting


@router.post("/youtube", response_model=MeetingOut, status_code=status.HTTP_202_ACCEPTED)
async def youtube_meeting(
    payload: MeetingCreateYouTube,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a YouTube URL for processing."""
    url = str(payload.url)
    
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    if not re.match(youtube_regex, url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")

    meeting = meeting_service.create_meeting(
        db=db,
        source_type="youtube",
        source_ref=str(payload.url),
        language=payload.language,
        title=f"YouTube Video: {payload.url}"
    )
    
    # Trigger background pipeline
    background_tasks.add_task(run_pipeline_background, meeting.id)
    
    return meeting


@router.get("/{meeting_id}", response_model=MeetingOut)
async def get_meeting(
    meeting_id: str,
    db: Session = Depends(get_db)
):
    """Get the current status and full details of a meeting."""
    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    return meeting


@router.get("/{meeting_id}/transcript", response_model=TranscriptOut)
async def get_transcript(
    meeting_id: str,
    db: Session = Depends(get_db)
):
    """Get just the transcript for a meeting."""
    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if meeting.transcript is None:
        raise HTTPException(status_code=404, detail="Transcript not yet available")
        
    return TranscriptOut(transcript=meeting.transcript)


@router.get("/{meeting_id}/summary", response_model=SummaryOut)
async def get_summary(
    meeting_id: str,
    db: Session = Depends(get_db)
):
    """Get just the summary and title for a meeting."""
    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if meeting.summary is None:
        raise HTTPException(status_code=404, detail="Summary not yet available")
        
    return SummaryOut(summary=meeting.summary, title=meeting.title)


@router.post("/{meeting_id}/chat", response_model=ChatResponse)
async def chat_with_meeting(
    meeting_id: str,
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    """Ask a question about the meeting using RAG."""
    meeting = meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    if meeting.status != "completed" or not meeting.chroma_path:
        raise HTTPException(status_code=400, detail="Meeting vector store not ready yet")
        
    try:
        # Load the RAG chain for this specific meeting
        rag_chain = load_rag_chain(
            persist_directory=meeting.chroma_path,
            collection_name=f"meeting_{meeting_id}"
        )
        
        # Ask the question
        answer = ask_question(rag_chain, payload.question)
        
        # Return the response (we return empty sources for now as LCEL doesn't extract them easily)
        return ChatResponse(answer=answer, sources=[])
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG Engine error: {str(e)}")
