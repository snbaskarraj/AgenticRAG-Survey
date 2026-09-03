"""Pydantic contracts used by the agent and UIs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolTrace(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)


class ChatTurn(BaseModel):
    role: str
    content: str


class AgentResponse(BaseModel):
    """Structured agent output so both Streamlit and Gradio stay consistent."""

    answer: str
    traces: list[dict[str, Any]] = Field(default_factory=list)
    provider: str = "offline"
    model: str | None = None

    def requirement_check(self) -> dict[str, bool]:
        return {
            "has_answer": bool(self.answer.strip()),
            "used_data_tool": any(
                (trace.get("tool") if isinstance(trace, dict) else None)
                in {
                    "query_metrics",
                    "analyze_trend",
                    "detect_anomalies",
                    "search_events",
                    "explain_change",
                    "list_catalog",
                }
                for trace in self.traces
            ),
        }
