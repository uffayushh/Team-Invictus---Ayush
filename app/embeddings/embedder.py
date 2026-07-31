import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger("embedder")

EMBEDDING_MODEL = getattr(settings, "GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2
BATCH_SIZE = 20


class EmbeddingError(Exception):
    pass


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    all_vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        all_vectors.extend(_embed_batch(batch, task_type="RETRIEVAL_DOCUMENT"))

    return all_vectors


def embed_query(text: str) -> list[float]:
    vectors = _embed_batch([text], task_type="RETRIEVAL_QUERY")
    return vectors[0]


def check_token_truncation(text: str) -> bool:
    approx_tokens = len(text.split()) * 1.3
    return approx_tokens > 2000


def _embed_batch(texts: list[str], task_type: str) -> list[list[float]]:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise EmbeddingError("GEMINI_API_KEY is not configured")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/{EMBEDDING_MODEL}:batchEmbedContents"
        f"?key={api_key}"
    )
    requests_payload = [
        {
            "model": EMBEDDING_MODEL,
            "content": {"parts": [{"text": t}]},
            "taskType": task_type,
        }
        for t in texts
    ]

    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            start = time.monotonic()
            resp = httpx.post(url, json={"requests": requests_payload}, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            elapsed = time.monotonic() - start
            logger.info(
                "embed_batch size=%d task_type=%s attempt=%d elapsed=%.2fs",
                len(texts), task_type, attempt, elapsed,
            )
            return [item["values"] for item in data["embeddings"]]
        except httpx.TimeoutException as e:
            last_error = e
            logger.warning("embed_batch timed out attempt=%d/%d", attempt, MAX_RETRIES + 1)
        except httpx.HTTPStatusError as e:
            last_error = e
            logger.warning("embed_batch HTTP error attempt=%d/%d: %s", attempt, MAX_RETRIES + 1, e)
        except (KeyError, IndexError) as e:
            last_error = e
            logger.warning("embed_batch malformed response attempt=%d/%d: %s", attempt, MAX_RETRIES + 1, e)

    raise EmbeddingError(f"Embedding request failed after {MAX_RETRIES + 1} attempts: {last_error}")ize(text))
    return token_count > MAX_SEQ_TOKENS
