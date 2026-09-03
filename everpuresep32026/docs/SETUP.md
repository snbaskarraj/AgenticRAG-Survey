# How to execute the whole setup

Two ways to run the same agent:

| Path | UI | Best for |
| --- | --- | --- |
| **Cursor / local** | Streamlit at http://localhost:8501 | Interview laptop, debugging, data tabs |
| **Google Colab** | Gradio inside the notebook | Walkthrough, diagrams, multi-framework demo |

Do **not** run `.vscode/launch.json` in the terminal. That file is a Cursor
debug configuration, not a shell script.

## 0. One-time install

From this folder (`everpuresep32026`):

```bash
pip install -r requirements.txt
python3 -m pytest -q
```

Optional LLM key (recommended for the interview):

```bash
cp .env.example .env
# set OPENAI_API_KEY=...   or   ANTHROPIC_API_KEY=...
```

Without a key the same tools still run through a deterministic planner, so
the demo stays grounded.

## 1. Cursor path (primary): Streamlit

If the prompt already says `everpuresep32026 $`:

```bash
./run.sh
```

From the repo root:

```bash
./everpuresep32026/run.sh
```

Or in Cursor:

1. Open `everpuresep32026` or `everpuresep32026.code-workspace`
2. **Run and Debug → Everpure Finance Agent (Streamlit)**
3. Or **Tasks: Run Task → Run chat app**

Open **http://localhost:8501** and ask:

`What was the revenue in Q1 FY2026?`

Expected grounded answer: **$118.0M** from `data/metrics.csv`.

If port 8501 is already taken, `./run.sh` reuses the live server.

## 2. Cursor alternate UI: Gradio

```bash
./run_gradio.sh
```

Or **Run and Debug → Everpure Finance Agent (Gradio)**.

Open **http://localhost:7860**. Same agent, same CSVs, same tools.

## 3. CLI smoke test

```bash
python3 ask.py "What was the revenue in Q1 FY2026?"
python3 ask.py "Why did win rate drop in Q4 FY2025?" --show-traces
```

## 4. Google Colab path

1. Open `notebooks/Everpure_Agentic_Finance_Agent.ipynb` in Colab
2. Runtime → Run all
3. The notebook restates the exercise, SDLC, architecture diagrams,
   design decisions, Pandas analysis, tool calls, an optional OpenAI
   cell, a LangGraph-style loop, and a live **Gradio** chat

Upload `data/metrics.csv` and `data/events.csv` into the notebook folder
if you are not cloning the repo.

## 5. Swap in the interview datasets

Thirty minutes before the call you will receive two real files. Then:

```bash
# replace these two files, keep the names or set FINAGENT_DATA_DIR
cp /path/to/their_metrics.csv data/metrics.csv
cp /path/to/their_events.csv  data/events.csv
```

The loader aliases common columns (`date`/`month`, `kpi`/`metric`,
`value`/`amount`). Restart Streamlit/Gradio after replacing files.

## Ports

| App | Port | Script |
| --- | --- | --- |
| Streamlit | 8501 | `./run.sh` |
| Gradio | 7860 | `./run_gradio.sh` |
