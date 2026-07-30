
import logging

from langgraph.graph import StateGraph, END

from app.agents.state import AgentState, ChunkRef, GroundedClaim
from app.agents.claim_extractor import extract_claims
from app.agents.citation_grounder import ground_claims

logger = logging.getLogger("orchestrator")


def _build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("extract_claims", extract_claims)
    graph.add_node("ground_claims", ground_claims)

    graph.set_entry_point("extract_claims")
    graph.add_edge("extract_claims", "ground_claims")
    graph.add_edge("ground_claims", END)

    return graph.compile()


_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph


def run_agent_pipeline(paper_id: str, chunks: list[ChunkRef]) -> tuple[list[GroundedClaim], list[dict]]:
    """
    Runs extract -> ground end to end for one paper.
    Returns (grounded_claims, trace) — trace is the per-step log that
    """
    initial_state: AgentState = {
        "paper_id": paper_id,
        "chunks": chunks,
        "extracted_claims": [],
        "grounded_claims": [],
        "trace": [],
        "error": None,
    }

    graph = _get_graph()

    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        logger.exception("Agent pipeline failed for paper %s", paper_id)
        # Cap retries at 2, per blueprint (no circuit breaker) — one retry here,
        # log and surface the failure if it fails again.
        try:
            final_state = graph.invoke(initial_state)
        except Exception as retry_e:
            logger.exception("Agent pipeline retry also failed for paper %s", paper_id)
            raise RuntimeError(f"Agent pipeline failed after retry: {retry_e}") from retry_e

    return final_state["grounded_claims"], final_state["trace"]