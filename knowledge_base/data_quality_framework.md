# Data quality and trust framework — PR #23

## Purpose
Provide transparent structural diagnostics for aggregate statistical observations. These checks are not a certification, accuracy score, representativeness assessment or substitute for source verification.

## Quality dimensions
| Dimension | Diagnostic | Interpretation |
|---|---|---|
| Completeness | Missing cells and required columns | Gaps in the retrieved table, not population-level missingness |
| Key consistency | Duplicate entity-variable-date-facet rows | Flags repeated keys; duplicates are not automatically deleted |
| Type validity | Values not parseable as numeric | Identifies values unsuitable for numeric charting without cleaning |
| Traceability | Facet count and missing provenance URLs | Indicates whether source facets and links are present |
| Temporal coverage | Earliest/latest date labels | Describes retrieved period; does not establish timeliness |
| Unit consistency | Distinct units in current view | Multiple units require separate analysis or explicit harmonisation |
| Geographic identity | Entity DCID | Identifies the selected entity; does not establish local representativeness |

## Required fields
- entity_dcid
- variable_dcid
- date
- value
- facet_id

Optional metadata include dataset, provenance_url, unit, measurement_method, observation_period, scaling_factor and is_dc_aggregate.

## Interpretation rules
1. Do not create a composite quality score from these checks.
2. Do not silently remove duplicates or impute missing values.
3. Do not compare different units or methods without a documented harmonisation method.
4. Do not merge facets by default.
5. A latest observation is not necessarily current; inspect reference date and source release.
6. Never represent a country-level value as a regional, district, facility or community estimate.
7. A successful API response does not prove the source is authoritative, accurate or fit for a decision.
8. Record retrieval date and exact variable/entity/facet selection.
9. Keep source values unchanged in exports; document any cleaning separately.
10. Verify the original publisher record and obtain qualified review before policy circulation.

## Output labels
- Structural diagnostics: computed checks.
- Descriptive summary: minimum, maximum, earliest/latest and first-to-last difference.
- Insufficient data: no numeric observations available.
- Not assessed: source evidence or metadata unavailable.

Avoid labels such as validated, accurate, high quality or safe for policy unless a separate validation process supports them.

## Operational gaps outside PR #23
- Source-level validation against publisher datasets.
- Indicator-specific timeliness thresholds.
- Geographic boundary and population-denominator validation.
- Statistical outlier review and revision history.
- Automated API uptime and schema monitoring.
- Persistent lineage and versioned extracts.
- Governance and access controls for non-public datasets.