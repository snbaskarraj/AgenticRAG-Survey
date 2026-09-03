# AetherData Finance Agent

Hands-on agentic application for the Everpure interview exercise: a chat UI plus an LLM-backed (or deterministic) analyst that answers questions about two fictional datasets.

- **metrics.csv** — monthly business KPIs
- **events.csv** — business events aligned to the same fiscal calendar

The model never reads the CSVs directly. It has to call analysis tools, so answers stay grounded in the supplied files.

## Run it

```bash
cd finance_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python data/generate_data.py          # already committed; rerun to refresh
streamlit run app.py
```

CLI check:

```bash
python ask.py "What was the revenue in Q1 FY2026?"
python ask.py "Why did win rate drop in Q4 FY2025?" --show-traces
```

Tests:

```bash
pytest -q
```

## What you can ask

- Point values: *What was the revenue in Q1 FY2026?*
- Trends: *How has ARR trended over the last 8 quarters?*
- Anomalies: *Which metrics look unusual in FY2025 and FY2026?*
- Explanations: *Why did win rate drop in Q4 FY2025?*

## Architecture

```
Chat UI (Streamlit)
        │
        ▼
FinanceAgent ── OpenAI / Anthropic tool loop
        │        or offline deterministic planner
        ▼
ToolBox  (query, trend, anomaly, events, explain)
        │
        ▼
DataStore  ← metrics.csv + events.csv
```

| Requirement | Implementation |
| --- | --- |
| Simple chat UI | `app.py` Streamlit chat, data preview, tool traces |
| LLM-powered backend | OpenAI or Anthropic function calling when an API key is set |
| Mechanism to query/analyze data | Six tools in `src/finagent/tools.py` |
| Answers grounded in the datasets | Tools compute numbers; the system prompt forbids invented figures; offline mode renders tool output directly |

No LangChain / LangGraph. The control loop is explicit so it is easy to discuss in the interview.

## Fiscal calendar

February–January, matching a common enterprise-storage year:

| Quarter | Calendar months | Example |
| --- | --- | --- |
| Q1 FY2026 | Feb–Apr 2025 | Revenue **$118.0M** |
| Q2 FY2026 | May–Jul 2025 | Sales realignment dip |
| Q3 FY2026 | Aug–Oct 2025 | NAND supply miss |
| Q4 FY2026 | Nov 2025–Jan 2026 | AetherOne launch |

## Story baked into the synthetic data

AetherData is a fictional all-flash / data-platform vendor.

- FY2025 Q2 — AetherFlash 2.0 launch, demand spike
- FY2025 Q3 — US-East outage, ticket surge, NRR drop
- FY2025 Q4 — NimbusBlock 20% price cut, win-rate crash
- FY2026 Q1 — 8% list-price increase + Northwind Cloud partnership
- FY2026 Q2 — CEO transition and territory realignment
- FY2026 Q3 — NAND constraint, slipped shipments
- FY2026 Q4 — AetherOne GA and a record year-end close

## LLM vs offline mode

| Mode | When | Behavior |
| --- | --- | --- |
| OpenAI | `OPENAI_API_KEY` set | Tool-calling loop, `gpt-4.1-mini` by default |
| Anthropic | only `ANTHROPIC_API_KEY` set | Tool-calling loop, `claude-sonnet-4-5` by default |
| Offline | no key | Same tools, regex planner, deterministic wording |

Copy `.env.example` to `.env` to switch providers. Offline mode is intentional: the app is demonstrable without a key, and the interview files can be dropped in later.

## Swap in the real interview datasets

1. Replace `data/metrics.csv` and `data/events.csv`, **or**
2. Point `FINAGENT_DATA_DIR` at a folder that contains them.

The loader aliases common column names (`date`/`month`, `kpi`/`metric`, `value`/`amount`). If `fiscal_year` is missing, it is derived from the period using the February fiscal calendar.

Expected metric grain: one row per period / metric / segment. Expected event grain: one row per event with a date and a title or description.

## Design notes worth discussing

1. **Grounding is a control-flow problem**, not a prompt-only problem. The LLM cannot see the CSVs.
2. **Company is the default segment** so Enterprise + Mid-Market + Cloud are not summed by accident.
3. **Flow vs stock vs rate** aggregation: revenue sums; ARR and NRR take the last month in the bucket.
4. **Anomalies are statistical** (robust z-score on period-over-period % change), then events are joined for narrative.
5. **`explain_change` does not claim causation.** It returns the metric delta and nearby events.
6. The data layer is the piece that should stay stable when the real sample files arrive 30 minutes before the call.
