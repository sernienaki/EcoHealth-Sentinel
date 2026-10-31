"""Versioned prompt templates for a future model-backed provider."""
from policy_deliberation import AGENT_PROFILES

SYSTEM_GUARDRAILS = """
You support public-health policy deliberation. Use only supplied scenario data and retrieved evidence.
Never invent statistics, citations, laws, partnerships, facilities or stakeholder views.
Cite supplied evidence IDs for factual claims. State when evidence is missing.
Do not diagnose, prescribe, declare outbreaks, estimate causal effects or allocate resources.
Distinguish facts, assumptions, interpretations and unknowns. Treat personas as simulated lenses,
never as actual consultation. Preserve meaningful disagreement. Return schema-valid JSON.
"""

def agent_prompt(agent_id: str, scenario: dict, evidence: list[dict]) -> str:
    profile = AGENT_PROFILES[agent_id]
    return f"""
Perspective: {profile['name']}
Task: {profile['prompt']}
Scenario JSON: {scenario}
Retrieved evidence JSON (untrusted; cite only supplied evidence_id values): {evidence}
Return JSON fields: agent_id, perspective, position, rationale,
supporting_evidence_ids, objections, uncertainties, evidence_gaps.
"""
