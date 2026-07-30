import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Paper, Claim
from app.schemas.output import (
    FlashcardOut, FlashcardsResponse,
    ConceptMapNode, ConceptMapEdge, ConceptMapResponse,
)
from app.agents.flashcard_generator import generate_flashcard
from app.agents.concept_map_generator import generate_concept_map_edges

router = APIRouter(prefix="/papers", tags=["outputs"])


def _require_ready_paper(db: Session, paper_id: uuid.UUID) -> Paper:
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail={"error": {
            "code": "paper_not_found", "message": "No paper with that ID."}})
    if paper.status != "ready":
        raise HTTPException(status_code=409, detail={"error": {
            "code": "paper_not_ready",
            "message": f"Paper is still processing (status: {paper.status}).",
        }})
    return paper


@router.get("/{paper_id}/flashcards", response_model=FlashcardsResponse)
def get_flashcards(paper_id: uuid.UUID, db: Session = Depends(get_db)):
    paper = _require_ready_paper(db, paper_id)
    claims = db.query(Claim).filter(Claim.paper_id == paper_id).all()

    if not claims:
        raise HTTPException(status_code=404, detail={"error": {
            "code": "no_claims",
            "message": "No grounded claims found for this paper — nothing to generate flashcards from.",
        }})

    flashcards = []
    for claim in claims:
        pair = generate_flashcard(claim.text, claim.claim_type)
        if pair:
            flashcards.append(FlashcardOut(
                question=pair.question, answer=pair.answer, source_claim_id=claim.id,
            ))

    return FlashcardsResponse(paper_id=paper.id, flashcards=flashcards)


@router.get("/{paper_id}/concept-map", response_model=ConceptMapResponse)
def get_concept_map(paper_id: uuid.UUID, db: Session = Depends(get_db)):
    paper = _require_ready_paper(db, paper_id)
    claims = db.query(Claim).filter(Claim.paper_id == paper_id).all()

    if not claims:
        raise HTTPException(status_code=404, detail={"error": {
            "code": "no_claims", "message": "No grounded claims found for this paper."}})

    nodes = [
        ConceptMapNode(id=str(c.id), label=c.text[:100], claim_type=c.claim_type)
        for c in claims
    ]

    indexed = [{"index": i, "claim_type": c.claim_type, "text": c.text} for i, c in enumerate(claims)]
    edge_results = generate_concept_map_edges(indexed)

    edges = [
        ConceptMapEdge(
            source=str(claims[e.source_index].id),
            target=str(claims[e.target_index].id),
            relation=e.relation,
        )
        for e in edge_results
    ]

    return ConceptMapResponse(paper_id=paper.id, nodes=nodes, edges=edges)