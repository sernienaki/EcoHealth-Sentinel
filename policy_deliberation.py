"""Evidence-grounded, human-reviewed policy deliberation primitives."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: str
    source: str
    excerpt: str
    page: Optional[int] = None
    url: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verification_status: str = "retrieved_not_independently_verified"

class Argument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str
    perspective: str
    position: str
    rationale: str
    supporting_evidence: List[EvidenceItem] = Field(default_factory=list)
    objections: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    evidence_gaps: List[str] = Field(default_factory=list)

class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario_id: str = Field(default_factory=lambda: str(uuid4()))
    question: str = Field(min_length=10, max_length=2000)
    geography: str = Field(default="Unspecified", max_length=160)
    time_horizon: str = Field(default="Not specified", max_length=120)
    constraints: List[str] = Field(default_factory=list)
    indicators: dict = Field(default_factory=dict)
    data_status: str = "unspecified"

class DeliberationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: Scenario
    arguments: List[Argument]
    unresolved_disagreements: List[str] = Field(default_factory=list)
    evidence_gaps: List[str] = Field(default_factory=list)
    safeguards: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    human_review_required: bool = True
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mode: str = "deterministic_prototype"

AGENT_PROFILES = {
    "epidemiology": {"name": "Epidemiology perspective", "focus": "surveillance trends, case definitions, denominators, uncertainty and data quality", "prompt": "Interpret only supplied aggregate indicators and retrieved evidence. Do not diagnose, invent trends, or estimate effects. Identify missing denominators, time periods and case definitions."},
    "health_systems": {"name": "Health systems perspective", "focus": "workforce, supplies, referral capacity, implementation feasibility and costs", "prompt": "Assess operational feasibility under stated constraints. Do not assume resources, staffing or partnerships exist. Identify implementation dependencies."},
    "equity": {"name": "Equity and community perspective", "focus": "geographic access, affordability, disability inclusion, gender and digital exclusion", "prompt": "Identify who may benefit, be excluded or bear unintended costs. Do not claim to speak for communities; require real stakeholder validation."},
    "environmental_health": {"name": "Environmental health perspective", "focus": "WASH, climate-sensitive determinants and environmental exposure", "prompt": "Identify relevant environmental determinants and evidence gaps. Do not infer exposure or causality from absent data."},
    "policy_critic": {"name": "Policy challenge perspective", "focus": "assumptions, unintended consequences, legal and governance risks", "prompt": "Challenge the proposal, identify trade-offs and list evidence needed before action. Preserve disagreement rather than forcing consensus."},
}

def retrieve_evidence(query: str, index=None, k: int = 5) -> list[EvidenceItem]:
    """Reuse the existing RAG index; empty retrieval is an explicit abstention."""
    if index is None:
        return []
    hits = index.search(query, k=k)
    return [EvidenceItem(
        evidence_id=str(h.get("id", "unknown")),
        source=str(h.get("source", "Unspecified source")),
        excerpt=str(h.get("text", ""))[:1800],
        page=h.get("page"),
        verification_status="retrieved_not_independently_verified",
    ) for h in hits]

def build_deliberation(scenario: Scenario, evidence: list[EvidenceItem]) -> DeliberationReport:
    """Deterministic baseline; intentionally not presented as LLM reasoning."""
    note = (f"{len(evidence)} passage(s) retrieved; each requires source verification."
            if evidence else "No relevant indexed passages were retrieved; policy claims are not evidence-backed.")
    gaps = []
    if not evidence:
        gaps.append("No supporting policy or guideline passages retrieved for this scenario.")
    if not scenario.indicators:
        gaps.append("No current, validated aggregate indicators were supplied.")
    if scenario.data_status.lower() in {"placeholder", "demo", "illustrative"}:
        gaps.append("Scenario data are illustrative or placeholder and must not guide operational decisions.")
    arguments = []
    for aid, profile in AGENT_PROFILES.items():
        arguments.append(Argument(
            agent_id=aid, perspective=profile["name"],
            position=f"Review the proposal through {profile['focus']}.",
            rationale=note + " " + profile["prompt"],
            supporting_evidence=evidence,
            objections=["Do not proceed on this perspective alone; compare it with other perspectives and verified local evidence."],
            uncertainties=["This perspective has not been validated through interviews with actual stakeholders."],
            evidence_gaps=list(gaps),
        ))
    disagreements = [
        "Immediate response capacity may compete with longer-term prevention investment.",
        "Centralised reporting may improve oversight while increasing workload or excluding low-connectivity facilities.",
        "Broader data collection may improve analysis while increasing privacy and governance risks.",
    ]
    safeguards = [
        "Use aggregate or de-identified data only; never enter patient names, phone numbers or identifiers.",
        "Treat perspectives as simulated analytical lenses, not community consultation.",
        "Do not use this report for diagnosis, treatment, outbreak declaration or autonomous resource allocation.",
        "Require human review and source verification before operational use.",
    ]
    limitations = [
        "This release uses deterministic templates, not an LLM-based debate.",
        "Retrieved passages are not independently verified by this module.",
        "No causal impact estimates or intervention rankings are generated.",
        "Outputs depend on the coverage and quality of the selected country-pack evidence index.",
    ]
    return DeliberationReport(scenario=scenario, arguments=arguments,
        unresolved_disagreements=disagreements, evidence_gaps=gaps,
        safeguards=safeguards, limitations=limitations)
