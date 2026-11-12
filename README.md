# EcoHealth Sentinel

A bilingual (English and Kiswahili) public health surveillance and outbreak preparedness assistant for district teams, community health workers, NGOs, researchers and policymakers. Built for the ITU AI for Good hackathon, UAE. It starts in Tanzania and is designed to scale to other African countries through country packs.

**Status: working prototype. All indicator values, weekly series, map markers and the Kenya pack are demonstration or placeholder data. It is decision support, not a clinical tool.**

## What it does

| Area | What is built |
| --- | --- |
| Dashboard | Bullet charts against national targets, a region by indicator heatmap, and a weekly trend with an alert line |
| Risk map | Regions shaded by overall risk, scenario risk or any indicator. Tap a region to filter the whole app |
| Agents | Four agents (epidemiology, policy and legal, data protection, district medical officer) and an orchestrator, with visible reasoning steps |
| Pipeline view | The ITU Y.3172 style ML pipeline (SRC, C, PP, M, P, D, SINK) with a sandbox lane and a production lane |
| Policy RAG | Ingests official PDFs from links or uploads, hybrid search (BM25 plus character n-grams, optional dense embeddings), page level citations, abstention |
| Policy deliberation | Five deterministic analytical perspectives, existing RAG evidence retrieval, structured Pydantic report, unresolved disagreements and human review |
| Agent harness | Tool loop, input and output guardrails, step trace, optional language model brain |
| Agent computer interface | Six validated tools, forgiving inputs, structured errors and a checker on the final answer |
| Outbreak Watch | Sourced threat board with exposure by region, signal triage, readiness checklist, 42 day and 21 day countdown clocks, El Niño context |
| Country packs | One JSON file per country: regions, targets, languages, USSD networks, legal references, policy passages |
| Evaluation | Task, safety, robustness, Kiswahili, alignment, retrieval and interface tests |
| UN Data Intelligence | Read-only UN System Data Commons variable discovery, observations, facet provenance and CSV export |

## Design choices

- **Aggregate data only.** No tool reads or returns personal data. Inputs that ask for patient names or phone numbers are refused.
- **Human in the loop.** Agents recommend. District teams decide.
- **Shared risk rule.** One function sets risk for the agents, the harness and the pipeline view, with a 5% tolerance around each target.
- **Modeled on real systems.** IDSR priority diseases and alert rules, DHIS2 and EWARS style thresholds, event based surveillance triage, IHR style readiness checklists, Go.Data and SORMAS style countdown clocks.

## Repository files

```
app.py            Streamlit app (six tabs)
agents.py         Agents, shared risk rule, pipeline view
harness.py        Tool loop, guardrails, language model brain
aci.py            Agent computer interface and contract tests
rag.py            Document ingestion, hybrid search, cited answers
packs.py          Country pack loader and validator
viz.py            Bullet charts, heatmap, risk map, weekly trend
evals.py          Evaluation suite
outbreak.py       Outbreak Watch
un_data_commons.py UN System Data Commons REST client and Streamlit tab
test_un_data_commons.py Mocked API client tests
pack_tz.json      Tanzania country pack
pack_ke.json      Kenya country pack (PLACEHOLDER data)
threats.json      Sourced and dated threat board
requirements.txt  Python packages
test_ecohealth.py Tests
```

## Run it

```
pip install -r requirements.txt
streamlit run app.py
python test_ecohealth.py
python -m unittest test_un_data_commons.py
```

On Streamlit Community Cloud, set the main file to `app.py`. To use a language model, add `ANTHROPIC_API_KEY` to the app secrets. Without it everything runs on the rule based brain.

## Add a country

1. Copy `pack_tz.json` to `pack_<code>.json`, or download the blank template from the Country Pack panel.
2. Fill in regions, targets, languages, USSD networks, neighbors, entry points, legal references and documents.
3. Upload it in the Country Pack panel to check it, then commit it. The country appears in the menu with no code changes.

## Keep the threat board current

`threats.json` holds each threat with its figures, status, sources and the date it was checked. Update the entries and the `as_of` date from WHO, Africa CDC and the Ministry of Health. Figures go stale quickly, and the app shows the check date.

## Knowledge base and ITU alignment

The `knowledge_base/` directory contains the submission evidence structure for EcoHealth Sentinel's public-health use case. It adapts the organisers' ITU AI Readiness knowledge-base pattern without copying their simulation application.

- `knowledge_base/Inputs.md`: source manifest.
- `knowledge_base/source_register.csv`: provenance, verification and indexing status.
- `knowledge_base/methodology.md`: ingestion, retrieval, citations and evaluation method.
- `knowledge_base/itu_alignment.md`: qualitative mapping to the six ITU readiness factors and selected toolkit requirements.
- `knowledge_base/record_schema.json`: proposed auditable knowledge-record metadata.
- `knowledge_base/evaluation/`: retrieval test cases and results template.
- `knowledge_base/un_data_commons.md`: UN System Data Commons API integration, source-facet handling, configuration and limitations.
- `knowledge_base/documents/`: instructions for source files; copyrighted documents are not included unless redistribution is permitted.

**Important:** the manifest is not proof that all sources are indexed. The RAG index is built in the running app. See `knowledge_base/README.md` for source status, build steps and limitations. EcoHealth Sentinel does not claim ITU AI4G Sandbox hosting, formal ITU certification, live DHIS2/eIDSR integration or validated outbreak prediction.


## UN System Data Commons integration

The **UN Data Intelligence** tab provides read-only variable discovery and observation retrieval from the UN System Data Commons custom deployment. It preserves source facets and provenance metadata, and does not merge observations from different datasets. See `knowledge_base/un_data_commons.md` for API details and limitations. This is aggregate contextual statistics, not a live DHIS2 feed.

## Limitations

- Indicator data, weekly series and map markers are samples. The weekly series is simulated unless real counts are added under `weekly` in a pack.
- Kenya's data, legal passages, targets and USSD codes are placeholders.
- Regions are shaded with circles until a boundary file is added to a pack.
- The existing agents and signal triage use fixed rules, not a trained model. The policy deliberation module is also deterministic in this release; it is not an LLM debate. The triage rules are a demo and must be replaced with national case definitions.
- The interface stress test uses a scripted agent that makes deliberate mistakes. It shows that the checks work. It does not measure a language model.
- The retrieval threshold and the evaluation phrases need tuning on the real documents.
- Login and the premium button are demonstrations. Real authentication, data hosting rules and a legal review of each country's data protection law are needed before any pilot.
- Not evaluated in the field. Not clinically validated.

## Roadmap

Live DHIS2 connection, real boundary files, real weekly data, a language model evaluation of both tool sets, an MCP server for country packs, automated tests on every commit, and field pilots in one Tanzanian district and one Kenyan county.


## Stakeholder intelligence workspace (PR #23)

The additive **Stakeholder Workspace** tab provides decision-support context, structural data diagnostics and a research workspace for a mixed pilot audience. It reuses the selected role, country, region and UN observations already held in the Streamlit session. It does not change the existing dashboard, risk rules, country packs, authentication flow or UN Data Commons source records.

- `stakeholder_workspaces.py`: stakeholder-facing views.
- `data_quality.py`: structural completeness, duplicate-key, type, facet, date and provenance diagnostics.
- `indicator_interpretation.py`: descriptive summaries only; no causal inference.
- `research_laboratory.py`: facet filtering, table, time-series plot and CSV export.
- `policy_evidence.py`: evidence note with explicit prototype limitations.
- `knowledge_base/stakeholder_framework.md`: mixed-audience needs, safeguards and pilot evaluation plan.
- `knowledge_base/data_quality_framework.md`: quality dimensions, interpretation rules and limitations.
- `test_stakeholder_intelligence.py`: unit tests.

The login and role selector remain demonstration controls, not production access control. Country-pack values and map markers remain illustrative. The workspace does not persist data, schedule refreshes or infer local values from national statistics.

Run the new tests with `python -m pytest test_stakeholder_intelligence.py test_un_data_commons.py`. Run the existing suite with `python test_ecohealth.py`.
