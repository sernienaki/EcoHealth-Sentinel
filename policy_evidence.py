"""Evidence-note helpers for cautious policy and programme interpretation."""
from __future__ import annotations
import pandas as pd


def build_evidence_note(frame: pd.DataFrame | None, country: str, region: str) -> str:
    lines = [
        "ECOHEALTH SENTINEL — EVIDENCE NOTE",
        f"Selected context: {region}, {country}",
        "Scope: prototype decision support; not an official surveillance report.",
    ]
    if frame is None or frame.empty:
        lines.extend([
            "UN System Data Commons observations: none loaded in this session.",
            "No source-backed statistical finding can be generated from the current UN workspace.",
        ])
    else:
        lines.extend([
            f"UN observation rows currently loaded: {len(frame)}.",
            "Review each variable's DCID, source facet, provenance URL, unit, method, geographic level and reference period.",
            "Different source facets are not pooled by this tool.",
        ])
    lines.extend([
        "Limitations: country-pack dashboard values and map markers are labelled demonstration data in the prototype.",
        "Interpretation: descriptive context only; no causal inference, risk prediction or intervention recommendation is produced here.",
        "Before external circulation: verify against the original publisher and relevant Tanzania NBS, Ministry of Health or DHIS2 source; record reviewer and retrieval date.",
    ])
    return "\n".join(lines)
