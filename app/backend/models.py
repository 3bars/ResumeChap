"""SQLAlchemy ORM models for ResumeChap.

A *Resume* is a named resume aimed at a type of role (e.g. "Cloud Engineer",
"DevOps", "Linux Admin"). Each Resume owns an ordered history of *ResumeVersion*
records so users can revise, roll back, and compare versions over time.
Tags allow cataloguing/filtering resumes across the collection.
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


# Many-to-many association between resumes and tags.
resume_tags = Table(
    "resume_tags",
    Base.metadata,
    Column("resume_id", Integer, ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False, index=True)

    resumes = relationship("Resume", secondary=resume_tags, back_populates="tags")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    # Free-form label for the target role/track this resume is tailored for.
    target_role = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tags = relationship("Tag", secondary=resume_tags, back_populates="resumes")
    versions = relationship(
        "ResumeVersion",
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="ResumeVersion.version_number",
    )


class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    __table_args__ = (UniqueConstraint("resume_id", "version_number", name="uq_resume_version"),)

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    label = Column(String(200), nullable=True)  # optional human label, e.g. "Applied to Acme"
    notes = Column(Text, nullable=True)

    # resume-engine content. `content_format` describes how `content` is stored.
    #   - "markdown": free-form markdown/plain text
    #   - "structured": JSON string of structured fields (name, experience, etc.)
    content_format = Column(String(20), nullable=False, default="markdown")
    content = Column(Text, nullable=False, default="")

    # Provenance of imported content, when applicable (e.g. "resume.pdf").
    source_filename = Column(String(300), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    resume = relationship("Resume", back_populates="versions")
