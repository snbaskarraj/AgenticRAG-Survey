"""Build the interview Colab notebook. Run: python3 notebooks/_build_colab.py"""

from __future__ import annotations

import json
from pathlib import Path

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        "colab": {"provenance": [], "toc_visible": True},
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
    """# Everpure Hands-on Agentic AI Exercise
## Conversational analyst over business metrics and events

**Audience:** walk through design, validation, and reasoning (not typing speed).
**Cursor path:** Streamlit at `http://localhost:8501` (`./run.sh`).
**This notebook:** SDLC, diagrams, Pandas, Pydantic, tool calling, optional OpenAI, a LangGraph-style loop, and a live **Gradio** chat.

### Email receipt (already drafted)

I confirm receipt of the exercise email. The application has:

1. a simple chat UI
2. an LLM-powered backend
3. a mechanism for the LLM to query / analyze the supplied data
4. answers grounded in the supplied datasets

Draft reply: `docs/EMAIL_RECEIPT.md`.
"""
)

md(
    """## 1. What we were asked to build

Two fictional datasets:

- **business metrics** (revenue, ARR, NRR, win rate, …)
- **business events** (launches, outages, competitor moves, pricing)

A conversational app that can answer:

- point questions — *What was the revenue in Q1 FY2026?*
- **metric trends**
- **unusual changes / anomalies**

Frameworks allowed: Python, Streamlit, Gradio, OpenAI SDK, Anthropic SDK, Pandas, LangChain, LangGraph, Pydantic.

### Framework split used here

| Surface | Framework | Why |
| --- | --- | --- |
| Cursor laptop | **Streamlit + OpenAI/Anthropic SDK + Pandas + Pydantic** | Best local chat, Data tab, tool traces |
| This Colab | **Gradio + Pandas + Pydantic + optional OpenAI + LangGraph-style loop** | Embeds in the notebook, easy to narrate |
"""
)

code(
    """
from IPython.display import HTML, display

def mermaid(graph: str):
    graph = graph.strip()
    display(HTML(f'''
    <div class="mermaid">{graph}</div>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
      mermaid.initialize({{ startOnLoad: true, theme: "neutral" }});
      mermaid.run();
    </script>
    '''))

print("Diagram helper ready.")
"""
)

md("## 2. SDLC used for the 60–90 minute exercise")

code(
    """
mermaid('''
flowchart LR
    A[1 Requirements] --> B[2 Design]
    B --> C[3 Implement]
    C --> D[4 Validate]
    D --> E[5 Demo]
    A --- A1[R1 chat UI<br/>R2 LLM backend<br/>R3 data tools<br/>R4 grounded]
    B --- B1[Tool-calling agent<br/>not dump CSVs]
    C --- C1[DataStore + ToolBox<br/>Streamlit / Gradio]
    D --- D1[pytest + ask.py]
    E --- E1[Cursor Streamlit<br/>Colab Gradio]
''')
"""
)

md(
    """| Phase | What we decide | Artifact |
| --- | --- | --- |
| Requirements | Map R1–R4 to files | `docs/SDLC.md` |
| Design | Grounding = control flow | architecture below |
| Implementation | One agent, two UIs | `src/finagent`, `app.py`, `gradio_app.py` |
| Validation | Known $118.0M Q1 FY2026 | `tests/`, `ask.py` |
| Demo | Cursor Streamlit, Colab Gradio | this notebook |

Design rules we will defend in the interview:

1. The LLM never reads the raw CSVs.
2. Company is the default segment (no double count).
3. Flow metrics sum; stock/rate metrics take last month.
4. Anomalies are statistical; events are correlated, not causal.
5. Streamlit in Cursor, Gradio in Colab, same backend.
"""
)

md("## 3. Architecture")

code(
    """
mermaid('''
flowchart TD
    U[User question] --> UI[Chat UI<br/>Streamlit or Gradio]
    UI --> A[FinanceAgent]
    A -->|API key| L[OpenAI / Anthropic<br/>function calling]
    A -->|no key| P[Offline planner<br/>same tools]
    L --> T[ToolBox]
    P --> T
    T --> Q[query_metrics]
    T --> TR[analyze_trend]
    T --> AN[detect_anomalies]
    T --> EV[search_events / explain_change]
    Q --> D[(metrics.csv + events.csv)]
    TR --> D
    AN --> D
    EV --> D
    T --> ANS[Grounded answer + traces]
''')
"""
)

md(
    """### Why not dump both CSVs into the prompt?

| Dump CSVs | Tool-calling agent |
| --- | --- |
| Context limit, silent rounding | Exact Pandas math |
| Hard to audit | Tool traces in the UI |
| Breaks when interview files grow | Same tools, new files |

That is the mechanism required by **R3** and the grounding required by **R4**.
"""
)

md("## 4. Setup — install and locate the project")

code(
    """
import os, sys, subprocess
from pathlib import Path

IN_COLAB = Path("/content").exists()
print("Running in Colab:" , IN_COLAB)

if IN_COLAB:
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-q",
        "pandas", "numpy", "pydantic", "python-dotenv", "openai", "gradio", "pytest",
    ])
    repo = Path("/content/AgenticRAG-Survey")
    if not repo.exists():
        subprocess.check_call([
            "git", "clone", "--depth", "1",
            "https://github.com/snbaskarraj/AgenticRAG-Survey.git",
            str(repo),
        ])
    ROOT = repo / "everpuresep32026"
else:
    here = Path.cwd().resolve()
    ROOT = here if (here / "src" / "finagent").exists() else here.parent
    if not (ROOT / "src" / "finagent").exists():
        ROOT = Path("/workspace/everpuresep32026")

os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))
print("Project root:", ROOT)
print("metrics exists:", (ROOT / "data" / "metrics.csv").exists())
"""
)

md("## 5. Data layer — Pandas + fiscal calendar")

code(
    """
from finagent.store import DataStore
from finagent.fiscal import fiscal_label, fiscal_year, fiscal_quarter

store = DataStore()
catalog = store.catalog()
print("Fiscal calendar:", catalog["fiscal_calendar"])
print("Period range:", catalog["metrics_period_range"])
print("Metrics:", [m["metric_name"] for m in catalog["metrics"]])
print("Event types:", catalog["event_types"])
print()
print("Q1 FY2026 means", fiscal_label("2025-02-01"), "through", fiscal_label("2025-04-30"))
print("January 2026 is", fiscal_label("2026-01-20"))
store.metrics.head()
"""
)

code(
    """
q1 = store.query_metrics(
    metric="revenue",
    fiscal_year=2026,
    fiscal_quarter="Q1",
    aggregation="quarterly",
)
display(q1[["fiscal_period", "segment", "metric_name", "metric_value", "unit"]])
print("Q1 FY2026 company revenue = $", f"{q1.iloc[0]['metric_value']:,.0f}")
assert q1.iloc[0]["metric_value"] == 118_000_000
print("Acceptance test passed: $118.0M")
"""
)

md(
    """**Decision:** long-format metrics (`period, metric_name, metric_value, segment`)
plus a date-stamped events table. When Everpure drops the real files, only
`store.py` aliases need to match. The agent tools stay the same.
"""
)

md("## 6. Mechanism for the LLM to query / analyze data")

code(
    """
from finagent.tools import ToolBox

tools = ToolBox(store)
print("Tools the LLM is allowed to call:")
for name in tools.names():
    print(" -", name)

print("\\n--- query_metrics ---")
print(tools.query_metrics(metric="revenue", fiscal_year=2026, fiscal_quarter="Q1", aggregation="quarterly"))
"""
)

code(
    """
print("--- analyze_trend (ARR, last 8 quarters) ---")
trend = tools.analyze_trend("arr", aggregation="quarterly", periods=8)
print({k: trend[k] for k in ("direction", "total_change_pct", "latest")})

print("\\n--- detect_anomalies ---")
anoms = tools.detect_anomalies(aggregation="quarterly")
for row in anoms["anomalies"][:5]:
    print(row["metric"], row["period"], row["direction"], row["pct_change"], "z=", row["robust_z"])
"""
)

code(
    """
print("--- explain_change: win rate Q4 FY2025 ---")
why = tools.explain_change("win_rate", 2025, "Q4")
print(why["baseline_period"], why["baseline_value"], "→", why["current_period"], why["current_value"])
for event in why["nearby_events"]:
    print(" event:", event["date"], event["title"])
"""
)

md(
    """Anomaly method: **robust z-score on quarter-over-quarter percent change**.
We do not ask the LLM to “spot spikes” from memory. The model only narrates
tool output.
"""
)

md("## 7. LLM-powered backend + Pydantic contract")

code(
    """
from finagent.agent import FinanceAgent
from finagent.config import active_provider
from finagent.schemas import AgentResponse

agent = FinanceAgent(store)
print("Active provider:", active_provider())
print("Pydantic model:", AgentResponse.__name__)

response = agent.ask("What was the revenue in Q1 FY2026?")
print(response.answer)
print("provider:", response.provider, "model:", response.model)
print("requirement check:", response.requirement_check())
assert "118" in response.answer
"""
)

md(
    """If `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set, `FinanceAgent` uses native
function calling. If not, the **offline planner** calls the same tools so
this notebook stays reproducible.

That still satisfies R3/R4. R2 (LLM backend) is the OpenAI/Anthropic path —
use a Colab secret for the live interview if you want the model to plan tool calls.
"""
)

md("## 8. Optional — OpenAI SDK tool loop (set Colab secret `OPENAI_API_KEY`)")

code(
    """
import os
try:
    from google.colab import userdata
    os.environ.setdefault("OPENAI_API_KEY", userdata.get("OPENAI_API_KEY") or "")
except Exception:
    pass

if os.getenv("OPENAI_API_KEY"):
    from finagent.agent import FinanceAgent
    live = FinanceAgent(store)
    print("Provider now:", live.provider)
    demo = live.ask("Which metrics look anomalous in FY2025?")
    print(demo.answer)
    print("tools used:", [t["tool"] for t in demo.traces])
else:
    print("No OPENAI_API_KEY in this runtime. Offline planner remains active.")
    print("In Colab: 🔑 Secrets → OPENAI_API_KEY → enable notebook access, then rerun.")
"""
)

md("## 9. Optional — LangGraph-style loop (explicit, no hidden graph magic)")

code(
    """
# Pedagogical loop. Same control flow we run in agent.py.
# We keep it visible so the interview discussion stays on design, not framework.

def langgraph_style_turn(question: str):
    state = {"question": question, "scratch": [], "answer": None}
    # node: plan
    plan = tools.detect_anomalies if "anomal" in question.lower() else tools.query_metrics
    # node: act
    if plan is tools.detect_anomalies:
        state["scratch"].append(plan(aggregation="quarterly"))
    else:
        state["scratch"].append(
            tools.query_metrics(metric="revenue", fiscal_year=2026, fiscal_quarter="Q1", aggregation="quarterly")
        )
    # node: answer (grounded)
    payload = state["scratch"][-1]
    state["answer"] = payload
    return state

state = langgraph_style_turn("What was the revenue in Q1 FY2026?")
print("Graph nodes: plan → act → answer")
print("Grounded payload keys:", list(state["answer"].keys()))
print("Rows:", state["answer"].get("rows"))
"""
)

code(
    """
mermaid('''
flowchart LR
    S[State: question] --> P[Plan node]
    P --> X[Act / tool node]
    X --> R[Answer node]
    R --> O[Grounded reply]
''')
"""
)

md(
    """We did **not** take a hard LangChain dependency in the Cursor app on purpose.
A 60–90 minute exercise is easier to debug when the loop is 40 lines of Python
you can point at. Colab shows the equivalent graph so we can still discuss
LangGraph if asked.
"""
)

md("## 10. Chat UI — Gradio (best in Colab)")

code(
    """
import json
import gradio as gr
from finagent.samples import SAMPLE_QUESTIONS

def chat_fn(message, history):
    turns = []
    for item in history or []:
        if isinstance(item, dict) and item.get("content"):
            turns.append({"role": item["role"], "content": item["content"]})
    result = agent.ask(message, history=turns)
    footer = f"\\n\\n_provider={result.provider} · tools={len(result.traces)} · grounded={result.requirement_check()['used_data_tool']}_"
    return result.answer + footer

demo = gr.ChatInterface(
    fn=chat_fn,
    title="AetherData finance analyst (Gradio)",
    description="Same backend as the Cursor Streamlit app. Ask about metrics and events.",
    examples=SAMPLE_QUESTIONS[:6],
)

print("Launching Gradio. In Colab a public link or inline UI will appear.")
demo.launch(share=IN_COLAB, debug=False)
"""
)

md(
    """### Streamlit (best in Cursor, not this notebook)

```bash
cd everpuresep32026
./run.sh          # http://localhost:8501
./run_gradio.sh   # http://localhost:7860
```

Streamlit is the Cursor default because the Data tab, sample-question
buttons, and tool-trace expanders are better for a live laptop demo.
**Both UIs call `FinanceAgent.ask()`.**
"""
)

md("## 11. Validation checklist")

code(
    """
import subprocess, sys
print(subprocess.check_output([sys.executable, "-m", "pytest", "-q"], text=True))
"""
)

md(
    """Manual questions to run during the interview (after the real files land):

1. A point question with a fiscal period (*What was the revenue in Q1 FY2026?*)
2. A trend (*How has ARR trended over the last 8 quarters?*)
3. An anomaly scan
4. A why-question that should pull **events**

If a number is not in a tool result, the correct answer is “not in the dataset”.
"""
)

md(
    """## 12. Talking points if they ask “why this design?”

- **R1 Chat UI:** Streamlit locally, Gradio in Colab — one agent, two skins.
- **R2 LLM backend:** OpenAI/Anthropic function calling; planner only if no key.
- **R3 Query mechanism:** six deterministic tools over Pandas. Not RAG over CSV text.
- **R4 Grounding:** system prompt + tool-only numbers + visible traces.
- **Swap-in:** column aliases and `FINAGENT_DATA_DIR` because the real files arrive 30 minutes before the call.
- **What I would add with more time:** SQL warehouse, eval set of gold questions, citation highlighter that rejects numbers not present in tool JSON.
"""
)

out = Path(__file__).resolve().parent / "Everpure_Agentic_Finance_Agent.ipynb"
out.write_text(json.dumps(nb, indent=2), encoding="utf-8")
print(f"Wrote {out} with {len(nb['cells'])} cells")
