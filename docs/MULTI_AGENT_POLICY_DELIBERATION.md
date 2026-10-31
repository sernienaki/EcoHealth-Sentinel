# EcoHealth Sentinel: Multi-Agent Policy Deliberation

## Purpose
This module adds a policy-deliberation workflow alongside the existing surveillance, agent, policy-RAG and outbreak tabs. It does not replace existing modules. The first release is a deterministic prototype demonstrating evidence retrieval, structured perspectives, disagreement preservation and a human-review boundary. It does not call an external LLM.

It is not a clinical decision-support system. It must not diagnose, prescribe, declare outbreaks, estimate causal effects or allocate resources autonomously.

## Architecture
1. Scenario input: policy question, geography, time horizon, constraints and available aggregate indicators.
2. Evidence retrieval: reuses the existing RAG hybrid retrieval and page-level provenance. Empty retrieval is an explicit abstention.
3. Perspective generation: five bounded analytical lenses: epidemiology, health systems, equity/community, environmental health and policy critique.
4. Deliberation report: Pydantic-validated scenario, arguments, evidence, unresolved disagreements, gaps, safeguards and limitations.
5. Human review: report is downloadable; no external system action is taken.

## Components
- policy_deliberation.py: Pydantic contracts, evidence adapter and deterministic orchestration.
- policy_agent_prompts.py: versionable system guardrails and perspective prompt templates for a future LLM provider.
- policy_deliberation_ui.py: Streamlit form, perspective panels, evidence display and JSON export.
- tests/test_policy_deliberation.py: schema, abstention, provenance and safety-boundary tests.

## Evidence workflow
The module calls the existing RAG index for the selected country pack. Retrieved passages retain passage IDs, source labels and page numbers. Each passage is labelled retrieved_not_independently_verified. Retrieval is not source verification. If no index exists or no passage meets the existing retrieval threshold, the interface states that no relevant passages were retrieved.

Before operational use, maintain curated official documents and record publisher, date, jurisdiction, version and URL. Verify source authenticity and currency, and evaluate English and Kiswahili retrieval separately.

## Prompt guardrails
The prompt templates require the model to use only supplied evidence and aggregate indicators; cite supplied evidence IDs; distinguish facts, assumptions and interpretations; state uncertainty; avoid invented statistics, sources or partnerships; and preserve disagreement. Personas are simulated analytical lenses, not actual consultation.

## Interface
A ninth tab, Policy Deliberation, is added without replacing the existing eight tabs. Users enter a policy question, geography, time horizon and constraints. The interface displays perspectives, evidence, unresolved disagreements, safeguards and limitations, and exports a JSON record.

## Safeguards
- Use aggregate or de-identified information only.
- Do not enter names, phone numbers, patient identifiers or case-level personal data.
- Do not use placeholder/sample indicators for operational decisions.
- Keep human review mandatory.
- The workflow is read-only and does not write to DHIS2, GoTHoMIS or other systems.
- A future model provider must undergo security, privacy and procurement review before external data transfer.

## Evaluation
Included tests cover question validation, expected perspectives, explicit evidence abstention, evidence provenance and human-review defaults. Further evaluation should measure citation validity, retrieval recall/precision, stakeholder coverage against a human-designed roster, expert-rated argument quality, repeated-run stability, language parity, latency and cost.

Historical backtesting and perturbation testing should use only evidence available at the historical decision date. Expert review is required before claiming that simulated perspectives reflect real stakeholder views.

## Run
Install requirements, run `pytest -q`, then `streamlit run app.py`. The current module is deterministic and does not require an API key.
