import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Job
from app.schemas.job import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail={"error": {
            "code": "job_not_found", "message": "No job with that ID."}})

    return JobStatusResponse(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status,
        current_step=job.current_step,
        error_message=job.error_message,
    )