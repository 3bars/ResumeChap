"""Database operations (CRUD) for resumes, versions, and tags."""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas


# ---------- Tags ----------
def get_or_create_tags(db: Session, names: List[str]) -> List[models.Tag]:
    tags: List[models.Tag] = []
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        tag = db.query(models.Tag).filter(func.lower(models.Tag.name) == name.lower()).first()
        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def list_tags(db: Session) -> List[models.Tag]:
    return db.query(models.Tag).order_by(models.Tag.name).all()


# ---------- Resumes ----------
def create_resume(db: Session, data: schemas.ResumeCreate) -> models.Resume:
    resume = models.Resume(
        title=data.title,
        target_role=data.target_role,
        description=data.description,
        tags=get_or_create_tags(db, data.tags),
    )
    db.add(resume)
    db.flush()

    # Seed with version 1.
    first = models.ResumeVersion(
        resume_id=resume.id,
        version_number=1,
        content=data.content or "",
        content_format=data.content_format,
        label="Initial version",
    )
    db.add(first)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes(db: Session, tag: Optional[str] = None, search: Optional[str] = None) -> List[models.Resume]:
    query = db.query(models.Resume)
    if tag:
        query = query.join(models.Resume.tags).filter(func.lower(models.Tag.name) == tag.lower())
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            func.lower(models.Resume.title).like(like)
            | func.lower(func.coalesce(models.Resume.target_role, "")).like(like)
            | func.lower(func.coalesce(models.Resume.description, "")).like(like)
        )
    return query.order_by(models.Resume.updated_at.desc()).all()


def get_resume(db: Session, resume_id: int) -> Optional[models.Resume]:
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()


def update_resume(db: Session, resume: models.Resume, data: schemas.ResumeUpdate) -> models.Resume:
    if data.title is not None:
        resume.title = data.title
    if data.target_role is not None:
        resume.target_role = data.target_role
    if data.description is not None:
        resume.description = data.description
    if data.tags is not None:
        resume.tags = get_or_create_tags(db, data.tags)
    db.commit()
    db.refresh(resume)
    return resume


def delete_resume(db: Session, resume: models.Resume) -> None:
    db.delete(resume)
    db.commit()


# ---------- Versions ----------
def _next_version_number(db: Session, resume_id: int) -> int:
    current_max = (
        db.query(func.max(models.ResumeVersion.version_number))
        .filter(models.ResumeVersion.resume_id == resume_id)
        .scalar()
    )
    return (current_max or 0) + 1


def add_version(db: Session, resume: models.Resume, data: schemas.VersionCreate) -> models.ResumeVersion:
    version = models.ResumeVersion(
        resume_id=resume.id,
        version_number=_next_version_number(db, resume.id),
        label=data.label,
        notes=data.notes,
        content=data.content,
        content_format=data.content_format,
        source_filename=data.source_filename,
    )
    db.add(version)
    # Touch the parent so updated_at reflects the revision.
    resume.updated_at = func.now()
    db.commit()
    db.refresh(version)
    return version


def get_version(db: Session, version_id: int) -> Optional[models.ResumeVersion]:
    return db.query(models.ResumeVersion).filter(models.ResumeVersion.id == version_id).first()


def update_version(db: Session, version: models.ResumeVersion, data: schemas.VersionUpdate) -> models.ResumeVersion:
    if data.label is not None:
        version.label = data.label
    if data.notes is not None:
        version.notes = data.notes
    if data.content_format is not None:
        version.content_format = data.content_format
    if data.content is not None:
        version.content = data.content
    db.commit()
    db.refresh(version)
    return version


def delete_version(db: Session, version: models.ResumeVersion) -> None:
    db.delete(version)
    db.commit()


# ---------- Helpers for serialization ----------
def resume_to_summary(resume: models.Resume) -> dict:
    version_numbers = [v.version_number for v in resume.versions]
    return {
        "id": resume.id,
        "title": resume.title,
        "target_role": resume.target_role,
        "description": resume.description,
        "created_at": resume.created_at,
        "updated_at": resume.updated_at,
        "tags": resume.tags,
        "version_count": len(resume.versions),
        "latest_version_number": max(version_numbers) if version_numbers else None,
    }
