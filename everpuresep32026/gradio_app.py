"""Gradio chat UI for the same grounded finance agent used by Streamlit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finagent.agent import FinanceAgent
from finagent.config import active_provider
from finagent.samples import SAMPLE_QUESTIONS
from finagent.store import DataStore

store = DataStore()
agent = FinanceAgent(store)
catalog = store.catalog()


def _history_for_agent(history: list) -> list[dict[str, str]]:
    turns: list[dict[str, str]] = []
    for item in history or []:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and content:
                turns.append({"role": role, "content": str(content)})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            user, assistant = item
            if user:
                turns.append({"role": "user", "content": str(user)})
            if assistant:
                turns.append({"role": "assistant", "content": str(assistant)})
    return turns


def reply(message: str, history: list):
    response = agent.ask(message, history=_history_for_agent(history))
    traces = json.dumps(response.traces, indent=2, default=str)
    meta = (
        f"provider={response.provider} · model={response.model} · "
        f"tools={len(response.traces)} · grounded={response.requirement_check()['used_data_tool']}"
    )
    return response.answer, traces, meta


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="AetherData Finance Agent") as demo:
        gr.Markdown(
            f"""
# AetherData finance analyst
Everpure hands-on agentic exercise. Same backend as the Streamlit app.

**Requirements covered:** chat UI · LLM-capable backend (`{active_provider()}`) ·
tool access to metrics/events · answers grounded in the CSVs.

Fiscal calendar: {catalog["fiscal_calendar"]}.
            """
        )
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="Chat", height=460)
                question = gr.Textbox(
                    label="Ask about the supplied datasets",
                    placeholder="What was the revenue in Q1 FY2026?",
                    submit_btn="Ask",
                )
                gr.Examples(examples=[[q] for q in SAMPLE_QUESTIONS], inputs=question)
            with gr.Column(scale=2):
                status = gr.Textbox(label="Grounding status", interactive=False)
                traces = gr.Code(label="Tool traces", language="json")

        def on_ask(message, history):
            if not message or not str(message).strip():
                return history, "", "Ask a question first."
            answer, trace_json, meta = reply(message, history)
            history = list(history or [])
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": answer})
            return history, trace_json, meta

        question.submit(on_ask, [question, chatbot], [chatbot, traces, status]).then(
            lambda: "", None, question
        )
    return demo


if __name__ == "__main__":
    build_demo().launch(server_name="0.0.0.0", server_port=7860, show_error=True)
