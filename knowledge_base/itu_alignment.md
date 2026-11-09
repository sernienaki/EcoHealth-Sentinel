# EcoHealth Sentinel — ITU AI Readiness Alignment

## Purpose and interpretation
This document maps the existing EcoHealth Sentinel prototype and its planned evidence layer to relevant concepts in the ITU AI Readiness Framework and the ITU AI-RE Toolkit requirements described in the organisers' reference materials.

This is a qualitative project mapping, not an official ITU assessment, certification, compliance declaration or complete implementation of the ITU AI-RE Toolkit. Only aspects relevant to this public-health use case are selected.

References: [ITU AI Ready framework](https://www.itu.int/epublications/publication/ai-ready-analysis-towards-a-standardized-readiness-framework), [organisers' reference repository](https://github.com/CrashingGuru/ITUAIReadiness), [ITU-T Y.3172](https://www.itu.int/rec/T-REC-Y.3172).

## Six-factor mapping

| ITU readiness factor | Public-health interpretation | Existing EcoHealth Sentinel evidence | Gap or next evidence needed |
|---|---|---|---|
| Data | Provenance, quality, access, privacy and representativeness of health indicators and policy documents | Country-pack metadata; demo data labelled illustrative; source register and RAG provenance documentation | No live DHIS2/eIDSR ingestion; validate access, metadata, quality and lawful basis before pilot |
| Research | Collaboration between public-health domain expertise and AI/data-science methods | Public-health use case; rule-based indicator risk logic; retrieval evaluation framework | No field validation or published model evaluation; document expert review and prospective evaluation |
| Deployment Support | Infrastructure and operational readiness for safe use in district/public-health workflows | Streamlit prototype; modular country packs; demo pipeline and agent workflow | No production hosting assurance, operational support model, uptime evidence or live integrations |
| Standards | Interoperability, safety, privacy, traceability and standards-aware architecture | Page-level RAG citations; structured country packs; Y.3172 concepts described in technical report | No formal conformance testing or certification; FHIR/GoTHoMIS integration not operational |
| Open Source and Code | Reproducible code, transparent methods and inspectable implementation | Public GitHub repository; documented RAG and evaluation methods | Add reproducible tests, dependency/version records and measured evaluation artefacts |
| Sandbox Environments | Controlled testing of data, workflows, models and policy scenarios before deployment | Demonstration environment and scenario-oriented prototype features | No evidence of ITU AI4G Sandbox hosting or formal sandbox integration |

## Selected toolkit requirement mapping
Requirement IDs below follow the organisers' reference. Status describes EcoHealth Sentinel evidence, not satisfaction of the complete ITU requirement.

| ITU requirement | Public-health adaptation | Current status |
|---|---|---|
| REQ-002 recommendations and gap analysis | Evidence-linked public-health policy gaps and preparedness recommendations | Partial/prototype; human review required |
| REQ-006 stakeholder-customised dashboards | District/public-health and policymaker views | Prototype views exist; role-specific validation needed |
| REQ-008 modular mapping to dimensions and local priorities | Country packs and configurable indicators; selected ITU factors used as an alignment lens | Partial; not a full ITU dimension-scoring implementation |
| REQ-009 multi-source metric inputs | Potential combination of indicator data and qualitative policy evidence | Partial; current values are illustrative |
| REQ-010 provenance, model lifecycle, privacy and ethics tracking | Source register, explicit data status, documented limitations and privacy safeguards | Partial; lifecycle and operational compliance evidence incomplete |
| REQ-012 cross-dimensional correlations | Consider relationships between disease signals, WASH, services and system readiness | Not demonstrated as validated analytics |
| REQ-013 language and inclusion adaptation | English/Kiswahili interface and locally relevant public-health context | Prototype capability; accessibility and language quality require evaluation |
| REQ-018 unstructured domain documents | Health laws, strategies, guidelines and technical reports | RAG ingestion implemented; corpus completeness and indexing must be verified |
| REQ-019 domain AI use cases mapped to factors | Documented public-health AI case studies tagged to relevant factors | Planned; no curated case-study corpus claimed |
| REQ-020 iterative learning and feedback | Versioned source updates and repeatable retrieval evaluation | Manual update/rebuild process; automated learning not implemented |
| REQ-022 local-language unstructured sources | Kiswahili policy and guidance documents where officially available | Planned; current source set is predominantly English |
| REQ-023 structured machine-readable application data | Country-pack JSON and source metadata | Partial; demo values are not operational surveillance data |
| REQ-024 uniform knowledge-record format | Common metadata schema proposed in `record_schema.json` | Schema documented; current runtime chunk structure is simpler |
| REQ-026 local data residency | Keep identifiable or restricted health data within authorised jurisdiction | No operational data-residency deployment demonstrated |
| REQ-027 local privacy and governance rules | Tanzanian PDPA and relevant sectoral governance sources | Policy references included; legal review and operational controls required |

## Requirements that must not be overclaimed
- REQ-015 requires the knowledge base to be hosted in the ITU AI4G Sandbox. EcoHealth Sentinel has no verified evidence of such hosting.
- REQ-016 recommends sandbox interfacing. No such integration is currently evidenced.
- REQ-005 refers to fine-tuned models. EcoHealth Sentinel does not claim a fine-tuned readiness model.
- REQ-021 concerns weighted composite scoring. Existing health indicator risk rules are not the ITU readiness scoring model.
- REQ-028 describes persistence and deletion expectations in the ITU toolkit. EcoHealth Sentinel's local runtime index and file handling have not been demonstrated to satisfy that requirement.

## Y.3172 relationship
The project technical report describes a conceptual ML pipeline mapping using Y.3172 vocabulary. This knowledge base supplies document evidence and traceability; it does not implement every Y.3172 functional component or establish conformance. Treat the mapping as architectural interpretation for this prototype, not certification.
