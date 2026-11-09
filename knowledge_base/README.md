# EcoHealth Sentinel Knowledge Base

## Purpose
This knowledge base supports evidence-informed public-health surveillance, outbreak preparedness, policy interpretation and responsible AI use in the EcoHealth Sentinel prototype. It adapts the organisers' ITU AI Readiness knowledge-base submission pattern to a public-health use case. It is not a copy of the ITUAIReadiness simulation and does not claim to implement the complete ITU AI-RE Toolkit.

## Included materials
- `Inputs.md`: source collection scope and organisation.
- `source_register.csv`: provenance, intended use, verification and indexing status.
- `methodology.md`: ingestion, retrieval, citations, abstention and human review.
- `itu_alignment.md`: qualitative mapping to ITU AI Readiness factors and selected toolkit requirements.
- `record_schema.json`: proposed common metadata format for auditable knowledge records.
- `evaluation/`: reproducible retrieval test-case and result templates.
- `documents/`: source-file organisation and reuse instructions.

## Current implementation
The Streamlit **Policy Documents (RAG)** tab uses the existing `rag.py` implementation: PDF/text ingestion, page-aware chunks, BM25 and character n-gram TF-IDF retrieval, optional dense embeddings, reciprocal-rank fusion, citations, abstention and retrieval evaluation.

The index is built at runtime from country-pack documents or uploaded files. A catalogue entry does not mean a document has been downloaded or indexed. The local runtime index may not survive a Streamlit Cloud restart or redeployment; rebuild when needed.

## Evidence status and limitations
- Tanzania country-pack indicator values, map points and assistant examples are illustrative/demo data, not live DHIS2 or eIDSR feeds.
- No live DHIS2, eIDSR, GoTHoMIS/FHIR, SMS or USSD integration is claimed.
- The risk engine is rule-based, not a validated outbreak prediction model.
- HSSP V (2021–2026) is historical; its planning period ended June 2026.
- WHO AFRO IDSR PDF automated download returned HTTP 403 in the deployed app. Obtain it from the official publication page and upload it manually.
- PDPA source URL was corrected in PR #16; verify successful indexing in the deployed app.
- The 2023 PDPC regulations have an official publication page recorded, but no verified direct PDF URL.
- Retrieval citations locate extracted text; they do not establish legal interpretation, clinical validity or regulatory approval. Human review is required.
- There is no verified evidence that this knowledge base is hosted in the ITU AI for Good Sandbox.

## Build and verify
1. Review `source_register.csv`; obtain documents from official publishers.
2. Confirm title, publisher, version, date and reuse permissions.
3. Configure direct PDF URLs only when the endpoint is verified; otherwise upload a publisher-obtained file.
4. Open **Policy Documents (RAG)**, select the relevant country pack, and build the index or upload sources.
5. Record actual document/chunk counts and failures. Do not infer indexing from the catalogue.
6. Run `evaluation/retrieval_test_cases.csv`; record observed outcomes in `evaluation/evaluation_results.csv`.
7. Check every important answer against its source page and obtain qualified review for high-impact interpretation.

## Relationship to the organisers' reference
The [ITUAIReadiness repository](https://github.com/CrashingGuru/ITUAIReadiness) provides a useful pattern: input-document manifest, framework references, ingestion, knowledge-base layer and structured metadata. EcoHealth Sentinel adapts that pattern to public-health evidence and retains its existing RAG implementation. It does not import the organisers' simulation agents, scoring engine, ChromaDB implementation or national AI strategy corpus.

## Key references
- [ITU AI Ready framework publication](https://www.itu.int/epublications/publication/ai-ready-analysis-towards-a-standardized-readiness-framework)
- [ITU AI Ready report PDF](https://www.itu.int/dms_pub/itu-t/opb/ai4g/T-AI4G-AI4GOOD-2025-6-PDF-E.pdf)
- [ITU-T Y.3172](https://www.itu.int/rec/T-REC-Y.3172)
- Tanzania and WHO primary sources: see `source_register.csv`.
