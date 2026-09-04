from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PACKAGE_ROOT / "data"


def data_dir() -> Path:
    return DEFAULT_DATA_DIR


def data_dir_override() -> Path | None:
    value = os.getenv("FINAGENT_DATA_DIR")
    return Path(value) if value else None


def metrics_path_override() -> Path | None:
    value = os.getenv("FINAGENT_METRICS_PATH")
    return Path(value) if value else None


def events_path_override() -> Path | None:
    value = os.getenv("FINAGENT_EVENTS_PATH")
    return Path(value) if value else None


def interview_dir() -> Path:
    override = os.getenv("FINAGENT_INTERVIEW_DIR")
    return Path(override) if override else DEFAULT_DATA_DIR / "interview"


def upload_dir() -> Path:
    override = os.getenv("FINAGENT_UPLOAD_DIR")
    return Path(override) if override else DEFAULT_DATA_DIR / "uploads"


def max_tool_rounds() -> int:
    return int(os.getenv("FINAGENT_MAX_TOOL_ROUNDS", "6"))


def openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY") or None


def openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def openai_base_url() -> str | None:
    return os.getenv("OPENAI_BASE_URL") or None


def anthropic_api_key() -> str | None:
    return os.getenv("ANTHROPIC_API_KEY") or None


def anthropic_model() -> str:
    return os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")


def active_provider() -> str:
    if openai_api_key():
        return "openai"
    if anthropic_api_key():
        return "anthropic"
    return "offline"
