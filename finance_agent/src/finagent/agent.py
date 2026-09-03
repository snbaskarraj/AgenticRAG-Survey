"""Tool-calling finance agent with OpenAI, Anthropic, and offline backends."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from . import config
from .fallback import OfflinePlanner
from .prompts import SYSTEM_PROMPT
from .store import DataStore
from .tools import TOOL_SCHEMAS, ToolBox, dump_tool_result


@dataclass
class AgentResponse:
    answer: str
    traces: list[dict[str, Any]] = field(default_factory=list)
    provider: str = "offline"
    model: str | None = None


class FinanceAgent:
    def __init__(self, store: DataStore | None = None) -> None:
        self.store = store or DataStore()
        self.tools = ToolBox(self.store)
        self.provider = config.active_provider()

    def ask(self, question: str, history: list[dict[str, str]] | None = None) -> AgentResponse:
        history = history or []
        if self.provider == "offline":
            answer, traces = OfflinePlanner(self.tools).run(question)
            return AgentResponse(answer=answer, traces=traces, provider="offline", model="deterministic-planner")
        if self.provider == "openai":
            return self._ask_openai(question, history)
        if self.provider == "anthropic":
            return self._ask_anthropic(question, history)
        raise RuntimeError(f"Unsupported provider: {self.provider}")

    def _ask_openai(self, question: str, history: list[dict[str, str]]) -> AgentResponse:
        from openai import OpenAI

        client_kwargs: dict[str, Any] = {"api_key": config.openai_api_key()}
        if config.openai_base_url():
            client_kwargs["base_url"] = config.openai_base_url()
        client = OpenAI(**client_kwargs)
        model = config.openai_model()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": schema["name"],
                    "description": schema["description"],
                    "parameters": schema["parameters"],
                },
            }
            for schema in TOOL_SCHEMAS
        ]
        messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turn in history[-8:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": question})

        traces: list[dict[str, Any]] = []
        final_text = ""
        for _ in range(config.max_tool_rounds()):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0,
            )
            choice = response.choices[0]
            message = choice.message
            if message.tool_calls:
                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {
                                    "name": call.function.name,
                                    "arguments": call.function.arguments,
                                },
                            }
                            for call in message.tool_calls
                        ],
                    }
                )
                for call in message.tool_calls:
                    arguments = _parse_json(call.function.arguments)
                    result = self.tools.execute(call.function.name, arguments)
                    traces.append(
                        {"tool": call.function.name, "arguments": arguments, "result": result}
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": dump_tool_result(result),
                        }
                    )
                continue
            final_text = (message.content or "").strip()
            break
        if not final_text:
            final_text = "The model used its tool budget without returning a final answer."
        return AgentResponse(answer=final_text, traces=traces, provider="openai", model=model)

    def _ask_anthropic(self, question: str, history: list[dict[str, str]]) -> AgentResponse:
        from anthropic import Anthropic

        client = Anthropic(api_key=config.anthropic_api_key())
        model = config.anthropic_model()
        tools = [
            {
                "name": schema["name"],
                "description": schema["description"],
                "input_schema": schema["parameters"],
            }
            for schema in TOOL_SCHEMAS
        ]
        messages: list[dict[str, Any]] = []
        for turn in history[-8:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": question})

        traces: list[dict[str, Any]] = []
        final_text = ""
        for _ in range(config.max_tool_rounds()):
            response = client.messages.create(
                model=model,
                system=SYSTEM_PROMPT,
                messages=messages,
                tools=tools,
                max_tokens=1600,
                temperature=0,
            )
            tool_uses = [block for block in response.content if block.type == "tool_use"]
            text_blocks = [block.text for block in response.content if block.type == "text"]
            if tool_uses:
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in tool_uses:
                    arguments = dict(block.input or {})
                    result = self.tools.execute(block.name, arguments)
                    traces.append({"tool": block.name, "arguments": arguments, "result": result})
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": dump_tool_result(result),
                        }
                    )
                messages.append({"role": "user", "content": tool_results})
                continue
            final_text = "\n".join(text_blocks).strip()
            break
        if not final_text:
            final_text = "The model used its tool budget without returning a final answer."
        return AgentResponse(answer=final_text, traces=traces, provider="anthropic", model=model)


def _parse_json(payload: str | None) -> dict[str, Any]:
    if not payload:
        return {}
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
