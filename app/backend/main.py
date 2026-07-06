"""ResumeChap backend — FastAPI application.

Serves a JSON API under /api and (in production) the built React frontend as
static files, so the whole self-hosted app runs from a single process/URL.
"""
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import ai_engine
import crud
import models
import resume_engine
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ResumeChap", version="0.1.0")

# During local dev the React dev server runs on a different port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI(title="ResumeChap API")


# ---------- Tags ----------
@api.get("/tags", response_model=List[schemas.TagOut])
def list_tags(db: Session = Depends(get_db)):
    return crud.list_tags(db)


# ---------- Resumes ----------
@api.get("/resumes", response_model=List[schemas.ResumeSummary])
def list_resumes(
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    resumes = crud.list_resumes(db, tag=tag, search=search)
    return [crud.resume_to_summary(r) for r in resumes]


@api.post("/resumes", response_model=schemas.ResumeDetail, status_code=201)
def create_resume(data: schemas.ResumeCreate, db: Session = Depends(get_db)):
    resume = crud.create_resume(db, data)
    return _resume_detail(resume)


@api.get("/resumes/{resume_id}", response_model=schemas.ResumeDetail)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")
    return _resume_detail(resume)


@api.patch("/resumes/{resume_id}", response_model=schemas.ResumeDetail)
def update_resume(resume_id: int, data: schemas.ResumeUpdate, db: Session = Depends(get_db)):
    resume = crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")
    resume = crud.update_resume(db, resume, data)
    return _resume_detail(resume)


@api.delete("/resumes/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")
    crud.delete_resume(db, resume)


# ---------- Versions ----------
@api.post("/resumes/{resume_id}/versions", response_model=schemas.VersionOut, status_code=201)
def add_version(resume_id: int, data: schemas.VersionCreate, db: Session = Depends(get_db)):
    resume = crud.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")
    return crud.add_version(db, resume, data)


@api.get("/versions/{version_id}", response_model=schemas.VersionOut)
def get_version(version_id: int, db: Session = Depends(get_db)):
    version = crud.get_version(db, version_id)
    if not version:
        raise HTTPException(404, "Version not found")
    return version


@api.patch("/versions/{version_id}", response_model=schemas.VersionOut)
def update_version(version_id: int, data: schemas.VersionUpdate, db: Session = Depends(get_db)):
    version = crud.get_version(db, version_id)
    if not version:
        raise HTTPException(404, "Version not found")
    return crud.update_version(db, version, data)


@api.delete("/versions/{version_id}", status_code=204)
def delete_version(version_id: int, db: Session = Depends(get_db)):
    version = crud.get_version(db, version_id)
    if not version:
        raise HTTPException(404, "Version not found")
    crud.delete_version(db, version)


# ---------- Import (resume-engine) ----------
@api.post("/import")
async def import_file(file: UploadFile = File(...)):
    """Parse an uploaded resume file and return its extracted content.

    The frontend uses this to pre-fill a new resume/version editor.
    """
    data = await file.read()
    try:
        content, content_format = resume_engine.parse_file(file.filename, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {
        "filename": file.filename,
        "content": content,
        "content_format": content_format,
    }


# ---------- AI engine ----------
@api.get("/ai/settings", response_model=schemas.AISettingsOut)
def get_ai_settings():
    return ai_engine.settings_public_view(ai_engine.load_settings())


@api.put("/ai/settings", response_model=schemas.AISettingsOut)
def update_ai_settings(data: schemas.AISettings):
    if data.provider not in ai_engine.AVAILABLE_PROVIDERS:
        raise HTTPException(400, f"Unknown provider: {data.provider}")
    saved = ai_engine.save_settings(data.model_dump())
    return ai_engine.settings_public_view(saved)


@api.post("/ai/diff", response_model=schemas.DiffResponse)
def diff_versions(req: schemas.DiffRequest, db: Session = Depends(get_db)):
    va = crud.get_version(db, req.version_a_id)
    vb = crud.get_version(db, req.version_b_id)
    if not va or not vb:
        raise HTTPException(404, "One or both versions not found")

    label_a = va.label or f"v{va.version_number}"
    label_b = vb.label or f"v{vb.version_number}"
    text_diff = ai_engine.build_text_diff(va.content, vb.content, label_a, label_b)

    settings = ai_engine.load_settings()
    if settings.get("enabled"):
        try:
            summary = ai_engine.summarize_diff(va.content, vb.content, label_a, label_b)
            return schemas.DiffResponse(ai_enabled=True, summary=summary, text_diff=text_diff)
        except ai_engine.AIError as exc:
            return schemas.DiffResponse(
                ai_enabled=True,
                summary=f"AI summary unavailable: {exc}",
                text_diff=text_diff,
            )
    return schemas.DiffResponse(
        ai_enabled=False,
        summary="AI engine is disabled. Enable it in Settings to get an AI-written summary of the changes.",
        text_diff=text_diff,
    )


@api.get("/health")
def health():
    return {"status": "ok"}


app.mount("/api", api)


# ---------- Static frontend (production build) ----------
_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        candidate = _FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def dev_root():
        return {
            "message": "ResumeChap API is running. Frontend build not found; "
            "run the React dev server or build the frontend.",
        }


# ---------- Serialization helper ----------
def _resume_detail(resume: models.Resume) -> dict:
    summary = crud.resume_to_summary(resume)
    summary["versions"] = resume.versions
    return summary
