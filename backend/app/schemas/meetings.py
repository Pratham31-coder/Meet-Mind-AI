from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


def _camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_camel,
        populate_by_name=True,
        ser_json_by_alias=True,
    )


class ActionItem(ApiModel):
    task: str
    owner: str | None = None
    deadline: str | None = None
    status: str = "open"


class MeetingCreateYouTube(ApiModel):
    url: HttpUrl
    language: Literal["english", "hinglish"] = "english"


class ChatMessage(ApiModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(ApiModel):
    question: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatSource(ApiModel):
    chunk_index: int
    text: str


class ChatResponse(ApiModel):
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)


class MeetingOut(ApiModel):
    id: str
    title: str | None
    source_type: str
    language: str
    status: str
    stage: str
    error_message: str | None = None
    transcript: str | None = None
    summary: str | None = None
    action_items: list[ActionItem] = Field(default_factory=list)
    key_decisions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TranscriptOut(ApiModel):
    transcript: str


class SummaryOut(ApiModel):
    summary: str
    title: str | None = None


class HealthOut(ApiModel):
    status: str
