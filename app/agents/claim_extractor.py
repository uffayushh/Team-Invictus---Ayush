
import logging

from app.agents.state import AgentState, ExtractedClaim, ExtractedClaimsList
from app.utils.llm_client import call_llm_json, LLMCallError

logger = logging.getLogger("claim_extractor")

SYSTEM_PROMPT = """
You are an expert academic claim extraction system.

Your task is to extract only explicit factual claims from a research paper excerpt.

Definitions:

finding:
A result or conclusion supported by experiments or analysis.

contribution:
A novel method, dataset, algorithm, framework, or system introduced by the authors.

limitation:
A stated weakness, assumption, constraint, or failure of the work.

future_work:
A statement describing planned or suggested future research.

metric:
A quantitative performance statement containing numbers, percentages, accuracy, F1, BLEU, latency, runtime, memory usage, etc.

Rules:
1. Never invent information.
2. Never summarize paragraphs.
3. Extract only complete, self-contained claims.
4. Replace pronouns like "it", "this", or "our method" with the actual subject whenever possible.
5. Preserve numerical values exactly.
6. Ignore citations such as [12], (Smith et al., 2024), etc.
7. Ignore background knowledge unless the paper explicitly presents it as a claim.
8. Return only claims supported by the provided text.
9. If there are no valid claims, return an empty list.
10. Your response must strictly conform to the provided JSON schema.
"""

# Group chunks into section-sized batches so each LLM call sees coherent context
MAX_CHUNKS_PER_CALL = 4


def extract_claims(state: AgentState) -> AgentState:
    trace = state["trace"]
    chunks = state["chunks"]
    all_claims: list[ExtractedClaim] = []

    batches = [chunks[i:i + MAX_CHUNKS_PER_CALL] for i in range(0, len(chunks), MAX_CHUNKS_PER_CALL)]

    for batch_idx, batch in enumerate(batches):
        combined_text = "\n\n".join(
            f"[Section: {c.section_heading or 'unknown'}]\n{c.text}" for c in batch
        )
        prompt = f"Extract claims from this excerpt:\n\n{combined_text}"

        try:
            result = call_llm_json(prompt, schema=ExtractedClaimsList, system=SYSTEM_PROMPT)
            all_claims.extend(result.claims)
            trace.append({
                "step": "claim_extraction",
                "batch": batch_idx,
                "claims_found": len(result.claims),
            })
        except LLMCallError as e:
            logger.warning("Claim extraction failed for batch %d: %s", batch_idx, e)
            trace.append({
                "step": "claim_extraction",
                "batch": batch_idx,
                "error": str(e),
            })
            # Don't fail the whole pipeline on one bad batch — continue with
            # what we have. A partial claim set beats a total pipeline failure
            continue

    state["extracted_claims"] = all_claims
    state["trace"] = trace
    return state