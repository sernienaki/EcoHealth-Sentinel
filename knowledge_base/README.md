# Tanzania policy knowledge base

This repository maintains two complementary knowledge resources:

1. **Public Resource Library** — a bilingual catalogue of source links for users and reviewers.
2. **AI retrieval knowledge base (RAG)** — page-aware PDF/text ingestion, chunking, hybrid retrieval, citations and abstention implemented in `rag.py`.

## Primary documents configured for RAG

| ID | Document | Publisher | Status |
|---|---|---|---|
| `pdpa2022` | Personal Data Protection Act, 2022 | Personal Data Protection Commission | Official primary-source PDF |
| `cholera_plan_2023_2027` | National Multi-Sectoral Cholera Prevention and Control Plan 2023–2027 | Tanzania Ministry of Health | Official primary-source PDF |
| `idsr3` | WHO AFRO IDSR Technical Guidelines, Third Edition | WHO Regional Office for Africa | Official primary-source PDF |
| `vision2050` | Tanzania Development Vision 2050 | National Planning Commission | Official primary-source PDF |
| `hssp5` | Health Sector Strategic Plan V, 2021–2026 | Tanzania Ministry of Health | Historical planning cycle ended June 2026 |

The Personal Data Collection and Processing Regulations, 2023 are listed in the public library. The official PDPC publication page is available, but a direct PDF URL is not configured for automated ingestion until it is confirmed. Download the PDF from the publisher and upload it through the RAG interface.

## How to make the KB available in the running app

1. Open the **Policy documents (RAG)** panel for Tanzania.
2. Select **Build index from official links**.
3. Check document/chunk counts and the retrieval method.
4. Search for questions answerable from each indexed document.
5. Expand results and verify document title, page number and passage.
6. Run retrieval evaluation and record actual results.

The public catalogue is available separately under **Public Resource Library**. It links users to original publishers; it does not itself index files.

## Evidence and safety rules

- A catalogue entry is not proof that a PDF has been downloaded or indexed.
- Only the primary-source documents listed above are configured for automated PDF ingestion.
- HSSP V is historical context, not the current health-sector strategy after June 2026.
- The old `kb` passages in `pack_tz.json` remain explicitly marked `placeholder`. Do not present them as legal quotations or verified policy requirements. Replace them only with passages checked against source PDFs.
- Do not treat illustrative country-pack indicators as current surveillance data.
- Retrieval citations show where text was extracted; they do not establish that an interpretation is legally authoritative. Human review remains necessary.
- The current app saves the generated index to a local runtime path. Streamlit-hosted local files may not persist across rebuilds or restarts; rebuild after a fresh deployment/session unless durable storage is added.
- This KB does not imply live DHIS2 connectivity, regulatory approval or operational public-health alerting.

## Source links

- PDPC Act: https://www.pdpc.go.tz/media/media/THE_PERSONAL_DATA_PROTECTION_ACT.pdf
- PDPC collection and processing regulations: https://pdpc.go.tz/publications/the-personal-data-protection-personal-data-collection-and-processing-regulations-2023/
- Tanzania cholera plan: https://www.moh.go.tz/storage/app/uploads/public/677/be0/2c8/677be02c88d8a451323386.pdf
- WHO AFRO IDSR third edition: https://iris.who.int/bitstream/handle/10665/325015/WHO-AF-WHE-CPI-05.2019-eng.pdf
- Tanzania Development Vision 2050: https://www.planning.go.tz/uploads/documents/en-1752762713-THE%20TANZANIA%20DEVELOPMENT%20VISION%202050.pdf
- HSSP V: https://mitu.or.tz/wp-content/uploads/2021/07/Tanzania-Health-Sector-Strategic-Plan-V-17-06-2021-Final-signed.pdf
