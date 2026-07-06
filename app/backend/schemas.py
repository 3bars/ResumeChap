"""Pydantic schemas (request/response models) for the ResumeChap API."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Tags ----------
class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


# ---------- Resume Versions ----------
class VersionBase(BaseModel):
    label: Optional[str] = None
    notes: Optional[str] = None
    content_format: str = Field(default="markdown", pattern="^(markdown|structured)$")
    content: str = ""


class VersionCreate(VersionBase):
    """Create a new version under a resume (a 'revision')."""
    source_filename: Optional[str] = None


class VersionUpdate(BaseModel):
    """In-place edit of an existing version."""
    label: Optional[str] = None
    notes: Optional[str] = None
    content_format: Optional[str] = Field(default=None, pattern="^(markdown|structured)$")
    content: Optional[str] = None


class VersionOut(VersionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    resume_id: int
    version_number: int
    source_filename: Optional[str] = None
    created_at: datetime


# ---------- Resumes ----------
class ResumeBase(BaseModel):
    title: str
    target_role: Optional[str] = None
    description: Optional[str] = None


class ResumeCreate(ResumeBase):
    tags: List[str] = []
    # Optional initial content for version 1.
    content: str = ""
    content_format: str = Field(default="markdown", pattern="^(markdown|structured)$")


class ResumeUpdate(BaseModel):
    title: Optional[str] = None
    target_role: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class ResumeSummary(ResumeBase):
    """Lightweight representation for the catalog/list view."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagOut] = []
    version_count: int = 0
    latest_version_number: Optional[int] = None


class ResumeDetail(ResumeSummary):
    versions: List[VersionOut] = []


# ---------- AI engine ----------
class AISettings(BaseModel):
    enabled: bool = False
    provider: str = "abacus"  # abacus | openai | anthropic | gemini | copilot
    model: Optional[str] = None
    api_key: Optional[str] = None  # not required for abacus (uses environment)
    # For Azure/Copilot style endpoints.
    endpoint: Optional[str] = None


class AISettingsOut(BaseModel):
    enabled: bool
    provider: str
    model: Optional[str] = None
    endpoint: Optional[str] = None
    has_api_key: bool = False
    available_providers: List[str] = []


class DiffRequest(BaseModel):
    version_a_id: int
    version_b_id: int


class DiffResponse(BaseModel):
    ai_enabled: bool
    summary: str
    text_diff: str
