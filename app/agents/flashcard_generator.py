
import logging
from pydantic import BaseModel

from app.utils.llm_client import call_llm_json, LLMCallError

logger = logging.getLogger("flashcard_generator")

SYSTEM_PROMPT = """Convert a research paper claim into a study flashcard.
The question should test understanding of the claim without giving away the answer.
The answer should be the claim itself, phrased naturally and self-contained."""


class FlashcardPair(BaseModel):
    question: str
    answer: str


def generate_flashcard(claim_text: str, claim_type: str) -> FlashcardPair | None:
    prompt = f"Claim type: {claim_type}\nClaim: {claim_text}"
    try:
        return call_llm_json(prompt, schema=FlashcardPair, system=SYSTEM_PROMPT)
    except LLMCallError as e:
        logger.warning("Flashcard generation failed for claim: %s", e)
        return None