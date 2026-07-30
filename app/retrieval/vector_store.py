"""
Chroma running embedded (in-process, PersistentClient) — no server, no
Docker. Data persists to disk at settings.CHROMA_PERSIST_DIR between
restarts.
"""
import chromadb

from app.core.config import settings

COLLECTION_NAME = "paper_chunks"

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def upsert_chunks(
    vector_ids: list[str],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    """metadatas should include at least: paper_id, chunk_id, section_heading, page_number."""
    collection = _get_collection()
    collection.upsert(
        ids=vector_ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def query(
    query_embedding: list[float],
    n_results: int = 8,
    paper_id: str | None = None,
) -> list[dict]:
    """Returns [{id, text, metadata, distance}, ...] sorted by relevance."""
    collection = _get_collection()
    where = {"paper_id": paper_id} if paper_id else None

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
    )

    hits = []
    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]

    for vid, doc, meta, dist in zip(ids, docs, metas, dists):
        hits.append({"id": vid, "text": doc, "metadata": meta, "distance": dist})
    return hits


def delete_paper_vectors(paper_id: str) -> None:
    """Called when a paper is deleted, keeps Chroma from accumulating orphans."""
    collection = _get_collection()
    collection.delete(where={"paper_id": paper_id})