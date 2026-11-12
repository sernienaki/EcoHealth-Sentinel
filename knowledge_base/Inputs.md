# EcoHealth Sentinel Knowledge Base — Input Manifest

This manifest describes the intended evidence collection for the Tanzania public-health prototype. It is a source plan, not proof that every item has been downloaded or indexed.

## 1. ITU framework and technical architecture

| Source | Type | Intended use | Status |
|---|---|---|---|
| ITU AI Ready: Analysis Towards a Standardized Readiness Framework, Report 2.0 | International framework | Reference six AI readiness factors and relevant dimensions/requirements | Official publication link recorded; obtain and verify local copy |
| ITU-T Y.3172, Architectural framework for machine learning in future networks including IMT-2020 | Technical recommendation | Architecture vocabulary for ML pipeline mapping | Official recommendation link recorded; obtain and verify applicable edition |

## 2. Tanzania health, law and policy

| Source | Type | Intended use | Status |
|---|---|---|---|
| Personal Data Protection Act, 2022 | Law | Personal-data governance context | Official PDPC PDF URL configured; live ingestion must be verified |
| Personal Data Collection and Processing Regulations, 2023 | Regulation | Data processing requirements | Official PDPC publication page recorded; direct PDF not confirmed |
| National Multi-Sectoral Cholera Prevention and Control Plan 2023–2027 | National plan | Cholera prevention and response context | Official Ministry PDF configured; index status must be checked |
| Tanzania Development Vision 2050 | National strategy | Long-term development context | Official National Planning Commission PDF configured; index status must be checked |
| Health Sector Strategic Plan V, July 2021–June 2026 | Historical sector strategy | Historical health-system planning context only | Historical; not a current strategy after June 2026 |

## 3. Public-health technical guidance

| Source | Type | Intended use | Status |
|---|---|---|---|
| WHO AFRO Technical Guidelines for Integrated Disease Surveillance and Response, Third Edition (2019) | Technical guideline | IDSR concepts and surveillance response guidance | Official WHO publication page recorded; automated IRIS PDF download returned HTTP 403; manual upload required |

## 4. Future evidence categories
Add sources only when publisher, version, date, relevance and permissions can be verified:
- WHO and Africa CDC technical guidance on surveillance and outbreak preparedness.
- Official Tanzania health-sector policies and disease-specific guidelines.
- Digital health, interoperability and health information exchange standards.
- Peer-reviewed public-health AI and evaluation studies.
- Documented public-health AI case studies mapped to relevant ITU readiness factors.

## 5. Exclusions and safeguards
- Do not ingest patient-identifiable records, case line lists or confidential facility data into this public knowledge base.
- Do not treat demo indicator values or illustrative map markers as source documents.
- Do not convert unverified country-pack placeholder passages into policy quotations.
- Keep superseded documents labelled historical and record their effective period.
- Store source files only where licence and publisher terms permit redistribution; otherwise provide official links and use an authorised upload workflow.


## 6. UN System Data Commons — aggregate statistical observations

| Source | Type | Intended use | Status |
|---|---|---|---|
| UN System Data Commons REST V2 custom deployment | Statistical knowledge graph/API | Discover statistical variables and retrieve aggregate observations for country-level context and cross-country analysis | Integration documented in `un_data_commons.py`; runtime availability and each variable's source facet, date range, unit and provenance must be verified before use |

Official technical references:
- UN System Data Commons getting started: https://data.un.org/undatacommons/docs/getting-started
- UN Statistics Division API examples: https://github.com/UNStats/OpenSourceWeek2026
- REST V2 observation API: https://docs.datacommons.org/api/rest/v2/observation
- REST V2 resolve API: https://docs.datacommons.org/api/rest/v2/resolve

The API integration does not establish that a particular Tanzania indicator is available. Variable DCIDs and observations are discovered at runtime and must be verified individually.
