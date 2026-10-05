from fastapi.testclient import TestClient
from backend.app.main import app
import os
import uuid

client = TestClient(app)


def test_youtube_validation_fail():
    response = client.post("/api/meetings/youtube", json={"url": "https://google.com/watch?v=123", "language": "english"})
    assert response.status_code == 400

def test_youtube_validation_pass():
    response = client.post("/api/meetings/youtube", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "language": "english"})
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    
    # Check status
    meeting_id = data["id"]
    res_status = client.get(f"/api/meetings/{meeting_id}")
    assert res_status.status_code == 200
    assert res_status.json()["status"] in ["pending", "processing"]

def test_upload_invalid_mime():
    file_content = b"fake-pdf-content"
    response = client.post(
        "/api/meetings/upload",
        files={"file": ("fake.pdf", file_content, "application/pdf")},
        data={"language": "english"}
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
