
from typing import TypedDict, Literal
from pydantic import BaseModel


class ChunkRef(BaseModel):
    """A minimal reference to a chunk — enough for grounding, not the full ORM row."""
    chunk_id: str
    vector_id: str
    text: str
    section_heading: str | None = None
    page_number: int | None = None


class ExtractedClaim(BaseModel):
    claim_type: Literal["finding", "limitation", "future_work", "contribution", "metric"]
    text: str


class ExtractedClaimsList(BaseModel):
    """Schema handed to call_llm_json — the claim extractor must return exactly this shape."""
    claims: list[ExtractedClaim]


class GroundedCitation(BaseModel):
    chunk_id: str
    similarity_score: float
    entailment_score: float
    entailed: bool


class GroundedClaim(BaseModel):
    claim_type: str
    text: str
    citations: list[GroundedCitation]   


class EntailmentCheck(BaseModel):
    """Schema for the LLM-based entailment check (Mistake #4: similarity != grounded)."""
    entailed: bool
    confidence: float   # 0.0-1.0
    reason: str


class AgentState(TypedDict):
    paper_id: str
    chunks: list[ChunkRef]              
    extracted_claims: list[ExtractedClaim]
    grounded_claims: list[GroundedClaim]
    trace: list[dict]                    
    error: str | None