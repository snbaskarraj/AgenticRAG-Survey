# Everpure Sep 3 2026 — Finance Analyst Agent

Standalone project for the Everpure hands-on Agentic AI exercise.

A chat UI talks to an analyst agent. The agent can only see the business
data through tools, so answers stay grounded in two fictional datasets:

- `data/metrics.csv` — monthly KPIs
- `data/events.csv` — business events on the same fiscal calendar

## Run in Cursor

1. Open this folder (`everpuresep32026`) as the project.
2. Install once if needed: `pip install -r requirements.txt`
3. Start the chat app from **this folder**:
   - Terminal: `./run.sh`
   - From the repo root: `./everpuresep32026/run.sh`
   - Command Palette → **Tasks: Run Task** → **Run chat app**
   - Run and Debug → **Everpure Finance Agent**

Do not `cd everpuresep32026` again if the prompt already shows `everpuresep32026 $`.
If port 8501 is already in use, `./run.sh` reuses that server instead of failing.

The UI is at [http://localhost:8501](http://localhost:8501).

CLI from this folder:

```bash
python3 ask.py "What was the revenue in Q1 FY2026?"
python3 ask.py "Why did win rate drop in Q4 FY2025?" --show-traces
python3 -m pytest -q
```

## Sample questions

- What was the revenue in Q1 FY2026?
- How has ARR trended over the last 8 quarters?
- Which metrics look anomalous in FY2025 and FY2026?
- Why did win rate drop in Q4 FY2025?
- Compare Enterprise vs Cloud revenue in FY2026.
- What happened to churn after the FY2026 price increase?
- Which events most likely explain the FY2026 Q3 revenue dip?

## LLM vs offline

The app runs without an API key using the same analysis tools.

| Mode | When | Behavior |
| --- | --- | --- |
| Offline | no key | Deterministic planner + tools |
| OpenAI | `OPENAI_API_KEY` | Tool-calling loop |
| Anthropic | only `ANTHROPIC_API_KEY` | Tool-calling loop |

Copy `.env.example` to `.env` to switch providers.

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

Fiscal year starts February 1. Q1 FY2026 is Feb–Apr 2025.

When the interview sample files arrive, replace `data/metrics.csv` and
`data/events.csv`, or set `FINAGENT_DATA_DIR`. Column names are aliased.
