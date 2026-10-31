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
```

On Streamlit Community Cloud, set the main file to `app.py`. To use a language model, add `ANTHROPIC_API_KEY` to the app secrets. Without it everything runs on the rule based brain.

## Add a country

1. Copy `pack_tz.json` to `pack_<code>.json`, or download the blank template from the Country Pack panel.
2. Fill in regions, targets, languages, USSD networks, neighbors, entry points, legal references and documents.
3. Upload it in the Country Pack panel to check it, then commit it. The country appears in the menu with no code changes.

## Keep the threat board current

`threats.json` holds each threat with its figures, status, sources and the date it was checked. Update the entries and the `as_of` date from WHO, Africa CDC and the Ministry of Health. Figures go stale quickly, and the app shows the check date.

## Policy documents

`pack_tz.json` lists HSSP V, the Personal Data Protection Act 2022, Vision 2050, Vision 2025, the 2022 census and the IDSR technical guidelines. HSSP V covered July 2021 to June 2026, and a successor plan was reported as being finalised, so add it when it is published. Build the index from the links or upload PDFs in the Policy documents panel.

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
