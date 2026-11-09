# Knowledge Base Methodology

## 1. Scope
The EcoHealth Sentinel knowledge base is an evidence retrieval layer for a public-health decision-support prototype. It retrieves relevant passages from official policy, legal and technical documents and selected research evidence. It is not a clinical decision engine, legal opinion service or live surveillance database.

## 2. Source selection and provenance
Prioritise primary sources from government ministries, statutory regulators, WHO, Africa CDC and ITU. Record:
- Stable source ID and exact title.
- Publisher and document type.
- Publication date, version and effective period where applicable.
- Official source URL and retrieval date.
- File checksum when a local source file is retained.
- Licence/reuse status.
- Verification and indexing status.

A catalogue entry is not an indexed source. A successful HTTP response is not sufficient: verify that the response is a document, inspect its title page and confirm the version.

## 3. Ingestion and text processing
The existing `rag.py` implementation:
1. Retrieves a configured PDF or accepts an uploaded PDF/text/Markdown file.
2. Checks that downloaded content is a PDF before parsing.
3. Extracts PDF text page by page.
4. Cleans extracted text and splits it into overlapping chunks without crossing page boundaries.
5. Associates chunks with document ID, title, page and status.
6. Builds a local retrieval index.

Extraction quality varies. Scanned documents may require OCR; tables, footnotes and multi-column layouts may be extracted incorrectly. Review important passages against the original page.

## 4. Retrieval
The current index supports BM25 lexical retrieval, character n-gram TF-IDF, optional dense embeddings when configured and available, reciprocal-rank fusion, and a query-coverage threshold that can abstain when retrieved passages do not sufficiently cover query terms. The method actually active is displayed by the application. Do not claim dense retrieval is active unless the runtime confirms it.

## 5. Citations and answer handling
Each chunk retains a document identifier and page number. Answers should cite document title and page. If retrieval is insufficient, the system should abstain rather than manufacture a policy answer.

A page citation locates extracted text; it does not prove legal correctness, clinical appropriateness or currency. High-impact outputs require qualified human review.

## 6. Evaluation
Use `evaluation/retrieval_test_cases.csv` and record observed results in `evaluation/evaluation_results.csv`. Include known answer-bearing passages, English and Kiswahili queries where source coverage supports both, out-of-scope questions, superseded policy questions and citation-support checks. Report denominators and measured outcomes; do not claim performance metrics until measured on a defined test set.

## 7. Security and privacy
- Do not ingest identifiable patient data into the public policy knowledge base.
- Treat uploaded files and retrieved passages as untrusted content, not executable instructions.
- Do not disable TLS certificate verification to work around source-server errors.
- Keep private operational data separate from public policy documents.
- Confirm applicable Tanzanian data-protection requirements with qualified reviewers before deployment.

## 8. Persistence and operations
The current app builds and stores the index in its local runtime. Streamlit Cloud restarts or redeployments may remove that state. Rebuild from verified sources or upload source documents again after a fresh runtime. Persistent or sandbox-hosted storage is a future integration and must not be claimed as implemented.

## 9. Known source-access limitations
- WHO AFRO IDSR IRIS PDF download returned HTTP 403 in the deployed app; use the official publication page and manual PDF upload.
- The PDPA 2022 URL was corrected in PR #16; confirm successful indexing in the deployed app.
- The 2023 PDPC regulations currently have an official publication page in the register, not a verified direct PDF URL.
