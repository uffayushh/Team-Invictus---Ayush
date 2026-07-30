"""
Local embedding model wrapper — sentence-transformers, runs entirely on
CPU, no API key/billing, no Docker.

`normalize_embeddings=True` is not optional (blueprint Mistake #2): Chroma's
default cosine-similarity math silently degrades without it.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings

MODEL_NAME = getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_SEQ_TOKENS = 512  # bge-small's context window; longer input is silently truncated (Mistake #21)


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of chunk texts. Returns one normalized vector per text."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """bge models recommend a query-side instruction prefix for retrieval —
    improves recall noticeably over embedding the raw query."""
    prefixed = f"Represent this sentence for searching relevant passages: {text}"
    return embed_texts([prefixed])[0]


def check_token_truncation(text: str) -> bool:
    """Rough guard against silently-truncated long chunks (Mistake #21).
    Returns True if the text likely exceeds the model's max sequence length."""
    model = _get_model()
    token_count = len(model.tokenizer.tokenize(text))
    return token_count > MAX_SEQ_TOKENS