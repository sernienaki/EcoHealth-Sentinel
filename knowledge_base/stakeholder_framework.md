# Stakeholder framework — PR #23

## Purpose
Integrated public-health intelligence for a mixed pilot audience: government/public-health officials, researchers, health workers and civil-society organisations. This is an additive presentation layer, not production role-based access control.

## Stakeholder needs and boundaries
| Stakeholder | Intended use | Boundary |
|---|---|---|
| Government and public-health officials | Review source-backed trends, reference periods and evidence gaps | No recommendations from unverified or demonstration values |
| Regional/district teams | Identify local evidence needs and distinguish national context | National observations are not district estimates |
| Health workers and CHWs | Understand community-health context in accessible language | No patient records, clinical advice or live reporting connection |
| Researchers/universities | Inspect definitions, facets, missingness, units and export data | No causal inference or automated modelling in this release |
| NGOs and civil society | Review contextual evidence and information gaps | No beneficiary estimates or programme impact claims |

## Shared design principles
1. Reuse the existing country, region, role and session state; do not duplicate data stores.
2. Keep demonstration country-pack values, imported datasets and UN observations visibly distinct.
3. Preserve entity DCID, variable DCID, source facet, dataset, provenance URL, unit, method and reference period where available.
4. Never silently pool different facets or geographic levels.
5. Explain missingness, reference period, geographic coverage and source limitations.
6. Outputs organise evidence; qualified staff and researchers interpret it.
7. Provide English and Kiswahili interface guidance without implying every source document is translated.
8. Use aggregate observations only; do not ingest identifiable patient or case-line-list data.

## Implemented in PR #23
- Additive Stakeholder Workspace tab in app.py.
- stakeholder_workspaces.py: decision-support, data-quality and research views.
- data_quality.py: structural completeness, duplicate-key, type, facet, date and provenance diagnostics.
- indicator_interpretation.py: descriptive summaries only.
- research_laboratory.py: facet filtering, table, time-series plot and CSV export.
- policy_evidence.py: conservative evidence note.
- test_stakeholder_intelligence.py: unit tests.

## Current limitations
- Sign-in and role selector are demonstration controls, not production authentication or access control.
- Country-pack dashboard values and map markers remain illustrative.
- UN coverage depends on the selected variable and source facet.
- The workspace reads observations already retrieved in the current Streamlit session; no persistence or scheduled refresh is added.
- No district or facility value is inferred from national observations.
- No external partnership, live reporting integration or production deployment is claimed.

## Mixed pilot validation
Conduct task-based walkthroughs with at least one representative from each stakeholder group using verified aggregate data and clearly labelled demo data.
- Official: trace source, period and geography; prepare a caveated evidence note.
- District team: distinguish national context from local operational data and identify the missing local source.
- Researcher: select a facet, inspect diagnostics and export a reproducible CSV.
- Health worker/CHW: explain in Kiswahili what an indicator can and cannot say.
- NGO/CSO: identify an evidence gap without inferring beneficiary counts or impact.

Measure task completion, time on task, correct source/period/geography identification, export success, Kiswahili comprehension and unsafe interpretation frequency. Report denominators and measured results; do not pre-populate success rates.

## Acceptance criteria
- Existing 12 tabs and workflows remain present.
- New workspace uses existing selected role, country and region.
- No existing country-pack values, risk rules, UN observations or policy documents are overwritten.
- Empty UN observation state is handled safely.
- Facets remain separable; no default pooling.
- Diagnostics are not presented as a validity score.
- Summaries make no causal or policy-effect claims.
- CSV export contains only the current aggregate observation view.
- English and Kiswahili guidance is available.
- Tests pass in the project environment before merge.