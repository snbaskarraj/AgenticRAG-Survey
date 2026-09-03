"""Deterministic analysis tools the LLM is allowed to call."""

from __future__ import annotations

import json
from typing import Any, Callable

import numpy as np
import pandas as pd

from .fiscal import fiscal_label, quarter_sort_key
from .store import DataStore

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "list_catalog",
        "description": (
            "List available metrics, segments, fiscal years, event types, "
            "and the date coverage of both datasets."
        ),
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "query_metrics",
        "description": (
            "Query business metrics. Use this for point-in-time questions "
            "such as revenue in Q1 FY2026. Defaults to Company segment so "
            "segment rows are not double-counted."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "Metric name or alias, e.g. revenue, arr, nrr, win_rate.",
                },
                "fiscal_year": {
                    "description": "Fiscal year, e.g. 2026.",
                    "anyOf": [{"type": "integer"}, {"type": "array", "items": {"type": "integer"}}],
                },
                "fiscal_quarter": {
                    "description": "Fiscal quarter such as Q1.",
                    "anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}],
                },
                "start_period": {"type": "string", "description": "Inclusive YYYY-MM start."},
                "end_period": {"type": "string", "description": "Inclusive YYYY-MM end."},
                "segment": {
                    "description": "Company, Enterprise, Mid-Market, or Cloud.",
                    "anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}],
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["monthly", "quarterly", "annual"],
                    "description": "How to roll the metric up. Default monthly.",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "analyze_trend",
        "description": (
            "Compute period-over-period change, latest value, and a simple "
            "slope for one metric. Use for trend questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {"type": "string"},
                "fiscal_year": {
                    "anyOf": [{"type": "integer"}, {"type": "array", "items": {"type": "integer"}}]
                },
                "segment": {"type": "string"},
                "aggregation": {
                    "type": "string",
                    "enum": ["monthly", "quarterly", "annual"],
                    "default": "quarterly",
                },
                "periods": {
                    "type": "integer",
                    "description": "How many recent periods to include. Default 8.",
                },
            },
            "required": ["metric"],
            "additionalProperties": False,
        },
    },
    {
        "name": "detect_anomalies",
        "description": (
            "Flag unusual metric movements using a robust z-score on "
            "period-over-period percent change. Use for anomaly questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "Optional. If omitted, scan the core KPI set.",
                },
                "fiscal_year": {
                    "anyOf": [{"type": "integer"}, {"type": "array", "items": {"type": "integer"}}]
                },
                "segment": {"type": "string"},
                "aggregation": {
                    "type": "string",
                    "enum": ["monthly", "quarterly"],
                    "default": "quarterly",
                },
                "z_threshold": {"type": "number", "default": 1.8},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "search_events",
        "description": "Search business events by keyword, type, fiscal period, or impacted metric.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "event_type": {
                    "anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]
                },
                "fiscal_year": {
                    "anyOf": [{"type": "integer"}, {"type": "array", "items": {"type": "integer"}}]
                },
                "fiscal_quarter": {
                    "anyOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]
                },
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "impact_area": {"type": "string"},
                "segment": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "explain_change",
        "description": (
            "Compare a metric across two fiscal periods and return nearby "
            "business events that may explain the change."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {"type": "string"},
                "fiscal_year": {"type": "integer"},
                "fiscal_quarter": {"type": "string"},
                "compare_fiscal_year": {
                    "type": "integer",
                    "description": "Baseline fiscal year. Defaults to the prior quarter.",
                },
                "compare_fiscal_quarter": {"type": "string"},
                "segment": {"type": "string"},
            },
            "required": ["metric", "fiscal_year", "fiscal_quarter"],
            "additionalProperties": False,
        },
    },
]


def _records(df: pd.DataFrame, limit: int = 80) -> list[dict[str, Any]]:
    if df.empty:
        return []
    keep = [
        col
        for col in [
            "period",
            "fiscal_year",
            "fiscal_quarter",
            "fiscal_period",
            "segment",
            "metric_name",
            "metric_value",
            "unit",
            "event_id",
            "date",
            "event_type",
            "title",
            "description",
            "impact_area",
            "severity",
        ]
        if col in df.columns
    ]
    out = df[keep].copy()
    if "metric_value" in out.columns:
        out["metric_value"] = out["metric_value"].map(_json_number)
    return out.head(limit).to_dict(orient="records")


def _json_number(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return int(number) if number.is_integer() else round(number, 4)
    if isinstance(value, (np.integer, int)):
        return int(value)
    return value


def _period_column(df: pd.DataFrame) -> str:
    if "fiscal_period" in df.columns and df["fiscal_period"].nunique() == len(df):
        return "fiscal_period"
    if "period" in df.columns:
        return "period"
    return "fiscal_year"


def _sort_quarterly(df: pd.DataFrame) -> pd.DataFrame:
    if {"fiscal_year", "fiscal_quarter"}.issubset(df.columns):
        df = df.copy()
        df["_sort"] = [
            quarter_sort_key(int(y), str(q)) for y, q in zip(df["fiscal_year"], df["fiscal_quarter"])
        ]
        return df.sort_values("_sort").drop(columns="_sort")
    return df


class ToolBox:
    def __init__(self, store: DataStore) -> None:
        self.store = store
        self._handlers: dict[str, Callable[..., dict[str, Any]]] = {
            "list_catalog": self.list_catalog,
            "query_metrics": self.query_metrics,
            "analyze_trend": self.analyze_trend,
            "detect_anomalies": self.detect_anomalies,
            "search_events": self.search_events,
            "explain_change": self.explain_change,
        }

    def names(self) -> list[str]:
        return list(self._handlers)

    def execute(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        if name not in self._handlers:
            return {"error": f"Unknown tool: {name}"}
        try:
            result = self._handlers[name](**(arguments or {}))
            return result
        except Exception as exc:  # noqa: BLE001 - surface tool errors to the agent
            return {"error": str(exc), "tool": name}

    def list_catalog(self) -> dict[str, Any]:
        return self.store.catalog()

    def query_metrics(self, **kwargs: Any) -> dict[str, Any]:
        df = self.store.query_metrics(**kwargs)
        return {
            "row_count": int(len(df)),
            "aggregation": kwargs.get("aggregation", "monthly"),
            "rows": _records(df),
        }

    def analyze_trend(
        self,
        metric: str,
        fiscal_year: int | list[int] | None = None,
        segment: str | None = None,
        aggregation: str = "quarterly",
        periods: int = 8,
    ) -> dict[str, Any]:
        df = self.store.query_metrics(
            metric=metric,
            fiscal_year=fiscal_year,
            segment=segment,
            aggregation=aggregation,
        )
        if df.empty:
            return {"metric": metric, "row_count": 0, "series": []}
        df = _sort_quarterly(df)
        df = df.tail(int(periods)).copy()
        df["pct_change"] = df["metric_value"].pct_change() * 100
        values = df["metric_value"].astype(float).tolist()
        slope = 0.0
        if len(values) >= 2:
            slope = float(np.polyfit(range(len(values)), values, 1)[0])
        first, last = values[0], values[-1]
        total_change_pct = ((last - first) / first * 100) if first else None
        label = _period_column(df)
        series = []
        for _, row in df.iterrows():
            series.append(
                {
                    "period": row.get(label) or row.get("period"),
                    "value": _json_number(row["metric_value"]),
                    "pct_change": _json_number(row["pct_change"]),
                    "unit": row.get("unit"),
                    "segment": row.get("segment"),
                }
            )
        direction = "up" if slope > 0 else "down" if slope < 0 else "flat"
        return {
            "metric": self.store._resolve_metric(metric),
            "aggregation": aggregation,
            "latest": series[-1] if series else None,
            "start": series[0] if series else None,
            "slope_per_period": _json_number(slope),
            "total_change_pct": _json_number(total_change_pct),
            "direction": direction,
            "series": series,
        }

    def detect_anomalies(
        self,
        metric: str | None = None,
        fiscal_year: int | list[int] | None = None,
        segment: str | None = None,
        aggregation: str = "quarterly",
        z_threshold: float = 1.8,
    ) -> dict[str, Any]:
        metrics = [metric] if metric else [
            "revenue_usd",
            "arr_usd",
            "nrr_pct",
            "win_rate_pct",
            "churned_arr_usd",
            "pipeline_usd",
            "support_tickets",
            "gross_margin_pct",
        ]
        anomalies: list[dict[str, Any]] = []
        scanned = 0
        for name in metrics:
            try:
                df = self.store.query_metrics(
                    metric=name,
                    fiscal_year=fiscal_year,
                    segment=segment,
                    aggregation=aggregation,
                )
            except ValueError:
                continue
            if len(df) < 4:
                continue
            df = _sort_quarterly(df).copy()
            df["pct_change"] = df["metric_value"].pct_change() * 100
            changes = df["pct_change"].dropna()
            if changes.empty:
                continue
            median = float(changes.median())
            mad = float((changes - median).abs().median()) or 1e-9
            df["robust_z"] = (df["pct_change"] - median) / (1.4826 * mad)
            scanned += int(df["pct_change"].notna().sum())
            hits = df[df["robust_z"].abs() >= float(z_threshold)]
            label = _period_column(df)
            for _, row in hits.iterrows():
                anomalies.append(
                    {
                        "metric": name,
                        "period": row.get(label) or row.get("period"),
                        "value": _json_number(row["metric_value"]),
                        "pct_change": _json_number(row["pct_change"]),
                        "robust_z": _json_number(row["robust_z"]),
                        "direction": "up" if row["pct_change"] > 0 else "down",
                        "segment": row.get("segment"),
                        "unit": row.get("unit"),
                    }
                )
        anomalies.sort(key=lambda item: abs(item.get("robust_z") or 0), reverse=True)
        return {
            "method": "robust z-score on period-over-period percent change",
            "z_threshold": z_threshold,
            "periods_scanned": scanned,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:20],
        }

    def search_events(self, **kwargs: Any) -> dict[str, Any]:
        df = self.store.search_events(**kwargs)
        return {"row_count": int(len(df)), "rows": _records(df)}

    def explain_change(
        self,
        metric: str,
        fiscal_year: int,
        fiscal_quarter: str,
        compare_fiscal_year: int | None = None,
        compare_fiscal_quarter: str | None = None,
        segment: str | None = None,
    ) -> dict[str, Any]:
        current = self.store.query_metrics(
            metric=metric,
            fiscal_year=int(fiscal_year),
            fiscal_quarter=fiscal_quarter,
            segment=segment,
            aggregation="quarterly",
        )
        if compare_fiscal_year is None or compare_fiscal_quarter is None:
            quarter_num = int(str(fiscal_quarter).upper().replace("Q", ""))
            if quarter_num == 1:
                compare_fiscal_year = int(fiscal_year) - 1
                compare_fiscal_quarter = "Q4"
            else:
                compare_fiscal_year = int(fiscal_year)
                compare_fiscal_quarter = f"Q{quarter_num - 1}"
        baseline = self.store.query_metrics(
            metric=metric,
            fiscal_year=int(compare_fiscal_year),
            fiscal_quarter=compare_fiscal_quarter,
            segment=segment,
            aggregation="quarterly",
        )
        if current.empty or baseline.empty:
            return {
                "error": "Missing current or baseline metric rows",
                "current_rows": _records(current),
                "baseline_rows": _records(baseline),
            }
        current_value = float(current.iloc[0]["metric_value"])
        baseline_value = float(baseline.iloc[0]["metric_value"])
        delta = current_value - baseline_value
        pct = (delta / baseline_value * 100) if baseline_value else None
        resolved = self.store._resolve_metric(metric)
        events = self.store.search_events(
            fiscal_year=[int(compare_fiscal_year), int(fiscal_year)],
            impact_area=resolved.replace("_usd", "").replace("_pct", ""),
            limit=20,
        )
        if events.empty:
            events = self.store.search_events(
                fiscal_year=[int(compare_fiscal_year), int(fiscal_year)],
                limit=20,
            )
        # Keep events in the two neighboring quarters plus the current one.
        nearby = events[
            (
                (events["fiscal_year"] == int(compare_fiscal_year))
                & (events["fiscal_quarter"] == str(compare_fiscal_quarter).upper())
            )
            | (
                (events["fiscal_year"] == int(fiscal_year))
                & (events["fiscal_quarter"] == str(fiscal_quarter).upper())
            )
        ]
        if nearby.empty:
            nearby = events
        return {
            "metric": resolved,
            "current_period": f"{str(fiscal_quarter).upper()} FY{fiscal_year}",
            "baseline_period": f"{str(compare_fiscal_quarter).upper()} FY{compare_fiscal_year}",
            "current_value": _json_number(current_value),
            "baseline_value": _json_number(baseline_value),
            "delta": _json_number(delta),
            "pct_change": _json_number(pct),
            "unit": current.iloc[0].get("unit"),
            "segment": current.iloc[0].get("segment"),
            "nearby_events": _records(nearby),
        }


def dump_tool_result(result: dict[str, Any]) -> str:
    return json.dumps(result, default=str, indent=2)
