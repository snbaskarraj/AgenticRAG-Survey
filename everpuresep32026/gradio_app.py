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
from finagent.datasets import activate_files, activate_folder, activate_synthetic
from finagent.samples import SAMPLE_QUESTIONS
from finagent.store import DataStore


class Runtime:
    def __init__(self) -> None:
        self.reload()

    def reload(self) -> None:
        self.store = DataStore()
        self.agent = FinanceAgent(self.store)

    def status_line(self) -> str:
        catalog = self.store.catalog()
        return (
            f"source={catalog.get('source')} · provider={active_provider()} · "
            f"metrics={Path(catalog['metrics_path']).name} · "
            f"events={Path(catalog['events_path']).name} · "
            f"{catalog['metric_count']} metrics / {catalog['event_count']} events"
        )


rt = Runtime()


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
    response = rt.agent.ask(message, history=_history_for_agent(history))
    traces = json.dumps(response.traces, indent=2, default=str)
    meta = (
        f"{rt.status_line()} · tools={len(response.traces)} · "
        f"grounded={response.requirement_check()['used_data_tool']}"
    )
    return response.answer, traces, meta


def _load_folder(folder: str):
    if not folder or not str(folder).strip():
        return rt.status_line(), "Enter the folder path they give you."
    try:
        activate_folder(folder)
        rt.reload()
        return rt.status_line(), f"Loaded datasets from {folder}. Synthetic files were not changed."
    except Exception as exc:
        return rt.status_line(), str(exc)


def _file_path(file_obj):
    if file_obj is None:
        return None
    if isinstance(file_obj, (str, Path)):
        return file_obj
    return getattr(file_obj, "name", None) or str(file_obj)


def _load_uploads(metrics_file, events_file):
    metrics_file = _file_path(metrics_file)
    events_file = _file_path(events_file)
    if metrics_file is None or events_file is None:
        return rt.status_line(), "Upload both a metrics file and an events file."
    try:
        activate_files(metrics_file, events_file)
        rt.reload()
        return rt.status_line(), "Interview files loaded. Synthetic CSVs were not overwritten."
    except Exception as exc:
        return rt.status_line(), str(exc)


def _restore_synthetic():
    activate_synthetic()
    rt.reload()
    return rt.status_line(), "Restored built-in synthetic metrics and events."


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="AetherData Finance Agent") as demo:
        gr.Markdown(
            """
# AetherData finance analyst
Same backend as the Streamlit app. Synthetic data is the default.
On interview day, load the two files they give you — do not replace the code.
            """
        )
        source = gr.Textbox(label="Active dataset", value=rt.status_line(), interactive=False)
        notice = gr.Textbox(label="Load status", interactive=False)
        with gr.Row():
            folder = gr.Textbox(label="Interview folder path", placeholder="/path/they/give/you")
            use_folder = gr.Button("Use this folder")
        with gr.Row():
            metrics_file = gr.File(label="Upload metrics file")
            events_file = gr.File(label="Upload events file")
            load_uploads = gr.Button("Load uploaded files")
        restore = gr.Button("Restore synthetic data")

        use_folder.click(_load_folder, folder, [source, notice])
        load_uploads.click(_load_uploads, [metrics_file, events_file], [source, notice])
        restore.click(_restore_synthetic, None, [source, notice])

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="Chat", height=420)
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
