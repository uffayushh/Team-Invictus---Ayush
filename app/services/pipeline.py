"""
The one file that knows the full end-to-end order of operations
(blueprint Part 2). API routes stay thin and just call `run_full_pipeline`.

Parser choice: PyMuPDF is the default (no Docker needed). If
settings.GROBID_BASE_URL is set, we try the GROBID cloud API first and
fall back to PyMuPDF on any failure or timeout — this is the same
GROBID -> fallback swap pattern the original blueprint used, just pointed
at a public endpoint instead of a local container.
"""
import logging
import uuid

from sqlalchemy.orm import Session

from app.database.models import Paper, PaperSection, Chunk, Job
from app.parser import pymupdf_parser, grobid_client
from app.parser.pymupdf_parser import PdfParseError
from app.parser.chunker import chunk_sections
from app.embeddings.embedder import embed_texts, check_token_truncation
from app.retrieval import vector_store

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

        _set_step(db, paper, job, status="extracting", step="Ready for claim extraction")
        # NOTE: claim extraction + grounding (the agent layer) is wired in
        # separately once app/agents/orchestrator.py exists — see Part 17,
        # Day 2 of the blueprint. This function's job ends at "chunks are
        # embedded and searchable."

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