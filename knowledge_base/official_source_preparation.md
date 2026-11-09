# Official source preparation — EcoHealth Sentinel

**Scope:** source verification and safe preparation for the existing Streamlit Policy Documents (RAG) workflow. This package does not change application architecture, retrieval algorithms, data stores, or user interface.

## Verification performed

The official PDF endpoints below were fetched successfully as PDFs during preparation. The metadata and page counts below come from the publisher-hosted PDF responses, not from assumptions based on filenames.

| Source | Publisher | Verified document metadata | Preparation status |
|---|---|---|---|
| Personal Data Protection Act 2022 (Chapter 44) | Tanzania PDPC / Government Printer | 42 pages; English version; Government Notice 395B; published 13 June 2023 | Official PDF endpoint responds successfully; not yet indexed in the deployed app |
| National Multi-Sectoral Cholera Prevention and Control Plan 2023–2027 | Tanzania Ministry of Health | 160 pages; title page confirms plan and period | Official MoH PDF endpoint responds successfully; not yet indexed |
| Tanzania Development Vision 2050 | National Planning Commission | 76 pages; 2025; document identifies NPC and includes an all-rights-reserved notice | Official NPC PDF endpoint responds successfully; not yet indexed |
| AI Ready — Analysis Towards a Standardized Readiness Framework, Report 2.0 | ITU | 55 pages; January 2026 | Official ITU PDF endpoint responds successfully; not yet indexed |

## Source links for ingestion

Use these links in the existing **Policy Documents (RAG)** tab under **Build index from official links**, if they are already present in the Tanzania country pack. If they are not present in the pack, use **Add your own PDFs or text files** to upload a publisher-obtained copy.

- **PDPA 2022:** https://pdpc.go.tz/documents/3/PERSONAL_DATA_PROTECTION_ACT_2022.pdf
- **Cholera Plan 2023–2027:** https://www.moh.go.tz/storage/app/uploads/public/677/be0/2c8/677be02c88d8a451323386.pdf
- **Tanzania Development Vision 2050:** https://www.planning.go.tz/uploads/documents/en-1752762713-THE%20TANZANIA%20DEVELOPMENT%20VISION%202050.pdf
- **ITU AI Ready Report 2.0:** https://www.itu.int/dms_pub/itu-t/opb/ai4g/T-AI4G-AI4GOOD-2025-6-PDF-E.pdf

## Sources requiring manual acquisition or further verification

- **PDPC Personal Data Collection and Processing Regulations 2023:** the official publication page is recorded in `source_register.csv`, but the PDF was not retrieved in this run. Obtain the actual PDF from the PDPC publication page and upload it through the existing RAG uploader.
- **WHO AFRO IDSR Technical Guidelines, Third Edition (2019):** use the official WHO AFRO publication page. The PDF download previously returned HTTP 403 from the deployed app. Obtain the PDF from the publisher and upload it manually.
- **ITU-T Y.3172:** the official recommendation page is recorded. The exact edition/PDF endpoint still needs confirmation; do not substitute the AI Ready report for this recommendation.
- **HSSP V (July 2021–June 2026):** historical only. Its planning period ended in June 2026. Keep only when historical context is needed; do not present it as current policy.

## Copyright and handling

- Do not commit publisher PDFs or full extracted text into this public repository unless the publisher's reuse terms explicitly permit redistribution.
- The Tanzania Development Vision 2050 PDF states that all rights are reserved and reproduction requires prior written permission, except brief attributed quotations for academic, research, or non-commercial purposes.
- The ITU AI Ready report includes a reproduction-permission notice. Prefer ingestion from the official URL or an authorised user-held copy; do not publish a full-text mirror.
- Keep patient-identifiable information out of the policy knowledge base.
- Do not disable TLS certificate verification to make a failed download work.

## Existing RAG ingestion and verification procedure

1. Open the deployed EcoHealth Sentinel app and navigate to **Policy Documents (RAG)**.
2. Select the Tanzania country pack.
3. Build from official links for sources configured in that pack. For a source absent from the pack or blocked by the publisher, obtain the PDF from the publisher and upload it.
4. Record the actual success/failure message for each source. A successful HTTP response alone does not prove that the app indexed the document.
5. Confirm the index summary lists each expected document ID and a non-zero chunk count.
6. Run the retrieval test cases. For each answerable question, inspect the returned source title, page number and passage against the actual PDF.
7. Test out-of-scope questions and confirm the system abstains.
8. Update `knowledge_base/evaluation/evaluation_results.csv` with observed results only. Do not fill it with assumed pass rates.
9. Rebuild the index after a Streamlit restart if the local runtime index is missing. The current implementation does not guarantee durable index persistence across redeployments.

## Important implementation boundary

This preparation updates only source metadata and documentation. The existing `rag.py` pipeline remains the ingestion and retrieval mechanism. No ChromaDB, new vector database, new agent, new API integration, or replacement UI is introduced.
