# UN System Data Commons integration

## Purpose and scope

EcoHealth Sentinel includes an exploratory, read-only interface to the UN System Data Commons REST API. It is intended to retrieve aggregate statistical observations for contextual public-health analysis. It is not a live DHIS2, eIDSR or facility reporting connection.

## Deployment and API base URL

Default custom-instance API base:

`https://unsd-datacommons.gcp.un-icc.cloud/core/api/v2`

The base can be overridden with `UN_DATA_COMMONS_BASE_URL`. The configured value should include `/core/api/v2` and must be an HTTPS URL.

The UN deployment is a Custom Data Commons instance. The published UN System Data Commons getting-started material documents GET access to `/resolve`, `/node` and `/observation`, and says the Postman environment's API key can be left blank for a custom deployment. This implementation uses GET requests and does not send a public Data Commons API key.

## Implemented workflow

1. Search a statistical variable through `GET /resolve` with `resolver=indicator`.
2. Review returned DCIDs and matching descriptions.
3. Query `GET /observation` for an entity DCID and selected variable DCID.
4. Request `date`, `value`, `entity`, `variable` and `facet` fields.
5. Preserve each source facet as a separate observation series.
6. Display the returned observations, source metadata and a CSV export.

The default entity is `country/TZA`. Users can enter another verified geographic DCID.

## Source facets and comparability

A variable/entity pair can have multiple facets representing different datasets or measurement methods. The app preserves facet ID, dataset/import name, provenance URL, unit, measurement method, observation period, scaling factor and aggregate flag when supplied. It does not sum or silently merge facets. Analysts must select a consistent facet before constructing a comparable time series.

Do not compare observations across different units, methods, reference periods or geographic levels without an explicit harmonisation method.

## Evidence and limitations

- The UI discovers variables at runtime; it does not assume a fixed catalogue of Tanzania indicators.
- Availability, dates, units and source organisations must be checked from each returned response.
- A national observation must not be represented as a regional or district estimate.
- UN statistical observations are contextual aggregate data and do not replace Tanzania NBS, Ministry of Health or DHIS2 administrative data.
- No indicator should be treated as current until its reference period and source metadata are checked.
- The integration is read-only and does not write UN data back to the source.
- No automated scheduled refresh, persistent cache or local database ingestion is introduced in this initial UI integration.
- The app's existing demo data remain demo data; UN observations are displayed separately.
- This feature is an exploratory data access tool, not a validated surveillance or outbreak prediction model.

## Configuration

Optional environment variable:

```text
UN_DATA_COMMONS_BASE_URL=https://unsd-datacommons.gcp.un-icc.cloud/core/api/v2
```

No API key is configured for the documented UN custom deployment. Do not add credentials unless the UN deployment's current documentation explicitly requires them.

## Verification

Run:

```bash
python test_ecohealth.py
```

Unit tests mock HTTP responses and verify request parameters, response parsing, facet provenance retention and error handling. They do not prove the remote service is available at runtime. A live check should be performed from the deployed environment and the retrieval date recorded before using results in a policy brief.

## Official references

- [UN System Data Commons getting started](https://data.un.org/undatacommons/docs/getting-started)
- [UN Statistics Division OpenSourceWeek2026 API examples](https://github.com/UNStats/OpenSourceWeek2026)
- [Data Commons REST V2 observation API](https://docs.datacommons.org/api/rest/v2/observation)
- [Data Commons REST V2 resolve API](https://docs.datacommons.org/api/rest/v2/resolve)
- [Using the UN System Data Commons with R](https://cran.r-project.org/web/packages/datacommons/vignettes/using-un-data-commons.html)
