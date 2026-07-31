import uuid
from datetime import datetime
from pydantic import BaseModel


class PaperUploadResponse(BaseModel):
    paper_id: uuid.UUID
    job_id: uuid.UUID


class PaperStatusResponse(BaseModel):
    paper_id: uuid.UUID
    status: str
    current_step: str | None = None
    error_message: str | None = None


class PaperSummaryResponse(BaseModel):
    paper_id: uuid.UUID
    title: str | None
    claims: list["ClaimOut"]


class ClaimOut(BaseModel):
    id: uuid.UUID
    claim_type: str
    text: str
    citations: list["CitationOut"]


class CitationOut(BaseModel):
    chunk_text: str
    section_heading: str | None
    page_number: int | None
    similarity_score: float | None


PaperSummaryResponse.model_rebuild()