"""Build the downloadable Colab notebook. python3 notebooks/_build_colab_upload.py"""

from __future__ import annotations

import json
from pathlib import Path

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        "colab": {
            "provenance": [],
            "toc_visible": True,
            "name": "Everpure_Colab_Upload.ipynb",
        },
    },
    "cells": [],
}


def md(source: str) -> None:
    nb["cells"].append(
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in source.strip("\n").split("\n")],
        }
    )


def code(source: str) -> None:
    nb["cells"].append(
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": [line + "\n" for line in source.strip("\n").split("\n")],
        }
    )


md(
    """# Everpure Agentic Finance Analyst — Google Colab

**Upload this `.ipynb` to Google Colab** → Runtime → **Run all**.

This is the same project as Cursor (`everpuresep32026`):

| Requirement | In this notebook |
| --- | --- |
| Simple chat UI | Gradio (embeds in Colab) |
| LLM-powered backend | OpenAI/Anthropic tool calling if a key is set |
| Query / analyze data | `query_metrics`, `analyze_trend`, `detect_anomalies`, `search_events`, `explain_change` |
| Grounded answers | Tools compute every number from the two CSVs |

Synthetic `metrics.csv` + `events.csv` load first. On interview day, upload the two files they give you in the cell marked **Interview-day files** — the synthetic CSVs are not overwritten.

Cursor still uses Streamlit (`./run.sh`). Colab uses Gradio because it embeds cleanly.
"""
)

md(
    """## How to use this file

1. Download `Everpure_Colab_Upload.ipynb`
2. [colab.research.google.com](https://colab.research.google.com) → **Upload notebook**
3. Runtime → **Run all**
4. Scroll to the Gradio cell and ask: *What was the revenue in Q1 FY2026?*
5. Expected synthetic answer: **$118.0M**
"""
)

md("## 1. Install packages")

code(
    """
import sys, subprocess
print(sys.version)

subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-q",
    "pandas", "numpy", "pydantic", "python-dotenv",
    "openai", "anthropic", "gradio", "pytest", "openpyxl",
])
print("Packages installed.")
"""
)

md("## 2. Get the project (clone if this notebook was uploaded alone)")

code(
    """
import os, sys, shutil, subprocess
from pathlib import Path

IN_COLAB = Path("/content").exists()
print("Google Colab:", IN_COLAB)

REPO_URL = "https://github.com/snbaskarraj/AgenticRAG-Survey.git"

def find_project() -> Path:
    here = Path.cwd().resolve()
    candidates = [
        here,
        here / "everpuresep32026",
        here.parent,
        Path("/content/AgenticRAG-Survey/everpuresep32026"),
        Path("/workspace/everpuresep32026"),
    ]
    for path in candidates:
        if (path / "src" / "finagent" / "agent.py").exists():
            return path
    if IN_COLAB:
        repo = Path("/content/AgenticRAG-Survey")
        if repo.exists():
            shutil.rmtree(repo)
        subprocess.check_call(["git", "clone", "--depth", "1", REPO_URL, str(repo)])
        return repo / "everpuresep32026"
    raise FileNotFoundError(
        "Could not find everpuresep32026. Upload this notebook to Colab "
        "and rerun so it can clone the repo."
    )

ROOT = find_project()
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))
print("Project root:", ROOT)
print("Synthetic metrics:", (ROOT / "data" / "metrics.csv").exists())
print("Synthetic events:", (ROOT / "data" / "events.csv").exists())
"""
)

md("## 3. SDLC and design (what we will discuss)")

code(
    """
from IPython.display import HTML, display

def mermaid(graph: str):
    display(HTML(f'''
    <div class="mermaid">{graph.strip()}</div>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
      mermaid.initialize({{startOnLoad:true, theme:"neutral"}});
      mermaid.run();
    </script>
    '''))

mermaid('''
flowchart LR
    A[1 Requirements] --> B[2 Design]
    B --> C[3 Implement]
    C --> D[4 Validate]
    D --> E[5 Demo]
''')
"""
)

code(
    """
mermaid('''
flowchart TD
    U[User question] --> UI[Chat UI<br/>Gradio in Colab / Streamlit in Cursor]
    UI --> A[FinanceAgent]
    A -->|API key| L[OpenAI / Anthropic function calling]
    A -->|no key| P[Offline planner<br/>same tools]
    L --> T[ToolBox]
    P --> T
    T --> Q[query_metrics]
    T --> TR[analyze_trend]
    T --> AN[detect_anomalies]
    T --> EV[search_events / explain_change]
    Q --> D[(metrics + events CSVs)]
    TR --> D
    AN --> D
    EV --> D
    T --> ANS[Grounded answer + traces]
''')
"""
)

md(
    """**Design decisions**

1. The LLM never sees the raw CSVs. It must call tools. That is grounding.
2. Synthetic files stay on disk. Interview files are pointed at or copied to `data/uploads/`.
3. Company is the default segment so Enterprise + Cloud are not double-counted.
4. Flow metrics sum; stock/rate metrics take the last month.
5. Anomalies use a robust z-score. Events are correlated, not called causal.
6. Streamlit in Cursor, Gradio here — same `FinanceAgent.ask()`.
"""
)

md("## 4. Load synthetic data and prove a grounded answer")

code(
    """
from finagent.store import DataStore
from finagent.tools import ToolBox
from finagent.agent import FinanceAgent
from finagent.config import active_provider
from finagent.datasets import activate_files, activate_synthetic, resolve_datasets

activate_synthetic()
store = DataStore()
tools = ToolBox(store)
agent = FinanceAgent(store)
catalog = store.catalog()

print("Source:", catalog["source"])
print("Provider:", active_provider())
print("Fiscal calendar:", catalog["fiscal_calendar"])
print("Period range:", catalog["metrics_period_range"])
print("Metrics:", [m["metric_name"] for m in catalog["metrics"]])
print("Events:", catalog["event_count"], catalog["event_types"])
store.metrics.head()
"""
)

code(
    """
print("=== R3 tool: query_metrics ===")
point = tools.query_metrics(metric="revenue", fiscal_year=2026, fiscal_quarter="Q1", aggregation="quarterly")
print(point)

print("\\n=== Agent answer (must be grounded) ===")
response = agent.ask("What was the revenue in Q1 FY2026?")
print(response.answer)
print("requirement check:", response.requirement_check())
assert "118" in response.answer
print("Acceptance test passed: $118.0M from synthetic metrics.csv")
"""
)

code(
    """
print("=== Trend ===")
trend = tools.analyze_trend("arr", aggregation="quarterly", periods=8)
print({k: trend[k] for k in ("direction", "total_change_pct", "latest")})

print("\\n=== Anomalies ===")
anoms = tools.detect_anomalies(aggregation="quarterly")
for row in anoms["anomalies"][:5]:
    print(row["metric"], row["period"], row["direction"], f'{row["pct_change"]}%', "z=", row["robust_z"])

print("\\n=== Why win rate dropped Q4 FY2025 ===")
why = tools.explain_change("win_rate", 2025, "Q4")
print(why["baseline_period"], why["baseline_value"], "→", why["current_period"], why["current_value"])
for event in why["nearby_events"]:
    print(" ", event["date"], event["title"])
"""
)

md(
    """## 5. Interview-day files

Keep the synthetic CSVs. Run this cell when they give you the two datasets.
Upload **metrics first**, then **events**. Column names are aliased; a wide KPI table is melted.
"""
)

code(
    """
from pathlib import Path
from finagent.datasets import activate_files, activate_synthetic
from finagent.store import DataStore
from finagent.agent import FinanceAgent
from finagent.tools import ToolBox

def reload_runtime():
    global store, tools, agent
    store = DataStore()
    tools = ToolBox(store)
    agent = FinanceAgent(store)
    cat = store.catalog()
    print("Active source:", cat["source"])
    print("Metrics file:", cat["metrics_path"])
    print("Events file:", cat["events_path"])
    print("Metric names:", [m["metric_name"] for m in cat["metrics"]])
    return cat

def load_interview_files(metrics_path, events_path):
    activate_files(metrics_path, events_path)
    return reload_runtime()

print("Synthetic is active until you upload interview files.")
print("Colab: run the next cell and pick the two files they give you.")
print("Local: set metrics_path / events_path in the cell after that.")
reload_runtime()
"""
)

code(
    """
# Colab upload widget. Skip this cell if you are not in Colab.
from pathlib import Path

if Path("/content").exists():
    from google.colab import files
    print("Select the METRICS file (csv / xlsx / json / parquet)")
    metrics_up = files.upload()
    print("Select the EVENTS file")
    events_up = files.upload()
    metrics_name = next(iter(metrics_up))
    events_name = next(iter(events_up))
    load_interview_files(Path.cwd() / metrics_name, Path.cwd() / events_name)
    print("Interview files loaded. Synthetic CSVs were not overwritten.")
    print(agent.ask("What data can you query?").answer)
else:
    print("Not in Colab. Use the next cell with local paths, or the Gradio upload controls.")
"""
)

code(
    """
# Optional local / pasted paths (the folder they give you on interview day).
# Leave both empty to keep the current source.

interview_metrics_path = ""  # e.g. "/content/their_metrics.csv"
interview_events_path = ""   # e.g. "/content/their_events.csv"

if interview_metrics_path and interview_events_path:
    load_interview_files(interview_metrics_path, interview_events_path)
else:
    print("No local paths set. Current source:", store.catalog()["source"])
"""
)

code(
    """
# Restore the built-in synthetic demo files (does not delete uploads).
activate_synthetic()
reload_runtime()
print(agent.ask("What was the revenue in Q1 FY2026?").answer)
"""
)

md("## 6. Chat UI — Gradio (same backend as Streamlit)")

code(
    """
import gradio as gr
from finagent.samples import SAMPLE_QUESTIONS

def chat_fn(message, history):
    turns = []
    for item in history or []:
        if isinstance(item, dict) and item.get("content"):
            turns.append({"role": item.get("role"), "content": item.get("content")})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            if item[0]:
                turns.append({"role": "user", "content": str(item[0])})
            if item[1]:
                turns.append({"role": "assistant", "content": str(item[1])})
    result = agent.ask(message, history=turns)
    check = result.requirement_check()
    footer = (
        f"\\n\\n_provider={result.provider} · tools={len(result.traces)} · "
        f"grounded={check['used_data_tool']} · source={store.catalog().get('source')}_"
    )
    return result.answer + footer

demo = gr.ChatInterface(
    fn=chat_fn,
    title="AetherData finance analyst (Gradio)",
    description=(
        "Same agent as the Cursor Streamlit app. "
        "Ask point, trend, anomaly, or why questions. "
        "Upload interview files in section 5 first if you have them."
    ),
    examples=SAMPLE_QUESTIONS[:6],
)

print("Launching Gradio. In Colab a public link appears.")
demo.launch(share=IN_COLAB, debug=False)
"""
)

md("## 7. Optional — turn on the live LLM (Colab secret `OPENAI_API_KEY`)")

code(
    """
import os
try:
    from google.colab import userdata
    key = userdata.get("OPENAI_API_KEY")
    if key:
        os.environ["OPENAI_API_KEY"] = key
except Exception:
    pass

from finagent.agent import FinanceAgent
from finagent.config import active_provider

live = FinanceAgent(store)
print("Provider:", active_provider(), "→", live.provider)
if live.provider == "offline":
    print("No API key. Offline planner still uses the same tools.")
    print("Colab: 🔑 Secrets → OPENAI_API_KEY → enable notebook access → rerun this cell.")
else:
    demo = live.ask("Which metrics look anomalous in FY2025 and FY2026?")
    print(demo.answer)
    print("tools used:", [t["tool"] for t in demo.traces])
"""
)

md("## 8. Optional — LangGraph-style loop (explicit, for discussion)")

code(
    """
def langgraph_style_turn(question: str):
    state = {"question": question, "scratch": [], "answer": None}
    if "anomal" in question.lower():
        state["scratch"].append(tools.detect_anomalies(aggregation="quarterly"))
    elif "why" in question.lower() or "explain" in question.lower():
        state["scratch"].append(tools.explain_change("win_rate", 2025, "Q4"))
    else:
        state["scratch"].append(
            tools.query_metrics(metric="revenue", fiscal_year=2026, fiscal_quarter="Q1", aggregation="quarterly")
        )
    state["answer"] = state["scratch"][-1]
    return state

state = langgraph_style_turn("What was the revenue in Q1 FY2026?")
print("Nodes: plan → act → answer")
print(state["answer"])
"""
)

md("## 9. Validation")

code(
    """
import subprocess, sys
print(subprocess.check_output([sys.executable, "-m", "pytest", "-q"], cwd=str(ROOT), text=True))
"""
)

md(
    """## 10. Talking points

- **R1 Chat UI:** Gradio here, Streamlit in Cursor, one agent.
- **R2 LLM backend:** OpenAI/Anthropic function calling; planner only if no key.
- **R3 Query mechanism:** six Pandas tools, not RAG over CSV text.
- **R4 Grounding:** no invented numbers; traces shown under each answer.
- **Interview swap:** upload / folder path / `data/interview/`. Synthetic files stay.
- **Q1 FY2026 revenue (synthetic):** $118.0M

Prompts to try in Gradio:

- What was the revenue in Q1 FY2026?
- How has ARR trended over the last 8 quarters?
- Which metrics look anomalous in FY2025 and FY2026?
- Why did win rate drop in Q4 FY2025?
"""
)

out = Path(__file__).resolve().parent / "Everpure_Colab_Upload.ipynb"
out.write_text(json.dumps(nb, indent=2), encoding="utf-8")
print(f"Wrote {out} with {len(nb['cells'])} cells")
