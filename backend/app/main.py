from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
import os
import sys
os.environ["PATH"] += os.pathsep + os.path.dirname(sys.executable)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.app.core.config import settings
from backend.app.api.meetings import router as meetings_router
from backend.app.db import engine, Base
from backend.app.models.meeting import Meeting  # Ensure models are imported for create_all

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Any teardown code can go here

app = FastAPI(
    title="MeetMind AI API",
    description="API for the MeetMind AI Video Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(meetings_router, prefix="/api/meetings", tags=["meetings"])

@app.get("/api/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
