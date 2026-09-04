# Everpure Sep 3 2026 — Agentic Finance Analyst

Conversational agent for the Everpure hands-on exercise. It answers
questions about two fictional datasets and stays grounded in those files.

**Open this folder in the IDE** (`File → Open Folder → everpuresep32026`)
or open `Everpure-Finance-Agent.code-workspace`. See [OPEN_IN_IDE.md](OPEN_IN_IDE.md).

## Project structure

```text
everpuresep32026/                      ← open this in Cursor / VS Code
├── Everpure-Finance-Agent.code-workspace
├── .vscode/                           ← launch, tasks, Python path
│   ├── launch.json
│   ├── tasks.json
│   ├── settings.json
│   └── extensions.json
├── app.py                             ← Streamlit chat UI (Cursor default)
├── gradio_app.py                      ← Gradio chat UI
├── ask.py                             ← CLI
├── run.sh                             ← start Streamlit :8501
├── run_gradio.sh                      ← start Gradio :7860
├── requirements.txt
├── pyproject.toml
├── data/
│   ├── metrics.csv                    ← business metrics
│   ├── events.csv                     ← business events
│   └── generate_data.py
├── src/finagent/                      ← LLM backend + data tools
│   ├── agent.py
│   ├── tools.py
│   ├── store.py
│   ├── schemas.py
│   └── fallback.py
├── tests/
├── docs/
│   ├── SETUP.md
│   ├── SDLC.md
│   └── EMAIL_RECEIPT.md
└── notebooks/
    └── Everpure_Agentic_Finance_Agent.ipynb
```

| Requirement | Where it lives |
| --- | --- |
| Simple chat UI | Streamlit (`app.py`) in Cursor · Gradio (`gradio_app.py`) in Colab |
| LLM-powered backend | `src/finagent/agent.py` (OpenAI or Anthropic tool calling) |
| Query / analyze data | `query_metrics`, `analyze_trend`, `detect_anomalies`, `search_events`, `explain_change` |
| Grounded answers | The model never sees the raw CSVs; tools compute every number |

## Execute

Read **[docs/SETUP.md](docs/SETUP.md)** for the full runbook.

**Cursor (best local path — Streamlit)**

```bash
./run.sh
# open http://localhost:8501
```

**Cursor alternate UI — Gradio**

```bash
./run_gradio.sh
# open http://localhost:7860
```

**Google Colab (diagrams + multiple frameworks)**

Open [`notebooks/Everpure_Agentic_Finance_Agent.ipynb`](notebooks/Everpure_Agentic_Finance_Agent.ipynb)
and Runtime → Run all.

Do not execute `.vscode/launch.json` in a terminal. Use **Run and Debug**.

## Documents

| Doc | Purpose |
| --- | --- |
| [docs/SETUP.md](docs/SETUP.md) | How to run Cursor, Gradio, Colab, and swap interview files |
| [docs/SDLC.md](docs/SDLC.md) | Requirements → design → implementation → tests → demo |
| [docs/EMAIL_RECEIPT.md](docs/EMAIL_RECEIPT.md) | Reply confirming receipt of Anurag’s email |

## Sample questions

- What was the revenue in Q1 FY2026?
- How has ARR trended over the last 8 quarters?
- Which metrics look anomalous in FY2025 and FY2026?
- Why did win rate drop in Q4 FY2025?

Q1 FY2026 revenue in the synthetic set is **$118.0M**.

## Architecture

```
Chat UI (Streamlit in Cursor, Gradio in Colab)
        │
        ▼
FinanceAgent ── OpenAI / Anthropic tool loop
        │        or offline planner if no API key
        ▼
ToolBox
        │
        ▼
DataStore  ← metrics.csv + events.csv
```

Fiscal year starts 1 February. Q1 FY2026 = Feb–Apr 2025.

When the interview CSVs arrive, replace `data/metrics.csv` and
`data/events.csv` (column names are aliased).
