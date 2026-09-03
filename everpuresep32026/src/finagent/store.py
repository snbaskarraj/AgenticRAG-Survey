"""Load and query the metrics and events datasets.

Column aliases let the same store accept the interview sample files
once they arrive, as long as the meaning of each column is recognizable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from . import config
from .fiscal import (
    fiscal_label,
    fiscal_quarter,
    fiscal_year,
    normalize_quarter,
    parse_period,
    period_label,
)

METRIC_ALIASES = {
    "period": ["period", "month", "date", "as_of", "asof", "period_date"],
    "fiscal_year": ["fiscal_year", "fy", "fiscalyear", "year"],
    "fiscal_quarter": ["fiscal_quarter", "quarter", "fq", "qtr"],
    "segment": ["segment", "business_unit", "region", "product", "line_of_business"],
    "metric_name": ["metric_name", "metric", "kpi", "measure", "name"],
    "metric_value": ["metric_value", "value", "amount", "metric_amount"],
    "unit": ["unit", "uom", "currency"],
    "metric_kind": ["metric_kind", "kind", "aggregation_type"],
    "description": ["description", "metric_description"],
    "fiscal_period": ["fiscal_period", "period_label"],
}

EVENT_ALIASES = {
    "event_id": ["event_id", "id", "eventid"],
    "date": ["date", "event_date", "occurred_at", "timestamp"],
    "event_type": ["event_type", "type", "category"],
    "title": ["title", "name", "event_name", "headline"],
    "description": ["description", "details", "notes", "narrative"],
    "impact_area": ["impact_area", "impact", "metrics_impacted", "affected_metrics"],
    "severity": ["severity", "priority", "impact_level"],
    "segment": ["segment", "business_unit", "region"],
    "fiscal_year": ["fiscal_year", "fy"],
    "fiscal_quarter": ["fiscal_quarter", "quarter"],
    "fiscal_period": ["fiscal_period"],
}

ADDITIVE_KINDS = {"flow"}


def _norm(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum() or ch == "_").replace("__", "_")


def _rename_columns(df: pd.DataFrame, aliases: dict[str, list[str]]) -> pd.DataFrame:
    mapping: dict[str, str] = {}
    normalized = {_norm(col): col for col in df.columns}
    for canonical, options in aliases.items():
        for option in options:
            key = _norm(option)
            if key in normalized and canonical not in mapping.values():
                mapping[normalized[key]] = canonical
                break
    return df.rename(columns=mapping)


def _read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".json", ".jsonl"}:
        return pd.read_json(path, lines=suffix == ".jsonl")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported dataset format: {path}")


def _find_file(data_dir: Path, stem: str) -> Path:
    for suffix in (".csv", ".json", ".jsonl", ".xlsx", ".xls", ".parquet"):
        candidate = data_dir / f"{stem}{suffix}"
        if candidate.exists():
            return candidate
    matches = sorted(data_dir.glob(f"*{stem}*.csv"))
    if matches:
        return matches[0]
    raise FileNotFoundError(
        f"Could not find a {stem} dataset in {data_dir}. "
        "Place metrics.csv and events.csv there, or set FINAGENT_DATA_DIR."
    )


class DataStore:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else config.data_dir()
        self.metrics = self._load_metrics(_find_file(self.data_dir, "metrics"))
        self.events = self._load_events(_find_file(self.data_dir, "events"))

    def _load_metrics(self, path: Path) -> pd.DataFrame:
        df = _rename_columns(_read_table(path), METRIC_ALIASES)
        required = {"period", "metric_name", "metric_value"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")

        df["period"] = df["period"].map(period_label)
        df["period_date"] = pd.to_datetime(df["period"] + "-01")
        if "fiscal_year" not in df.columns:
            df["fiscal_year"] = df["period"].map(fiscal_year)
        if "fiscal_quarter" not in df.columns:
            df["fiscal_quarter"] = df["period"].map(fiscal_quarter)
        if "fiscal_period" not in df.columns:
            df["fiscal_period"] = df["period"].map(fiscal_label)
        if "segment" not in df.columns:
            df["segment"] = "Company"
        if "unit" not in df.columns:
            df["unit"] = ""
        if "metric_kind" not in df.columns:
            df["metric_kind"] = df["metric_name"].map(
                lambda name: "rate" if str(name).endswith("_pct") else "flow"
            )
        if "description" not in df.columns:
            df["description"] = ""

        df["fiscal_year"] = df["fiscal_year"].astype(int)
        df["fiscal_quarter"] = df["fiscal_quarter"].map(lambda q: normalize_quarter(str(q)))
        df["metric_name"] = df["metric_name"].astype(str)
        df["segment"] = df["segment"].fillna("Company").astype(str)
        df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")
        return df.sort_values(["period_date", "metric_name", "segment"]).reset_index(drop=True)

    def _load_events(self, path: Path) -> pd.DataFrame:
        df = _rename_columns(_read_table(path), EVENT_ALIASES)
        if "date" not in df.columns:
            raise ValueError(f"{path} is missing a date column")
        if "title" not in df.columns and "description" not in df.columns:
            raise ValueError(f"{path} needs a title or description column")

        df["date"] = df["date"].map(lambda v: parse_period(v).isoformat())
        df["date_parsed"] = pd.to_datetime(df["date"])
        if "fiscal_year" not in df.columns:
            df["fiscal_year"] = df["date"].map(fiscal_year)
        if "fiscal_quarter" not in df.columns:
            df["fiscal_quarter"] = df["date"].map(fiscal_quarter)
        if "fiscal_period" not in df.columns:
            df["fiscal_period"] = df["date"].map(fiscal_label)
        for column, default in {
            "event_id": "",
            "event_type": "other",
            "title": "",
            "description": "",
            "impact_area": "",
            "severity": "medium",
            "segment": "Company",
        }.items():
            if column not in df.columns:
                df[column] = default
            df[column] = df[column].fillna(default).astype(str)

        df["fiscal_year"] = df["fiscal_year"].astype(int)
        df["fiscal_quarter"] = df["fiscal_quarter"].map(lambda q: normalize_quarter(str(q)))
        return df.sort_values("date_parsed").reset_index(drop=True)

    def catalog(self) -> dict[str, Any]:
        metrics = (
            self.metrics.groupby("metric_name", as_index=False)
            .agg(
                unit=("unit", "first"),
                kind=("metric_kind", "first"),
                description=("description", "first"),
                segments=("segment", lambda s: sorted(set(s))),
            )
            .to_dict(orient="records")
        )
        return {
            "company": "AetherData (fictional)",
            "fiscal_calendar": "February–January; Q1 = Feb–Apr",
            "metrics_period_range": [
                self.metrics["period"].min(),
                self.metrics["period"].max(),
            ],
            "fiscal_years": sorted(self.metrics["fiscal_year"].unique().tolist()),
            "segments": sorted(self.metrics["segment"].unique().tolist()),
            "metric_count": int(self.metrics["metric_name"].nunique()),
            "metrics": metrics,
            "event_types": sorted(self.events["event_type"].unique().tolist()),
            "event_count": int(len(self.events)),
            "events_date_range": [
                self.events["date"].min(),
                self.events["date"].max(),
            ],
        }

    def query_metrics(
        self,
        metric: str | list[str] | None = None,
        fiscal_year: int | list[int] | None = None,
        fiscal_quarter: str | list[str] | None = None,
        start_period: str | None = None,
        end_period: str | None = None,
        segment: str | list[str] | None = None,
        aggregation: str = "monthly",
    ) -> pd.DataFrame:
        df = self.metrics.copy()
        if metric:
            names = [metric] if isinstance(metric, str) else list(metric)
            names = [self._resolve_metric(name) for name in names]
            df = df[df["metric_name"].isin(names)]
        if fiscal_year:
            years = [int(fiscal_year)] if isinstance(fiscal_year, (int, str)) else [int(y) for y in fiscal_year]
            df = df[df["fiscal_year"].isin(years)]
        if fiscal_quarter:
            quarters = (
                [normalize_quarter(fiscal_quarter)]
                if isinstance(fiscal_quarter, str)
                else [normalize_quarter(q) for q in fiscal_quarter]
            )
            df = df[df["fiscal_quarter"].isin(quarters)]
        if start_period:
            df = df[df["period"] >= period_label(start_period)]
        if end_period:
            df = df[df["period"] <= period_label(end_period)]
        if segment:
            segments = [segment] if isinstance(segment, str) else list(segment)
            df = df[df["segment"].isin(segments)]
        elif "segment" in df.columns:
            # Default to company-level so totals are not double-counted.
            if (df["segment"] == "Company").any():
                df = df[df["segment"] == "Company"]

        if df.empty:
            return df

        aggregation = (aggregation or "monthly").lower()
        if aggregation == "monthly":
            return df.sort_values(["period_date", "metric_name", "segment"]).reset_index(drop=True)
        if aggregation == "quarterly":
            return self._aggregate(df, ["fiscal_year", "fiscal_quarter", "fiscal_period", "metric_name", "segment"])
        if aggregation in {"annual", "yearly"}:
            return self._aggregate(df, ["fiscal_year", "metric_name", "segment"])
        raise ValueError("aggregation must be monthly, quarterly, or annual")

    def _aggregate(self, df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for (metric_name, kind), group in df.groupby(["metric_name", "metric_kind"], dropna=False):
            grouped = group.groupby(group_cols, as_index=False)
            if kind in ADDITIVE_KINDS:
                out = grouped.agg(
                    metric_value=("metric_value", "sum"),
                    unit=("unit", "first"),
                    metric_kind=("metric_kind", "first"),
                    description=("description", "first"),
                    period=("period", "max"),
                )
            else:
                # Rates and stock metrics: take the last month in the bucket.
                last_idx = group.sort_values("period_date").groupby(group_cols, as_index=False).tail(1)
                out = last_idx[group_cols + ["metric_value", "unit", "metric_kind", "description", "period"]]
            frames.append(out)
        result = pd.concat(frames, ignore_index=True)
        return result.sort_values(group_cols).reset_index(drop=True)

    def search_events(
        self,
        query: str | None = None,
        event_type: str | list[str] | None = None,
        fiscal_year: int | list[int] | None = None,
        fiscal_quarter: str | list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        impact_area: str | None = None,
        segment: str | None = None,
        limit: int = 20,
    ) -> pd.DataFrame:
        df = self.events.copy()
        if query:
            tokens = [tok.lower() for tok in str(query).replace(",", " ").split() if tok]
            blob = (
                df["title"].fillna("")
                + " "
                + df["description"].fillna("")
                + " "
                + df["event_type"].fillna("")
                + " "
                + df["impact_area"].fillna("")
            ).str.lower()
            for token in tokens:
                df = df[blob.str.contains(token, regex=False)]
                blob = blob.loc[df.index]
        if event_type:
            types = [event_type] if isinstance(event_type, str) else list(event_type)
            df = df[df["event_type"].isin(types)]
        if fiscal_year:
            years = [int(fiscal_year)] if isinstance(fiscal_year, (int, str)) else [int(y) for y in fiscal_year]
            df = df[df["fiscal_year"].isin(years)]
        if fiscal_quarter:
            quarters = (
                [normalize_quarter(fiscal_quarter)]
                if isinstance(fiscal_quarter, str)
                else [normalize_quarter(q) for q in fiscal_quarter]
            )
            df = df[df["fiscal_quarter"].isin(quarters)]
        if start_date:
            df = df[df["date"] >= parse_period(start_date).isoformat()]
        if end_date:
            df = df[df["date"] <= parse_period(end_date).isoformat()]
        if impact_area:
            df = df[df["impact_area"].str.contains(str(impact_area), case=False, regex=False)]
        if segment:
            df = df[df["segment"].str.contains(str(segment), case=False, regex=False)]
        return df.head(int(limit)).reset_index(drop=True)

    def _resolve_metric(self, name: str) -> str:
        available = sorted(self.metrics["metric_name"].unique())
        if name in available:
            return name
        compact = name.lower().replace(" ", "_")
        synonyms = {
            "revenue": "revenue_usd",
            "sales": "revenue_usd",
            "arr": "arr_usd",
            "annual_recurring_revenue": "arr_usd",
            "nrr": "nrr_pct",
            "net_revenue_retention": "nrr_pct",
            "gross_margin": "gross_margin_pct",
            "margin": "gross_margin_pct",
            "opex": "opex_usd",
            "operating_expenses": "opex_usd",
            "customers": "ending_customers",
            "customer_count": "ending_customers",
            "pipeline": "pipeline_usd",
            "win_rate": "win_rate_pct",
            "cac": "cac_usd",
            "churn": "churned_arr_usd",
            "churned_arr": "churned_arr_usd",
            "new_logo": "new_logo_acv_usd",
            "new_logos": "new_logo_acv_usd",
            "expansion": "expansion_acv_usd",
            "tickets": "support_tickets",
            "headcount": "headcount",
            "employees": "headcount",
        }
        if compact in synonyms and synonyms[compact] in available:
            return synonyms[compact]
        matches = [m for m in available if compact in m.lower()]
        if len(matches) == 1:
            return matches[0]
        raise ValueError(f"Unknown metric {name!r}. Available: {available}")
