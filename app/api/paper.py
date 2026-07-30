import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.database.models import Paper, Job
from app.schemas.paper import PaperUploadResponse, PaperStatusResponse
from app.services.pipeline import run_full_pipeline

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail={"error": {
            "code": "unsupported_file_type",
            "message": "Only PDF uploads are supported right now.",
        }})

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    paper_id = uuid.uuid4()
    file_path = os.path.join(settings.UPLOAD_DIR, f"{paper_id}.pdf")

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    paper = Paper(
        id=paper_id,
        title=file.filename,
        source_type="upload",
        file_path=file_path,
        status="pending",
    )
    db.add(paper)

    job = Job(paper_id=paper_id, job_type="process_paper", status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    return PaperUploadResponse(paper_id=paper.id, job_id=job.id)


@router.post("/{paper_id}/process", response_model=PaperStatusResponse)
def process_paper(
    paper_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail={"error": {
            "code": "paper_not_found", "message": "No paper with that ID."}})

    job = (
        db.query(Job)
        .filter(Job.paper_id == paper_id, Job.job_type == "process_paper")
        .order_by(Job.created_at.desc())
        .first()
    )
    if not job:
        job = Job(paper_id=paper_id, job_type="process_paper", status="pending")
        db.add(job)
        db.commit()
        db.refresh(job)

    if paper.status == "failed" and (paper.error_message or "").count("retry") >= 2:
        raise HTTPException(status_code=409, detail={"error": {
            "code": "max_retries_exceeded",
            "message": "This paper failed processing twice; please re-upload it.",
        }})

    background_tasks.add_task(_run_pipeline_task, paper_id, job.id)

    return PaperStatusResponse(
        paper_id=paper.id, status="parsing", current_step="Queued"
    )


def _run_pipeline_task(paper_id: uuid.UUID, job_id: uuid.UUID):
    """Runs in the BackgroundTasks thread — needs its own DB session,
    can't reuse the request-scoped one from Depends(get_db)."""
    from app.database.session import SessionLocal

    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        if paper and job:
            run_full_pipeline(db, paper, job)
    finally:
        db.close()


@router.get("/{paper_id}/status", response_model=PaperStatusResponse)
def get_paper_status(paper_id: uuid.UUID, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail={"error": {
            "code": "paper_not_found", "message": "No paper with that ID."}})

    return PaperStatusResponse(
        paper_id=paper.id,
        status=paper.status,
        current_step=paper.current_step,
        error_message=paper.error_message,
    )