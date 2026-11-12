"""Transparent quality diagnostics for aggregate indicator datasets.

These checks describe structural completeness and consistency only. They do not
validate the truth, representativeness, timeliness, or fitness for policy use.
"""
from __future__ import annotations

from typing import Any
import pandas as pd

REQUIRED_COLUMNS = ("entity_dcid", "variable_dcid", "date", "value", "facet_id")


def assess_observations(frame: pd.DataFrame | None) -> dict[str, Any]:
    """Return reproducible, non-certifying quality diagnostics."""
    if frame is None:
        frame = pd.DataFrame()
    n = int(len(frame))
    columns = list(frame.columns)
    missing_by_column = {
        col: int(frame[col].isna().sum()) for col in columns
    }
    required_present = [col for col in REQUIRED_COLUMNS if col in columns]
    missing_required_columns = [col for col in REQUIRED_COLUMNS if col not in columns]
    required_missing_cells = sum(missing_by_column.get(col, 0) for col in required_present)
    required_cells = n * len(required_present)
    duplicate_keys = 0
    key_columns = [c for c in ("entity_dcid", "variable_dcid", "date", "facet_id") if c in columns]
    if n and len(key_columns) == 4:
        duplicate_keys = int(frame.duplicated(subset=key_columns, keep=False).sum())
    numeric_values = pd.to_numeric(frame["value"], errors="coerce") if "value" in columns else pd.Series(dtype=float)
    non_numeric_values = int(numeric_values.isna().sum()) if "value" in columns else n
    facets = int(frame["facet_id"].nunique(dropna=True)) if "facet_id" in columns else 0
    dates = frame["date"].dropna().astype(str) if "date" in columns else pd.Series(dtype=str)
    return {
        "row_count": n,
        "columns": columns,
        "missing_by_column": missing_by_column,
        "missing_required_columns": missing_required_columns,
        "required_field_completeness_pct": (
            round(100 * (1 - required_missing_cells / required_cells), 1)
            if required_cells else None
        ),
        "duplicate_key_rows": duplicate_keys,
        "non_numeric_value_rows": non_numeric_values,
        "facet_count": facets,
        "date_min": min(dates) if len(dates) else None,
        "date_max": max(dates) if len(dates) else None,
        "unit_values": sorted(frame["unit"].dropna().astype(str).unique().tolist()) if "unit" in columns else [],
        "provenance_url_missing_rows": int(frame["provenance_url"].isna().sum()) if "provenance_url" in columns else n,
        "quality_scope": "Structural diagnostics only; not a validation or certification score.",
    }
