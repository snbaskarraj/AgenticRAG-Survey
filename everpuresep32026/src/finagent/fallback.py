"""Deterministic planner used when no LLM API key is configured.

The same tools run as in LLM mode, so answers stay grounded in the CSVs.
"""

from __future__ import annotations

import re
from typing import Any

from .tools import ToolBox

METRIC_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bwin[-\s]?rate\b", re.I), "win_rate_pct"),
    (re.compile(r"\bsupport tickets?\b|\btickets\b", re.I), "support_tickets"),
    (re.compile(r"\bgross margin\b|\bmargin\b", re.I), "gross_margin_pct"),
    (re.compile(r"\bnrr\b|net revenue retention", re.I), "nrr_pct"),
    (re.compile(r"\barr\b|annual recurring", re.I), "arr_usd"),
    (re.compile(r"\brevenue\b|\bsales\b", re.I), "revenue_usd"),
    (re.compile(r"\bpipeline\b", re.I), "pipeline_usd"),
    (re.compile(r"\bchurn\b", re.I), "churned_arr_usd"),
    (re.compile(r"\bnew logo\b|\bnew logos\b|\bacv\b", re.I), "new_logo_acv_usd"),
    (re.compile(r"\bexpansion\b", re.I), "expansion_acv_usd"),
    (re.compile(r"\bcac\b|acquisition cost", re.I), "cac_usd"),
    (re.compile(r"\bcustomer", re.I), "ending_customers"),
    (re.compile(r"\bheadcount\b|\bemployee", re.I), "headcount"),
    (re.compile(r"\bopex\b|operating expense", re.I), "opex_usd"),
]

SEGMENT_PATTERNS = [
    (re.compile(r"\benterprise\b", re.I), "Enterprise"),
    (re.compile(r"\bmid[-\s]?market\b|\bsmb\b", re.I), "Mid-Market"),
    (re.compile(r"\bcloud\b", re.I), "Cloud"),
]


def _find_metric(text: str) -> str | None:
    for pattern, metric in METRIC_PATTERNS:
        if pattern.search(text):
            return metric
    return None


def _find_years(text: str) -> list[int]:
    years = [int(y) for y in re.findall(r"\bFY\s*(20\d{2})\b", text, flags=re.I)]
    years += [int(y) for y in re.findall(r"\b(20\d{2})\b", text) if int(y) >= 2023]
    # de-dupe, preserve order
    seen: list[int] = []
    for year in years:
        if year not in seen:
            seen.append(year)
    return seen


def _find_quarters(text: str) -> list[str]:
    found = [f"Q{n}" for n in re.findall(r"\bQ\s*([1-4])\b", text, flags=re.I)]
    seen: list[str] = []
    for q in found:
        if q not in seen:
            seen.append(q)
    return seen


def _find_segments(text: str) -> list[str]:
    found: list[str] = []
    for pattern, segment in SEGMENT_PATTERNS:
        if pattern.search(text) and segment not in found:
            found.append(segment)
    return found


def _find_segment(text: str) -> str | None:
    segments = _find_segments(text)
    return segments[0] if segments else None


def _format_value(value: Any, unit: str | None) -> str:
    if value is None:
        return "n/a"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if unit == "USD" or (isinstance(unit, str) and "usd" in unit.lower()):
        if abs(number) >= 1_000_000_000:
            return f"${number / 1_000_000_000:.2f}B"
        if abs(number) >= 1_000_000:
            return f"${number / 1_000_000:.1f}M"
        if abs(number) >= 1_000:
            return f"${number:,.0f}"
        return f"${number:,.2f}"
    if unit == "percent" or (isinstance(value, float) and str(unit).endswith("pct")):
        return f"{number:.1f}%"
    if abs(number) >= 1000 and float(number).is_integer():
        return f"{int(number):,}"
    if float(number).is_integer():
        return str(int(number))
    return f"{number:.2f}"


class OfflinePlanner:
    def __init__(self, tools: ToolBox) -> None:
        self.tools = tools

    def run(self, question: str) -> tuple[str, list[dict[str, Any]]]:
        traces: list[dict[str, Any]] = []
        text = question.strip()
        lowered = text.lower()
        metric = _find_metric(text)
        years = _find_years(text)
        quarters = _find_quarters(text)
        segment = _find_segment(text)

        def call(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
            result = self.tools.execute(name, arguments or {})
            traces.append({"tool": name, "arguments": arguments or {}, "result": result})
            return result

        if any(word in lowered for word in ("catalog", "what can you", "available metric", "what data")):
            catalog = call("list_catalog")
            names = [row["metric_name"] for row in catalog.get("metrics", [])]
            answer = (
                "I can query the AetherData metrics and events datasets. "
                f"Metrics: {', '.join(names)}. "
                f"Coverage: {catalog.get('metrics_period_range')} "
                f"({catalog.get('fiscal_calendar')})."
            )
            return answer, traces

        if any(word in lowered for word in ("why", "explain", "caused", "reason", "what happened")):
            if not metric:
                metric = "revenue_usd"
            year = years[0] if years else 2026
            quarter = quarters[0] if quarters else "Q1"
            result = call(
                "explain_change",
                {
                    "metric": metric,
                    "fiscal_year": year,
                    "fiscal_quarter": quarter,
                    "segment": segment,
                },
            )
            return self._render_explain(result), traces

        if any(word in lowered for word in ("anomal", "unusual", "outlier", "strange", "spike")):
            result = call(
                "detect_anomalies",
                {
                    "metric": metric,
                    "fiscal_year": years or None,
                    "segment": segment,
                    "aggregation": "quarterly",
                },
            )
            return self._render_anomalies(result, metric), traces

        if any(word in lowered for word in ("trend", "over time", "trajectory", "how has", "history")):
            result = call(
                "analyze_trend",
                {
                    "metric": metric or "arr_usd",
                    "fiscal_year": years or None,
                    "segment": segment,
                    "aggregation": "quarterly",
                    "periods": 8,
                },
            )
            return self._render_trend(result), traces

        if any(word in lowered for word in ("event", "outage", "launch", "competitor", "partnership")):
            result = call(
                "search_events",
                {
                    "query": text,
                    "fiscal_year": years[0] if len(years) == 1 else years or None,
                    "fiscal_quarter": quarters[0] if len(quarters) == 1 else None,
                    "segment": segment,
                },
            )
            return self._render_events(result), traces

        if "compare" in lowered and metric:
            segments = _find_segments(text) or (["Company", segment] if segment else ["Enterprise", "Cloud"])
            current = call(
                "query_metrics",
                {
                    "metric": metric,
                    "fiscal_year": years or None,
                    "fiscal_quarter": quarters[0] if quarters else None,
                    "segment": segments,
                    "aggregation": "annual" if years and not quarters else "quarterly",
                },
            )
            return self._render_rows(current, f"Comparison for {metric}"), traces

        if metric or years or quarters:
            aggregation = "monthly"
            if years and quarters:
                aggregation = "quarterly"
            elif years:
                aggregation = "annual"
            result = call(
                "query_metrics",
                {
                    "metric": metric or "revenue_usd",
                    "fiscal_year": years or None,
                    "fiscal_quarter": quarters[0] if len(quarters) == 1 else quarters or None,
                    "segment": segment,
                    "aggregation": aggregation,
                },
            )
            label = metric or "revenue_usd"
            return self._render_rows(result, f"{label} from the metrics dataset"), traces

        catalog = call("list_catalog")
        answer = (
            "I need a metric or period to query. "
            f"Available metrics include {', '.join(row['metric_name'] for row in catalog.get('metrics', [])[:8])}. "
            "Try: “What was the revenue in Q1 FY2026?”"
        )
        return answer, traces

    def _render_rows(self, result: dict[str, Any], title: str) -> str:
        if result.get("error"):
            return f"I could not complete that query: {result['error']}"
        rows = result.get("rows") or []
        if not rows:
            return "The metrics dataset has no rows for that filter. The number is not available."
        def period_label(row: dict) -> str:
            if result.get("aggregation") == "annual" and row.get("fiscal_year"):
                return f"FY{row.get('fiscal_year')}"
            return row.get("fiscal_period") or row.get("period") or f"FY{row.get('fiscal_year')}"

        if len(rows) == 1:
            row = rows[0]
            period = period_label(row)
            value = _format_value(row.get("metric_value"), row.get("unit"))
            return (
                f"{value} ({row.get('metric_name')}, {period}, {row.get('segment')} segment; "
                f"source: metrics, {result.get('aggregation')} aggregation)."
            )
        lines = [f"{title} ({result.get('aggregation')} aggregation; source: metrics):"]
        for row in rows[:12]:
            value = _format_value(row.get("metric_value"), row.get("unit"))
            lines.append(f"- {period_label(row)} / {row.get('segment')}: {value}")
        if len(rows) > 12:
            lines.append(f"- … {len(rows) - 12} more rows")
        return "\n".join(lines)

    def _render_trend(self, result: dict[str, Any]) -> str:
        if result.get("error"):
            return f"I could not complete that trend: {result['error']}"
        if not result.get("series"):
            return "No trend series was returned for that metric."
        latest = result["latest"]
        start = result["start"]
        unit = latest.get("unit")
        return (
            f"{result['metric']} is trending {result['direction']} "
            f"({result.get('total_change_pct')}% from {start['period']} to {latest['period']}; "
            f"latest { _format_value(latest['value'], unit)}). "
            "Source: metrics via analyze_trend."
        )

    def _render_anomalies(self, result: dict[str, Any], metric: str | None) -> str:
        if result.get("error"):
            return f"I could not scan for anomalies: {result['error']}"
        anomalies = result.get("anomalies") or []
        if not anomalies:
            scope = metric or "core KPIs"
            return f"No unusual period-over-period moves were flagged for {scope} at the current threshold."
        lines = [
            f"Unusual changes (robust z-score ≥ {result.get('z_threshold')} on QoQ % change; source: metrics):"
        ]
        for item in anomalies[:8]:
            lines.append(
                f"- {item['metric']} in {item['period']}: {item['direction']} "
                f"{item['pct_change']}% (z={item['robust_z']}), value={_format_value(item['value'], item.get('unit'))}"
            )
        return "\n".join(lines)

    def _render_explain(self, result: dict[str, Any]) -> str:
        if result.get("error"):
            return f"I could not explain that change: {result['error']}"
        unit = result.get("unit")
        lines = [
            (
                f"{result['metric']} moved from {_format_value(result['baseline_value'], unit)} "
                f"in {result['baseline_period']} to {_format_value(result['current_value'], unit)} "
                f"in {result['current_period']} ({result['pct_change']}% ; source: metrics)."
            )
        ]
        events = result.get("nearby_events") or []
        if events:
            lines.append("Nearby events from the events dataset:")
            for event in events[:6]:
                lines.append(
                    f"- {event.get('date')} ({event.get('fiscal_period')}): "
                    f"{event.get('title')} [{event.get('event_type')}]"
                )
        else:
            lines.append("No nearby events were found for that window.")
        return "\n".join(lines)

    def _render_events(self, result: dict[str, Any]) -> str:
        if result.get("error"):
            return f"I could not search events: {result['error']}"
        rows = result.get("rows") or []
        if not rows:
            return "No matching events were found in the events dataset."
        lines = ["Matching events (source: events):"]
        for event in rows[:8]:
            lines.append(
                f"- {event.get('date')} ({event.get('fiscal_period')}): "
                f"{event.get('title')} — {event.get('description')}"
            )
        return "\n".join(lines)
