"""Generate fictional AetherData business metrics and events.

The numbers are internally consistent so quarterly sums, ARR, and
event timing can be used to ground interview Q&A.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finagent.fiscal import fiscal_label, fiscal_quarter, fiscal_year, iter_months  # noqa: E402

# Quarterly company revenue in USD. Monthly rows split these totals.
REVENUE_BY_QUARTER: dict[tuple[int, str], int] = {
    (2024, "Q1"): 68_000_000,
    (2024, "Q2"): 72_000_000,
    (2024, "Q3"): 76_000_000,
    (2024, "Q4"): 84_000_000,
    (2025, "Q1"): 88_000_000,
    (2025, "Q2"): 102_000_000,  # AetherFlash 2.0 launch
    (2025, "Q3"): 94_000_000,  # regional outage
    (2025, "Q4"): 98_000_000,  # competitor price cut
    (2026, "Q1"): 118_000_000,  # partnership + list-price increase
    (2026, "Q2"): 112_000_000,  # CEO / sales realignment
    (2026, "Q3"): 108_000_000,  # supply constraint
    (2026, "Q4"): 136_000_000,  # AetherOne GA
}

# Ending ARR at quarter close.
ARR_BY_QUARTER: dict[tuple[int, str], int] = {
    (2024, "Q1"): 292_000_000,
    (2024, "Q2"): 308_000_000,
    (2024, "Q3"): 324_000_000,
    (2024, "Q4"): 346_000_000,
    (2025, "Q1"): 368_000_000,
    (2025, "Q2"): 412_000_000,
    (2025, "Q3"): 404_000_000,
    (2025, "Q4"): 418_000_000,
    (2026, "Q1"): 462_000_000,
    (2026, "Q2"): 455_000_000,
    (2026, "Q3"): 448_000_000,
    (2026, "Q4"): 512_000_000,
}

# End-of-quarter operating metrics (company-level).
KPI_BY_QUARTER: dict[str, dict[tuple[int, str], float]] = {
    "new_logo_acv_usd": {
        (2024, "Q1"): 18_000_000,
        (2024, "Q2"): 19_500_000,
        (2024, "Q3"): 21_000_000,
        (2024, "Q4"): 24_000_000,
        (2025, "Q1"): 26_000_000,
        (2025, "Q2"): 38_000_000,
        (2025, "Q3"): 22_000_000,
        (2025, "Q4"): 20_000_000,
        (2026, "Q1"): 36_000_000,
        (2026, "Q2"): 24_000_000,
        (2026, "Q3"): 21_000_000,
        (2026, "Q4"): 48_000_000,
    },
    "expansion_acv_usd": {
        (2024, "Q1"): 9_000_000,
        (2024, "Q2"): 9_800_000,
        (2024, "Q3"): 10_400_000,
        (2024, "Q4"): 12_200_000,
        (2025, "Q1"): 13_500_000,
        (2025, "Q2"): 16_000_000,
        (2025, "Q3"): 9_500_000,
        (2025, "Q4"): 11_000_000,
        (2026, "Q1"): 18_000_000,
        (2026, "Q2"): 12_500_000,
        (2026, "Q3"): 11_000_000,
        (2026, "Q4"): 22_000_000,
    },
    "churned_arr_usd": {
        (2024, "Q1"): 4_200_000,
        (2024, "Q2"): 4_400_000,
        (2024, "Q3"): 4_600_000,
        (2024, "Q4"): 5_000_000,
        (2025, "Q1"): 5_200_000,
        (2025, "Q2"): 5_400_000,
        (2025, "Q3"): 11_800_000,
        (2025, "Q4"): 8_600_000,
        (2026, "Q1"): 9_800_000,
        (2026, "Q2"): 8_200_000,
        (2026, "Q3"): 7_400_000,
        (2026, "Q4"): 5_500_000,
    },
    "nrr_pct": {
        (2024, "Q1"): 114.0,
        (2024, "Q2"): 115.0,
        (2024, "Q3"): 116.0,
        (2024, "Q4"): 117.0,
        (2025, "Q1"): 118.0,
        (2025, "Q2"): 121.0,
        (2025, "Q3"): 104.0,
        (2025, "Q4"): 108.0,
        (2026, "Q1"): 111.0,
        (2026, "Q2"): 109.0,
        (2026, "Q3"): 107.0,
        (2026, "Q4"): 119.0,
    },
    "gross_margin_pct": {
        (2024, "Q1"): 68.4,
        (2024, "Q2"): 68.8,
        (2024, "Q3"): 69.1,
        (2024, "Q4"): 69.5,
        (2025, "Q1"): 69.8,
        (2025, "Q2"): 70.6,
        (2025, "Q3"): 67.2,
        (2025, "Q4"): 68.0,
        (2026, "Q1"): 71.4,
        (2026, "Q2"): 70.8,
        (2026, "Q3"): 66.1,
        (2026, "Q4"): 72.2,
    },
    "opex_usd": {
        (2024, "Q1"): 41_000_000,
        (2024, "Q2"): 43_000_000,
        (2024, "Q3"): 44_500_000,
        (2024, "Q4"): 47_000_000,
        (2025, "Q1"): 49_000_000,
        (2025, "Q2"): 54_000_000,
        (2025, "Q3"): 56_500_000,
        (2025, "Q4"): 55_000_000,
        (2026, "Q1"): 58_000_000,
        (2026, "Q2"): 61_000_000,
        (2026, "Q3"): 59_500_000,
        (2026, "Q4"): 64_000_000,
    },
    "ending_customers": {
        (2024, "Q1"): 410,
        (2024, "Q2"): 428,
        (2024, "Q3"): 447,
        (2024, "Q4"): 469,
        (2025, "Q1"): 492,
        (2025, "Q2"): 538,
        (2025, "Q3"): 521,
        (2025, "Q4"): 529,
        (2026, "Q1"): 548,
        (2026, "Q2"): 541,
        (2026, "Q3"): 536,
        (2026, "Q4"): 587,
    },
    "pipeline_usd": {
        (2024, "Q1"): 210_000_000,
        (2024, "Q2"): 225_000_000,
        (2024, "Q3"): 240_000_000,
        (2024, "Q4"): 268_000_000,
        (2025, "Q1"): 280_000_000,
        (2025, "Q2"): 355_000_000,
        (2025, "Q3"): 310_000_000,
        (2025, "Q4"): 250_000_000,
        (2026, "Q1"): 340_000_000,
        (2026, "Q2"): 275_000_000,
        (2026, "Q3"): 260_000_000,
        (2026, "Q4"): 390_000_000,
    },
    "win_rate_pct": {
        (2024, "Q1"): 27.0,
        (2024, "Q2"): 27.5,
        (2024, "Q3"): 28.0,
        (2024, "Q4"): 29.0,
        (2025, "Q1"): 29.5,
        (2025, "Q2"): 33.0,
        (2025, "Q3"): 26.0,
        (2025, "Q4"): 19.5,
        (2026, "Q1"): 28.0,
        (2026, "Q2"): 24.0,
        (2026, "Q3"): 23.0,
        (2026, "Q4"): 32.5,
    },
    "cac_usd": {
        (2024, "Q1"): 42_000,
        (2024, "Q2"): 41_500,
        (2024, "Q3"): 41_000,
        (2024, "Q4"): 40_000,
        (2025, "Q1"): 39_500,
        (2025, "Q2"): 36_000,
        (2025, "Q3"): 44_000,
        (2025, "Q4"): 48_500,
        (2026, "Q1"): 40_000,
        (2026, "Q2"): 46_000,
        (2026, "Q3"): 47_500,
        (2026, "Q4"): 38_000,
    },
    "support_tickets": {
        (2024, "Q1"): 1_820,
        (2024, "Q2"): 1_760,
        (2024, "Q3"): 1_710,
        (2024, "Q4"): 1_690,
        (2025, "Q1"): 1_740,
        (2025, "Q2"): 1_980,
        (2025, "Q3"): 4_260,
        (2025, "Q4"): 2_410,
        (2026, "Q1"): 2_050,
        (2026, "Q2"): 2_180,
        (2026, "Q3"): 2_640,
        (2026, "Q4"): 2_220,
    },
    "headcount": {
        (2024, "Q1"): 620,
        (2024, "Q2"): 640,
        (2024, "Q3"): 655,
        (2024, "Q4"): 680,
        (2025, "Q1"): 705,
        (2025, "Q2"): 760,
        (2025, "Q3"): 780,
        (2025, "Q4"): 790,
        (2026, "Q1"): 810,
        (2026, "Q2"): 835,
        (2026, "Q3"): 848,
        (2026, "Q4"): 870,
    },
}

# Revenue mix by segment. Cloud share rises; Enterprise is hit by the FY25 Q4 competitor event.
SEGMENT_MIX = {
    (2024, "Q1"): {"Enterprise": 0.60, "Mid-Market": 0.27, "Cloud": 0.13},
    (2024, "Q2"): {"Enterprise": 0.59, "Mid-Market": 0.27, "Cloud": 0.14},
    (2024, "Q3"): {"Enterprise": 0.58, "Mid-Market": 0.27, "Cloud": 0.15},
    (2024, "Q4"): {"Enterprise": 0.57, "Mid-Market": 0.27, "Cloud": 0.16},
    (2025, "Q1"): {"Enterprise": 0.56, "Mid-Market": 0.27, "Cloud": 0.17},
    (2025, "Q2"): {"Enterprise": 0.55, "Mid-Market": 0.26, "Cloud": 0.19},
    (2025, "Q3"): {"Enterprise": 0.54, "Mid-Market": 0.26, "Cloud": 0.20},
    (2025, "Q4"): {"Enterprise": 0.48, "Mid-Market": 0.28, "Cloud": 0.24},
    (2026, "Q1"): {"Enterprise": 0.52, "Mid-Market": 0.25, "Cloud": 0.23},
    (2026, "Q2"): {"Enterprise": 0.51, "Mid-Market": 0.25, "Cloud": 0.24},
    (2026, "Q3"): {"Enterprise": 0.50, "Mid-Market": 0.25, "Cloud": 0.25},
    (2026, "Q4"): {"Enterprise": 0.53, "Mid-Market": 0.23, "Cloud": 0.24},
}

# Last month of a quarter is strongest (enterprise deal timing).
MONTHLY_WEIGHTS = (0.28, 0.30, 0.42)

METRIC_META = {
    "revenue_usd": {"unit": "USD", "kind": "flow", "description": "Recognized product and subscription revenue"},
    "arr_usd": {"unit": "USD", "kind": "stock", "description": "Ending annual recurring revenue"},
    "new_logo_acv_usd": {"unit": "USD", "kind": "flow", "description": "Annual contract value from new customers"},
    "expansion_acv_usd": {"unit": "USD", "kind": "flow", "description": "Upsell and cross-sell ACV from existing customers"},
    "churned_arr_usd": {"unit": "USD", "kind": "flow", "description": "ARR lost to logo churn and downsell"},
    "nrr_pct": {"unit": "percent", "kind": "rate", "description": "Net revenue retention"},
    "gross_margin_pct": {"unit": "percent", "kind": "rate", "description": "Gross margin"},
    "opex_usd": {"unit": "USD", "kind": "flow", "description": "Operating expenses"},
    "ending_customers": {"unit": "count", "kind": "stock", "description": "Ending customer count"},
    "pipeline_usd": {"unit": "USD", "kind": "stock", "description": "Qualified pipeline at period end"},
    "win_rate_pct": {"unit": "percent", "kind": "rate", "description": "Competitive win rate"},
    "cac_usd": {"unit": "USD", "kind": "rate", "description": "Customer acquisition cost"},
    "support_tickets": {"unit": "count", "kind": "flow", "description": "Opened support tickets"},
    "headcount": {"unit": "count", "kind": "stock", "description": "Ending employee headcount"},
}

EVENTS = [
    {
        "event_id": "EVT-001",
        "date": "2023-03-15",
        "event_type": "product_launch",
        "title": "AetherFlash generally available",
        "description": "First generally available release of the AetherFlash all-flash array, opening the mid-market motion.",
        "impact_area": "revenue,new_logo_acv_usd,pipeline_usd",
        "severity": "medium",
        "segment": "Mid-Market",
    },
    {
        "event_id": "EVT-002",
        "date": "2023-08-01",
        "event_type": "org_change",
        "title": "Opened EMEA headquarters in Dublin",
        "description": "Stood up EMEA sales, solutions engineering, and a small support pod to pursue multinational accounts.",
        "impact_area": "pipeline_usd,headcount,opex_usd",
        "severity": "low",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-003",
        "date": "2024-01-12",
        "event_type": "market",
        "title": "Growth financing closed",
        "description": "Closed a growth round used to expand enterprise sales capacity heading into FY2025.",
        "impact_area": "headcount,opex_usd,pipeline_usd",
        "severity": "medium",
        "segment": "Company",
    },
    {
        "event_id": "EVT-004",
        "date": "2024-03-20",
        "event_type": "org_change",
        "title": "Enterprise sales kickoff",
        "description": "Reoriented the FY2025 plan around 50 named enterprise accounts and a dedicated closer team.",
        "impact_area": "pipeline_usd,win_rate_pct,new_logo_acv_usd",
        "severity": "low",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-005",
        "date": "2024-06-12",
        "event_type": "product_launch",
        "title": "AetherFlash 2.0 launch",
        "description": "Shipped AetherFlash 2.0 with 2x density, native replication, and a consumption SKU. Largest demand-gen week in company history.",
        "impact_area": "revenue,arr_usd,new_logo_acv_usd,pipeline_usd,win_rate_pct",
        "severity": "high",
        "segment": "Company",
    },
    {
        "event_id": "EVT-006",
        "date": "2024-07-01",
        "event_type": "partnership",
        "title": "National channel partner program launched",
        "description": "Signed 12 regional VARs and introduced deal-registration incentives that expanded mid-market coverage.",
        "impact_area": "pipeline_usd,new_logo_acv_usd,cac_usd",
        "severity": "medium",
        "segment": "Mid-Market",
    },
    {
        "event_id": "EVT-007",
        "date": "2024-09-18",
        "event_type": "outage",
        "title": "US-East control-plane outage (14 hours)",
        "description": "A configuration error took the US-East management plane offline for 14 hours. Several enterprise customers invoked SLA credits and two logos churned.",
        "impact_area": "support_tickets,churned_arr_usd,nrr_pct,gross_margin_pct,revenue",
        "severity": "high",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-008",
        "date": "2024-10-02",
        "event_type": "outage",
        "title": "SLA credits and customer advisory issued",
        "description": "Issued service credits and a public advisory after the September outage. Support backlog remained elevated through October.",
        "impact_area": "support_tickets,gross_margin_pct,nrr_pct,churned_arr_usd",
        "severity": "medium",
        "segment": "Company",
    },
    {
        "event_id": "EVT-009",
        "date": "2024-11-15",
        "event_type": "competitor",
        "title": "NimbusBlock announced a 20% list-price cut",
        "description": "Primary competitor NimbusBlock cut list prices by 20% on comparable all-flash SKUs and started matching bake-off discounts.",
        "impact_area": "win_rate_pct,pipeline_usd,new_logo_acv_usd,revenue",
        "severity": "high",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-010",
        "date": "2024-12-05",
        "event_type": "competitor",
        "title": "Lost two late-stage enterprise bake-offs",
        "description": "Lost Northwind Logistics and Helios Health bake-offs to NimbusBlock on price. Pipeline coverage for Q4 slipped below 2x.",
        "impact_area": "win_rate_pct,pipeline_usd,new_logo_acv_usd",
        "severity": "high",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-011",
        "date": "2025-02-10",
        "event_type": "pricing_change",
        "title": "List prices increased 8%",
        "description": "Raised list prices 8% across AetherFlash SKUs. Enterprise deals were grandfathered for 90 days; SMB and some mid-market renewals saw sticker shock.",
        "impact_area": "revenue,gross_margin_pct,churned_arr_usd,nrr_pct",
        "severity": "high",
        "segment": "Company",
    },
    {
        "event_id": "EVT-012",
        "date": "2025-03-01",
        "event_type": "partnership",
        "title": "Northwind Cloud marketplace partnership",
        "description": "AetherFlash became a featured marketplace offering on Northwind Cloud, unlocking a new enterprise consumption motion.",
        "impact_area": "revenue,arr_usd,pipeline_usd,new_logo_acv_usd,win_rate_pct",
        "severity": "high",
        "segment": "Cloud",
    },
    {
        "event_id": "EVT-013",
        "date": "2025-04-18",
        "event_type": "pricing_change",
        "title": "SMB churn after price increase",
        "description": "A cluster of SMB customers declined renewal after the February price increase. Logo churn was concentrated below $80k ACV.",
        "impact_area": "churned_arr_usd,ending_customers,nrr_pct",
        "severity": "medium",
        "segment": "Mid-Market",
    },
    {
        "event_id": "EVT-014",
        "date": "2025-05-22",
        "event_type": "org_change",
        "title": "CEO transition announced",
        "description": "Founder-CEO announced a planned transition. Incoming CEO Mira Chen named, effective July 1. Some late-stage buyers paused.",
        "impact_area": "pipeline_usd,win_rate_pct,headcount",
        "severity": "medium",
        "segment": "Company",
    },
    {
        "event_id": "EVT-015",
        "date": "2025-06-15",
        "event_type": "org_change",
        "title": "Sales territory realignment",
        "description": "New CEO realigned territories and quota. Coverage gaps in the Central region delayed several FY26 Q2 close plans.",
        "impact_area": "pipeline_usd,win_rate_pct,new_logo_acv_usd,revenue",
        "severity": "high",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-016",
        "date": "2025-08-28",
        "event_type": "supply",
        "title": "NAND supply constraint",
        "description": "A key NAND supplier missed deliveries. Lead times stretched from 3 weeks to 11 weeks and several Q3 shipments slipped.",
        "impact_area": "revenue,gross_margin_pct,pipeline_usd,support_tickets",
        "severity": "high",
        "segment": "Company",
    },
    {
        "event_id": "EVT-017",
        "date": "2025-09-10",
        "event_type": "supply",
        "title": "AetherOne shipments delayed",
        "description": "First AetherOne customer shipments delayed into Q4 because of the NAND constraint. A few customers accepted AetherFlash 2.0 as a bridge.",
        "impact_area": "revenue,arr_usd,win_rate_pct,support_tickets",
        "severity": "high",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-018",
        "date": "2025-11-05",
        "event_type": "product_launch",
        "title": "AetherOne generally available",
        "description": "Launched AetherOne, a disaggregated high-density platform aimed at AI/analytics estates. Early attach was strongest in Enterprise and Cloud.",
        "impact_area": "revenue,arr_usd,new_logo_acv_usd,expansion_acv_usd,pipeline_usd,win_rate_pct",
        "severity": "high",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-019",
        "date": "2025-12-12",
        "event_type": "market",
        "title": "Record year-end enterprise close",
        "description": "Closed four eight-figure AetherOne deals in the second week of December as supply recovered and year-end budgets landed.",
        "impact_area": "revenue,arr_usd,new_logo_acv_usd,win_rate_pct",
        "severity": "high",
        "segment": "Enterprise",
    },
    {
        "event_id": "EVT-020",
        "date": "2026-01-20",
        "event_type": "market",
        "title": "FedRAMP Moderate authorization",
        "description": "Received FedRAMP Moderate authorization, opening a civilian-agency pipeline for FY2027.",
        "impact_area": "pipeline_usd,new_logo_acv_usd",
        "severity": "medium",
        "segment": "Enterprise",
    },
]


def _split_quarter(total: float, kind: str) -> list[float]:
    if kind == "flow":
        return [round(total * w, 2) for w in MONTHLY_WEIGHTS]
    # stock / rate: hold the quarter-end value across the quarter
    return [float(total), float(total), float(total)]


def _quarter_key(period: str) -> tuple[int, str]:
    return fiscal_year(period), fiscal_quarter(period)


def build_metrics() -> pd.DataFrame:
    months = iter_months("2023-02", "2026-01")
    rows: list[dict] = []

    for month in months:
        key = _quarter_key(month)
        q_months = [
            m
            for m in months
            if (fiscal_year(m), fiscal_quarter(m)) == key
        ]
        idx = q_months.index(month)

        company_revenue = _split_quarter(REVENUE_BY_QUARTER[key], "flow")[idx]
        company_arr = ARR_BY_QUARTER[key]
        mix = SEGMENT_MIX[key]

        def add_row(metric: str, value: float, segment: str) -> None:
            meta = METRIC_META[metric]
            rows.append(
                {
                    "period": month,
                    "fiscal_year": fiscal_year(month),
                    "fiscal_quarter": fiscal_quarter(month),
                    "fiscal_period": fiscal_label(month),
                    "segment": segment,
                    "metric_name": metric,
                    "metric_value": value,
                    "unit": meta["unit"],
                    "metric_kind": meta["kind"],
                    "description": meta["description"],
                }
            )

        add_row("revenue_usd", company_revenue, "Company")
        add_row("arr_usd", company_arr, "Company")

        for segment, share in mix.items():
            add_row("revenue_usd", round(company_revenue * share, 2), segment)
            add_row("arr_usd", round(company_arr * share, 2), segment)

        for metric, series in KPI_BY_QUARTER.items():
            kind = METRIC_META[metric]["kind"]
            value = _split_quarter(series[key], kind)[idx]
            add_row(metric, value, "Company")

    return pd.DataFrame(rows)


def build_events() -> pd.DataFrame:
    rows = []
    for event in EVENTS:
        rows.append(
            {
                **event,
                "fiscal_year": fiscal_year(event["date"]),
                "fiscal_quarter": fiscal_quarter(event["date"]),
                "fiscal_period": fiscal_label(event["date"]),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    metrics = build_metrics()
    events = build_events()
    metrics.to_csv(out_dir / "metrics.csv", index=False)
    events.to_csv(out_dir / "events.csv", index=False)
    print(f"Wrote {len(metrics)} metric rows and {len(events)} events to {out_dir}")


if __name__ == "__main__":
    main()
