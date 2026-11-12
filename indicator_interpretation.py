"""Conservative descriptive interpretation of selected aggregate observations."""
from __future__ import annotations

from typing import Any
import pandas as pd


def describe_indicator(frame: pd.DataFrame, entity_dcid: str, variable_dcid: str) -> dict[str, Any]:
    """Summarise one selected entity-variable-facet slice without causal claims."""
    subset = frame.copy()
    if "entity_dcid" in subset:
        subset = subset[subset["entity_dcid"].astype(str) == str(entity_dcid)]
    if "variable_dcid" in subset:
        subset = subset[subset["variable_dcid"].astype(str) == str(variable_dcid)]
    values = pd.to_numeric(subset.get("value", pd.Series(dtype=float)), errors="coerce").dropna()
    dates = subset.get("date", pd.Series(dtype=str)).dropna().astype(str)
    units = subset.get("unit", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()
    facets = subset.get("facet_id", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()
    if values.empty:
        return {
            "status": "insufficient_data", "observation_count": 0,
            "message": "No numeric observations are available for this selection.",
        }
    ordered = subset.assign(_value=pd.to_numeric(subset["value"], errors="coerce"))
    ordered = ordered.dropna(subset=["_value"]).sort_values("date") if "date" in ordered else ordered.dropna(subset=["_value"])
    first = float(ordered["_value"].iloc[0])
    last = float(ordered["_value"].iloc[-1])
    return {
        "status": "descriptive_only",
        "observation_count": int(len(values)),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "latest_value": last,
        "latest_period": str(ordered["date"].iloc[-1]) if "date" in ordered else None,
        "earliest_value": first,
        "earliest_period": str(ordered["date"].iloc[0]) if "date" in ordered else None,
        "absolute_change_first_to_last": last - first if len(values) > 1 else None,
        "units": units,
        "facets": facets,
        "geographic_entity": entity_dcid,
        "variable_dcid": variable_dcid,
        "message": "Descriptive summary only. It does not establish causality, explain drivers, or justify a policy intervention.",
    }
