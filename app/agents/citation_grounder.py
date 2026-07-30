
import logging

from app.agents.state import AgentState, GroundedClaim, GroundedCitation, EntailmentCheck
from app.embeddings.embedder import embed_query
from app.retrieval import vector_store
from app.utils.llm_client import call_llm_json, LLMCallError

logger = logging.getLogger("citation_grounder")

TOP_K = 5
SIMILARITY_FLOOR = 0.3          # below this, don't even bother checking entailment
ENTAILMENT_CONFIDENCE_FLOOR = 0.6

ENTAILMENT_SYSTEM_PROMPT = """You are checking whether a passage from a paper actually
supports a specific claim. Answer strictly based on what the passage states —
do not use outside knowledge.

A passage "entails" a claim if reading the passage alone would let a reader verify
the claim is true. Being on the same topic is NOT enough — the passage must actually
state or directly support the claim.
"""


def ground_claims(state: AgentState) -> AgentState:
    trace = state["trace"]
    grounded: list[GroundedClaim] = []

    for claim in state["extracted_claims"]:
        query_vec = embed_query(claim.text)
        hits = vector_store.query(query_vec, n_results=TOP_K, paper_id=state["paper_id"])

        citations: list[GroundedCitation] = []
        for hit in hits:
            similarity = 1 - hit["distance"]  # Chroma cosine distance -> similarity
            if similarity < SIMILARITY_FLOOR:
                continue

            entailment = _check_entailment(claim.text, hit["text"])
            if entailment is None:
                continue  # LLM call failed for this hit; skip rather than guess

            if entailment.entailed and entailment.confidence >= ENTAILMENT_CONFIDENCE_FLOOR:
                citations.append(GroundedCitation(
                    chunk_id=hit["id"],
                    similarity_score=round(similarity, 4),
                    entailment_score=round(entailment.confidence, 4),
                    entailed=True,
                ))

        trace.append({
            "step": "citation_grounding",
            "claim": claim.text[:80],
            "candidates_checked": len(hits),
            "citations_kept": len(citations),
        })

        if citations:
            grounded.append(GroundedClaim(
                claim_type=claim.claim_type,
                text=claim.text,
                citations=citations,
            ))
        else:
            # Ungrounded claim — dropped, never reaches an output generator
            trace.append({
                "step": "citation_grounding",
                "claim": claim.text[:80],
                "dropped": True,
                "reason": "no chunk passed entailment check",
            })

    state["grounded_claims"] = grounded
    state["trace"] = trace
    return state


def _check_entailment(claim_text: str, passage_text: str) -> EntailmentCheck | None:
    prompt = (
        f"Claim: {claim_text}\n\n"
        f"Passage: {passage_text}\n\n"
        f"Does the passage entail (directly support) the claim?"
    )
    try:
        return call_llm_json(prompt, schema=EntailmentCheck, system=ENTAILMENT_SYSTEM_PROMPT)
    except LLMCallError as e:
        logger.warning("Entailment check failed: %s", e)
        return None