# SDLC for the Everpure Agentic Finance Agent

The interview scores design, validation, and reasoning. This file is the
software-development lifecycle for the project, mapped to code.

```text
Requirements → Design → Implementation → Validation → Release / Demo
     │            │            │              │              │
 docs/SETUP   architecture   src/finagent    tests/      Streamlit
 EMAIL_RECEIPT  tools.py      app.py         ask.py      Gradio
                schemas.py    gradio_app.py  pytest      Colab
```

## 1. Requirements

Source: Everpure hands-on Agentic AI exercise.

| ID | Requirement | Implementation |
| --- | --- | --- |
| R1 | Simple chat UI | `app.py` (Streamlit, Cursor default), `gradio_app.py` |
| R2 | LLM-powered backend | `src/finagent/agent.py` — OpenAI or Anthropic tool loop |
| R3 | Mechanism to query/analyze data | `ToolBox` in `src/finagent/tools.py` |
| R4 | Answers grounded in supplied datasets | tools only; system prompt forbids invented numbers |
| R5 | Point questions, trends, anomalies | `query_metrics`, `analyze_trend`, `detect_anomalies` |
| R6 | Two datasets: metrics + events | `data/metrics.csv`, `data/events.csv` |
| R7 | 60–90 minute swap-in | column aliases in `store.py`, `FINAGENT_DATA_DIR` |

Acceptance examples:

- “What was the revenue in Q1 FY2026?” → `$118.0M` from metrics
- ARR trend over last 8 quarters → `analyze_trend`
- Unusual changes → robust z-score on period-over-period % change
- “Why did win rate drop in Q4 FY2025?” → metric delta + nearby events

## 2. Design decisions

1. **Grounding is control flow, not a longer prompt.** The LLM never
   receives the raw CSVs. It must call tools.
2. **Streamlit in Cursor, Gradio in Colab.** Streamlit has a better local
   layout (sidebar, Data tab, traces). Gradio embeds cleanly in notebooks.
3. **Same backend for every UI.** `FinanceAgent.ask()` is the only entry.
4. **No LangChain/LangGraph in the Cursor runtime.** The tool loop is
   explicit so it is easy to debug and discuss. Colab shows a LangGraph-style
   loop as a teaching cell.
5. **Pydantic** models (`AgentResponse`) keep Streamlit and Gradio aligned.
6. **February fiscal year** so “Q1 FY2026” is deterministic (Feb–Apr 2025).
7. **Company is the default segment** so Enterprise + Cloud are not summed.
8. **Flow vs stock vs rate:** revenue sums; ARR and NRR take last month.
9. **Anomalies are statistical.** Events are joined afterwards. No causation claim.
10. **Offline planner** uses the same tools when no API key is present so
    the demo and tests stay deterministic.

```text
User question
    │
    ▼
Chat UI (Streamlit or Gradio)
    │
    ▼
FinanceAgent  ── OpenAI / Anthropic function calling
    │            (or offline planner if no key)
    ▼
ToolBox
    ├─ query_metrics
    ├─ analyze_trend
    ├─ detect_anomalies
    ├─ search_events
    └─ explain_change
    │
    ▼
DataStore  ← metrics.csv + events.csv
    │
    ▼
Grounded answer + tool traces
```

## 3. Implementation map

| Layer | Files |
| --- | --- |
| Data | `data/generate_data.py`, `data/metrics.csv`, `data/events.csv` |
| Calendar | `src/finagent/fiscal.py` |
| Store | `src/finagent/store.py` |
| Tools | `src/finagent/tools.py` |
| Agent | `src/finagent/agent.py`, `prompts.py`, `fallback.py` |
| Contracts | `src/finagent/schemas.py` |
| Streamlit | `app.py` |
| Gradio | `gradio_app.py` |
| CLI | `ask.py` |
| Tests | `tests/` |

## 4. Validation

```bash
python3 -m pytest -q
python3 ask.py "What was the revenue in Q1 FY2026?"
```

Automated checks cover fiscal mapping, Q1 FY2026 revenue, no double-count
of segments, win-rate anomaly, competitor event join, and planner routing.

Manual demo script is in `docs/SETUP.md`.

## 5. Release / demo

- Cursor: `./run.sh` → http://localhost:8501
- Alternate UI: `./run_gradio.sh` → http://localhost:7860
- Explain path: `notebooks/Everpure_Agentic_Finance_Agent.ipynb`

When the real files arrive, replace the two CSVs and rerun the Q1-style
question plus one trend and one anomaly question before the discussion.
