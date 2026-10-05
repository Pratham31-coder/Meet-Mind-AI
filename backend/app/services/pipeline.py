import traceback
import os

from backend.app.core.config import settings
from backend.app.db import SessionLocal
from backend.app.services.meeting_service import get_meeting, update_meeting
from core.extractor import generate_all_insights
from core.transcriber import transcribe_all
from core.vector_store import build_vector_store
from utils.audio_processor import process_input

def run_pipeline_background(meeting_id: str):
    """
    Background task to process a meeting through the entire AI pipeline.
    """
    # Use a fresh DB session for the background task
    db = SessionLocal()
    try:
        meeting = get_meeting(db, meeting_id)
        if not meeting:
            print(f"Meeting {meeting_id} not found for processing.")
            return

        # Mark as processing
        update_meeting(db, meeting_id, status="processing", stage="audio_extraction")

        # 1. Audio Processing
        is_url = meeting.source_type == "youtube"
        job_dir = settings.data_dir / "jobs" / meeting_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        chunks = process_input(
            source=meeting.source_ref,
            output_dir=job_dir.as_posix()
        )

        # 2. Transcription
        update_meeting(db, meeting_id, stage="transcribing")
        transcript = transcribe_all(chunks, meeting.language)
        
        # Save transcript early
        update_meeting(db, meeting_id, transcript=transcript)

        # 3 & 4. Summarization & Extraction (Unified in 1 call)
        update_meeting(db, meeting_id, stage="extracting_insights")
        insights = generate_all_insights(transcript)
        title = insights.title
        summary = insights.summary
        action_items = [item.model_dump() for item in insights.action_items]
        key_decisions = insights.key_decisions
        open_questions = insights.open_questions

        # 5. Vector Store Setup (for RAG)
        update_meeting(db, meeting_id, stage="building_vector_store")
        # Store vector DB inside the job directory for isolation
        chroma_dir = (job_dir / "chroma_db").as_posix()
        build_vector_store(
            transcript=transcript,
            persist_directory=chroma_dir,
            collection_name=f"meeting_{meeting_id}"
        )

        # Mark as Completed
        update_meeting(
            db, 
            meeting_id,
            status="completed",
            stage="completed",
            title=title if is_url else meeting.title, # Keep file name if uploaded, use generated if YT
            summary=summary,
            action_items=action_items,
            key_decisions=key_decisions,
            open_questions=open_questions,
            chroma_path=chroma_dir
        )
        print(f"Pipeline successfully completed for {meeting_id}")
        
        # Phase 10: Cleanup large WAV files from the job directory
        try:
            for file_name in os.listdir(job_dir):
                if file_name.endswith(".wav"):
                    os.remove(job_dir / file_name)
            print(f"Cleaned up WAV files for {meeting_id}")
        except Exception as cleanup_err:
            print(f"Failed to cleanup files for {meeting_id}: {cleanup_err}")

    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Pipeline failed for {meeting_id}: {error_msg}")
        update_meeting(
            db, 
            meeting_id,
            status="error",
            stage="error",
            error_message=error_msg
        )
    finally:
        db.close()
