"""Resolve which two datasets the agent should use.

Synthetic files in data/metrics.csv and data/events.csv stay untouched.
Interview-day files are pointed at, copied into data/uploads/, or dropped
into data/interview/. The active choice is stored in data/active.json.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from . import config

TABLE_SUFFIXES = {".csv", ".json", ".jsonl", ".xlsx", ".xls", ".parquet"}
METRIC_HINTS = ("metric", "kpi", "measure", "financial", "fact", "numbers")
EVENT_HINTS = ("event", "incident", "news", "timeline", "narrative")


@dataclass(frozen=True)
class DatasetRef:
    source: str
    metrics_path: Path
    events_path: Path
    folder: Path | None = None

    def fingerprint(self) -> str:
        parts = [self.source, str(self.metrics_path), str(self.events_path)]
        for path in (self.metrics_path, self.events_path):
            if path.exists():
                stat = path.stat()
                parts.append(f"{stat.st_mtime_ns}:{stat.st_size}")
        return "|".join(parts)

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "metrics_path": str(self.metrics_path),
            "events_path": str(self.events_path),
            "folder": str(self.folder) if self.folder else "",
        }


def active_state_path() -> Path:
    return config.data_dir() / "active.json"


def interview_dir() -> Path:
    path = config.interview_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def upload_dir() -> Path:
    path = config.upload_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def synthetic_ref() -> DatasetRef:
    root = config.data_dir()
    return DatasetRef(
        source="synthetic",
        metrics_path=_find_named(root, "metrics"),
        events_path=_find_named(root, "events"),
        folder=root,
    )


def resolve_datasets(
    data_dir: str | Path | None = None,
    metrics_path: str | Path | None = None,
    events_path: str | Path | None = None,
) -> DatasetRef:
    if metrics_path and events_path:
        return DatasetRef("explicit", Path(metrics_path), Path(events_path))
    if data_dir:
        return _from_folder(Path(data_dir), source="folder")

    env_metrics = config.metrics_path_override()
    env_events = config.events_path_override()
    if env_metrics and env_events:
        return DatasetRef("env_files", Path(env_metrics), Path(env_events))

    env_dir = config.data_dir_override()
    if env_dir:
        return _from_folder(Path(env_dir), source="env_folder")

    state = _read_state()
    mode = (state.get("mode") or "synthetic").lower()
    if mode == "folder" and state.get("folder"):
        return _from_folder(Path(state["folder"]), source="interview_folder")
    if mode == "files" and state.get("metrics_path") and state.get("events_path"):
        return DatasetRef(
            "upload",
            Path(state["metrics_path"]),
            Path(state["events_path"]),
        )

    dropped = _maybe_interview_drop()
    if dropped:
        return dropped
    return synthetic_ref()


def activate_synthetic() -> DatasetRef:
    _write_state({"mode": "synthetic"})
    return synthetic_ref()


def activate_folder(folder: str | Path) -> DatasetRef:
    ref = _from_folder(Path(folder), source="interview_folder")
    _write_state({"mode": "folder", "folder": str(Path(folder).expanduser().resolve())})
    return ref


def activate_files(metrics_src: str | Path, events_src: str | Path) -> DatasetRef:
    dest = upload_dir()
    metrics_path = _copy_as(metrics_src, dest, "metrics")
    events_path = _copy_as(events_src, dest, "events")
    _write_state(
        {
            "mode": "files",
            "metrics_path": str(metrics_path),
            "events_path": str(events_path),
        }
    )
    return DatasetRef("upload", metrics_path, events_path, dest)


def list_table_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in TABLE_SUFFIXES]
    return sorted(files)


def _maybe_interview_drop() -> DatasetRef | None:
    folder = interview_dir()
    files = list_table_files(folder)
    if len(files) < 2:
        return None
    try:
        return _from_folder(folder, source="interview_folder")
    except FileNotFoundError:
        return None


def _from_folder(folder: Path, source: str) -> DatasetRef:
    folder = folder.expanduser().resolve()
    if not folder.exists():
        raise FileNotFoundError(f"Dataset folder not found: {folder}")
    metrics = _guess_file(folder, "metrics", METRIC_HINTS)
    events = _guess_file(folder, "events", EVENT_HINTS)
    if metrics == events:
        raise FileNotFoundError(
            f"{folder} does not contain two distinct metrics and events files."
        )
    return DatasetRef(source, metrics, events, folder)


def _find_named(folder: Path, stem: str) -> Path:
    for suffix in TABLE_SUFFIXES:
        candidate = folder / f"{stem}{suffix}"
        if candidate.exists():
            return candidate
    matches = sorted(folder.glob(f"*{stem}*.csv"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"Could not find a {stem} file in {folder}")


def _guess_file(folder: Path, stem: str, hints: tuple[str, ...]) -> Path:
    try:
        return _find_named(folder, stem)
    except FileNotFoundError:
        pass
    files = list_table_files(folder)
    hinted = [p for p in files if any(h in p.stem.lower() for h in hints)]
    if len(hinted) == 1:
        return hinted[0]
    if len(files) == 2:
        other_hints = EVENT_HINTS if stem == "metrics" else METRIC_HINTS
        leftover = [p for p in files if not any(h in p.stem.lower() for h in other_hints)]
        if len(leftover) == 1:
            return leftover[0]
        return files[0] if stem == "metrics" else files[1]
    names = [p.name for p in files] or ["<empty>"]
    raise FileNotFoundError(
        f"Could not identify a {stem} file in {folder}. Found: {names}. "
        "Name the files with 'metrics' and 'events', or upload them in the UI."
    )


def _copy_as(src: str | Path, dest_dir: Path, stem: str) -> Path:
    src_path = Path(src).expanduser().resolve()
    if not src_path.exists():
        raise FileNotFoundError(f"Upload source not found: {src_path}")
    dest = dest_dir / f"{stem}{src_path.suffix.lower() or '.csv'}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dest)
    return dest


def _read_state() -> dict:
    path = active_state_path()
    if not path.exists():
        return {"mode": "synthetic"}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"mode": "synthetic"}


def _write_state(payload: dict) -> None:
    path = active_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))
