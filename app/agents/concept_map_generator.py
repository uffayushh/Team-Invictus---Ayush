
import logging
from pydantic import BaseModel

from app.utils.llm_client import call_llm_json, LLMCallError

logger = logging.getLogger("concept_map_generator")

SYSTEM_PROMPT = """You are building a concept map from a list of claims extracted from
a research paper. Identify meaningful relationships between claims (e.g. "supports",
"contrasts with", "builds on", "limits"). Only connect claims that are actually related —
do not force connections. It's fine to leave some claims unconnected."""


class ConceptMapEdgeOut(BaseModel):
    source_index: int   # index into the claims list passed in
    target_index: int
    relation: str


class ConceptMapEdges(BaseModel):
    edges: list[ConceptMapEdgeOut]


def generate_concept_map_edges(claims: list[dict]) -> list[ConceptMapEdgeOut]:
    """claims: [{"index": int, "claim_type": str, "text": str}, ...]"""
    if len(claims) < 2:
        return []

    claims_text = "\n".join(f"[{c['index']}] ({c['claim_type']}) {c['text']}" for c in claims)
    prompt = f"Claims:\n{claims_text}\n\nIdentify relationships between these claims by index."

    try:
        result = call_llm_json(prompt, schema=ConceptMapEdges, system=SYSTEM_PROMPT)
        # Guard against the LLM inventing indices that don't exist
        valid_indices = {c["index"] for c in claims}
        return [
            e for e in result.edges
            if e.source_index in valid_indices and e.target_index in valid_indices
            and e.source_index != e.target_index
        ]
    except LLMCallError as e:
        logger.warning("Concept map generation failed: %s", e)
        return []