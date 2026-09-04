from pathlib import Path

import pandas as pd

from finagent.datasets import activate_files, activate_folder, activate_synthetic, resolve_datasets
from finagent.store import DataStore


def _copy_synthetic(dest: Path) -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[1] / "data"
    metrics = dest / "company_kpis.csv"
    events = dest / "business_events.csv"
    metrics.write_bytes((root / "metrics.csv").read_bytes())
    events.write_bytes((root / "events.csv").read_bytes())
    return metrics, events


def test_synthetic_default_stays_intact():
    store = DataStore()
    assert store.source == "synthetic"
    rows = store.query_metrics(metric="revenue", fiscal_year=2026, fiscal_quarter="Q1", aggregation="quarterly")
    assert rows.iloc[0]["metric_value"] == 118_000_000


def test_load_renamed_files_from_interview_folder(tmp_path):
    _copy_synthetic(tmp_path)
    store = DataStore(data_dir=tmp_path)
    assert store.source == "folder"
    rows = store.query_metrics(metric="revenue", fiscal_year=2026, fiscal_quarter="Q1", aggregation="quarterly")
    assert rows.iloc[0]["metric_value"] == 118_000_000


def test_explicit_paths(tmp_path):
    metrics, events = _copy_synthetic(tmp_path)
    store = DataStore(metrics_path=metrics, events_path=events)
    assert store.source == "explicit"
    assert DataStore().source == "synthetic"


def test_wide_metrics_are_melted(tmp_path):
    wide = pd.DataFrame(
        {
            "period": ["2025-02", "2025-03", "2025-04"],
            "revenue_usd": [30_000_000, 40_000_000, 48_000_000],
            "arr_usd": [400_000_000, 410_000_000, 420_000_000],
        }
    )
    metrics = tmp_path / "metrics.csv"
    events = tmp_path / "events.csv"
    wide.to_csv(metrics, index=False)
    pd.DataFrame(
        {
            "date": ["2025-02-10"],
            "title": "Price increase",
            "description": "List prices up 8%.",
            "event_type": "pricing_change",
        }
    ).to_csv(events, index=False)
    store = DataStore(metrics_path=metrics, events_path=events)
    rows = store.query_metrics(metric="revenue", fiscal_year=2026, fiscal_quarter="Q1", aggregation="quarterly")
    assert rows.iloc[0]["metric_value"] == 118_000_000


def test_activate_folder_and_restore(tmp_path, monkeypatch):
    _copy_synthetic(tmp_path)
    monkeypatch.setattr("finagent.datasets.active_state_path", lambda: tmp_path / "active.json")
    ref = activate_folder(tmp_path)
    assert ref.source == "interview_folder"
    assert resolve_datasets().folder == tmp_path.resolve()
    restored = activate_synthetic()
    assert restored.source == "synthetic"
