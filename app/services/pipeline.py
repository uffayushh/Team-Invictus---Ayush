
import logging
import uuid

from sqlalchemy.orm import Session

from app.database.models import Paper, PaperSection, Chunk, Job, Claim, Citation
from app.parser import pymupdf_parser, grobid_client
from app.parser.pymupdf_parser import PdfParseError
from app.parser.chunker import chunk_sections
from app.embeddings.embedder import embed_texts, check_token_truncation
from app.retrieval import vector_store
from app.agents.orchestrator import run_agent_pipeline
from app.agents.state import ChunkRef

logger = logging.getLogger("pipeline")

GROBID_TIMEOUT_SECONDS = 20


def run_full_pipeline(db: Session, paper: Paper, job: Job) -> None:
    """
    Runs synchronously inside a FastAPI BackgroundTask. Updates
    paper.status / job.status / current_step at each stage so the
    frontend's polling endpoint always has something more useful to show
    than a bare "processing..." (blueprint Mistake #14).
    """
    try:
        _set_step(db, paper, job, status="parsing", step="Parsing PDF")
        sections = _parse(paper.file_path)

        _set_step(db, paper, job, status="parsing", step="Saving sections")
        section_rows = _save_sections(db, paper, sections)

        _set_step(db, paper, job, status="embedding", step="Chunking text")
        chunks = chunk_sections(sections)
        if not chunks:
            raise PdfParseError("Parsing succeeded but produced zero chunks")

        _set_step(db, paper, job, status="embedding", step=f"Embedding {len(chunks)} chunks")
        chunk_rows = _save_chunks_and_embed(db, paper, section_rows, chunks)

        _set_step(db, paper, job, status="extracting", step="Extracting claims")
        chunk_refs = [
            ChunkRef(
                chunk_id=str(row.id),
                vector_id=row.vector_id,
                text=row.text,
                section_heading=row.section.heading if row.section else None,
                page_number=row.page_number,
            )
            for row in chunk_rows
        ]
        grounded_claims, agent_trace = run_agent_pipeline(str(paper.id), chunk_refs)

        _set_step(db, paper, job, status="extracting", step="Saving grounded claims")
        _save_grounded_claims(db, paper, chunk_rows, grounded_claims)

        paper.status = "ready"
        paper.current_step = "Done"
        job.status = "done"
        job.current_step = "Done"
        db.commit()

    except PdfParseError as e:
        logger.exception("Parse failure for paper %s", paper.id)
        _fail(db, paper, job, f"Could not parse PDF: {e}")
    except Exception as e:
        logger.exception("Pipeline failure for paper %s", paper.id)
        _fail(db, paper, job, f"Unexpected error: {e}")


def _parse(file_path: str) -> list[dict]:
    from app.core.config import settings

    if getattr(settings, "GROBID_BASE_URL", None):
        try:
            return grobid_client.parse_pdf(file_path, timeout_seconds=GROBID_TIMEOUT_SECONDS)
        except PdfParseError as e:
            logger.warning("GROBID parse failed (%s), falling back to PyMuPDF", e)

    return pymupdf_parser.parse_pdf(file_path)


def _save_sections(db: Session, paper: Paper, sections: list[dict]) -> list[PaperSection]:
    rows = []
    for s in sections:
        row = PaperSection(
            paper_id=paper.id,
            heading=s["heading"],
            section_order=s["section_order"],
            raw_text=s["raw_text"],
        )
        db.add(row)
        rows.append(row)
    db.flush()  # get IDs without committing yet
    return rows


def _save_chunks_and_embed(
    db: Session, paper: Paper, section_rows: list[PaperSection], chunks
) -> list[Chunk]:
    section_by_order = {row.section_order: row for row in section_rows}

    texts = [c.text for c in chunks]
    for text in texts:
        if check_token_truncation(text):
            logger.warning("Chunk exceeds model max sequence length and will be truncated")

    embeddings = embed_texts(texts)

    chunk_rows: list[Chunk] = []
    vector_ids: list[str] = []
    metadatas: list[dict] = []

    for c, emb in zip(chunks, embeddings):
        vector_id = str(uuid.uuid4())
        section = section_by_order.get(c.section_order)
        row = Chunk(
            paper_id=paper.id,
            section_id=section.id if section else None,
            chunk_index=c.chunk_index,
            text=c.text,
            page_number=None,
            vector_id=vector_id,
        )
        db.add(row)
        chunk_rows.append(row)
        vector_ids.append(vector_id)
        metadatas.append({
            "paper_id": str(paper.id),
            "section_heading": c.section_heading,
            "chunk_index": c.chunk_index,
        })

    db.flush()

    vector_store.upsert_chunks(
        vector_ids=vector_ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    return chunk_rows


def _save_grounded_claims(
    db: Session, paper: Paper, chunk_rows: list[Chunk], grounded_claims
) -> None:
    """
    Writes grounded claims + their citations to Postgres. Ungrounded
    claims never reach this point — citation_grounder.py already dropped
    them (blueprint: the entire pitch depends on this rule holding).
    """
    chunk_by_vector_id = {row.vector_id: row for row in chunk_rows}

    for gc in grounded_claims:
        claim_row = Claim(paper_id=paper.id, claim_type=gc.claim_type, text=gc.text)
        db.add(claim_row)
        db.flush()  # need claim_row.id for the citations below

        for cite in gc.citations:
            chunk_row = chunk_by_vector_id.get(cite.chunk_id)
            if chunk_row is None:
                logger.warning("Citation referenced unknown chunk_id %s, skipping", cite.chunk_id)
                continue
            db.add(Citation(
                claim_id=claim_row.id,
                chunk_id=chunk_row.id,
                similarity_score=str(cite.similarity_score),
                entailment_score=str(cite.entailment_score),
            ))

    db.flush()


def _set_step(db: Session, paper: Paper, job: Job, status: str, step: str) -> None:
    paper.status = status
    paper.current_step = step
    job.status = "running"
    job.current_step = step
    db.commit()


def _fail(db: Session, paper: Paper, job: Job, message: str) -> None:
    paper.status = "failed"
    paper.error_message = message
    job.status = "failed"
    job.error_message = message
    db.commit()