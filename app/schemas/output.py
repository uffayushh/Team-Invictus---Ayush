import uuid
from pydantic import BaseModel


class FlashcardOut(BaseModel):
    question: str
    answer: str
    source_claim_id: uuid.UUID


class FlashcardsResponse(BaseModel):
    paper_id: uuid.UUID
    flashcards: list[FlashcardOut]


class ConceptMapNode(BaseModel):
    id: str
    label: str
    claim_type: str


class ConceptMapEdge(BaseModel):
    source: str
    target: str
    relation: str


class ConceptMapResponse(BaseModel):
    paper_id: uuid.UUID
    nodes: list[ConceptMapNode]
    edges: list[ConceptMapEdge]