import uuid
from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    job_id: uuid.UUID
    job_type: str
    status: str                 # pending | running | done | failed
    current_step: str | None = None
    error_message: str | None = None