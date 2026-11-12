# PR #24 — UN Data Navigator and plain-language data understanding

## Product objective
Help non-specialist users understand what public-health and development statistics mean, where they came from, how old they are, where they apply and what they cannot establish.

## Audience
- Government and public-health officials.
- Regional and district public-health teams.
- Health workers and community health workers.
- Universities and researchers.
- NGOs, civil-society organisations and interested community members.

## Scope delivered
1. Add an additive UN Data Navigator tab.
2. Add a metadata-led source registry with explicit connector status.
3. Add a read-only UNSD SDG API connector.
4. Add a bilingual plain-language glossary of selected indicator concepts.
5. Document connector boundaries, source governance and user-facing language principles.
6. Add mocked unit tests.

## Connector architecture
Each source has an independent registry entry. Status values distinguish existing connectors, the PR24 connector and sources documented for future discovery only.
- UN System Data Commons: existing connector from PR #22.
- UNSD SDG API: implemented in PR #24.
- WHO GHO, UNICEF Data, WHO/UNICEF JMP, UN WPP and UNdata: discovery-only; no application API integration is claimed.

Official SDG API documentation: https://unstats.un.org/sdgapi/swagger/
Implemented read-only GET endpoints:
- /v1/sdg/Goal/List?includechildren=true
- /v1/sdg/Indicator/{indicatorCode}/Series/List
- /v1/sdg/Series/{seriesCode}/GeoArea/{geoAreaCode}/DataSlice

Tanzania default geography is UN M49 code 834. The user can enter another numeric M49 code. Configuration can override the base URL using UN_SDG_API_BASE_URL. No credentials are hard-coded.

## Plain-language explanation requirements
Every source-backed explanation should show the official indicator name, plain English explanation, plain Kiswahili explanation, illustrative example, why it matters, unit and denominator, reference period, retrieval date, geography, publisher, provenance, limitations and missing metadata.

The built-in glossary is educational starter content. It is not a substitute for a source's official definition. Do not attach a generic glossary definition to a retrieved observation unless the match is explicit and reviewed.

## Interpretation safeguards
- Never invent missing values, units, years, publishers or local estimates.
- Never describe a country statistic as a regional, district, facility or village statistic.
- Distinguish survey estimates, modelled estimates, administrative data and projections.
- Do not infer causality from a trend or country comparison.
- Do not rank countries when periods, definitions, methods or units differ.
- Preserve disaggregation dimensions and footnotes where supplied.
- Do not pool source facets or series automatically.
- Label hypothetical examples as illustrative.
- If metadata are absent, say not supplied or not verified.

## Non-goals
- No WHO, UNICEF, JMP, WPP or UNdata API integration in this PR.
- No automated AI policy recommendations.
- No live DHIS2, facility or patient-level connection.
- No persistent data lake, scheduled synchronisation or cross-source harmonisation.

## Acceptance criteria
- Existing tabs and PR #22/23 functionality are retained.
- Data Navigator handles API outages without breaking other tabs.
- SDG requests use bounded timeouts and GET only.
- Invalid series and geography inputs are rejected before network calls.
- Empty responses are handled safely.
- Tanzania M49 default is 834 and editable.
- Returned observations preserve original fields and export as CSV.
- Source registry distinguishes implemented from discovery-only sources.
- Glossary has English and Kiswahili explanations and limitations.
- No secrets are committed.
- Unit tests pass; live API and UI smoke tests are recorded separately.

## Verification
Run: python -m pytest test_un_data_navigator.py test_stakeholder_intelligence.py test_un_data_commons.py
Run existing tests: python test_ecohealth.py

Manual checks: no network, valid SDG goal/series, Tanzania M49 834, invalid series, English and Kiswahili glossary, source statuses, and regression of existing PR22/23 tabs.