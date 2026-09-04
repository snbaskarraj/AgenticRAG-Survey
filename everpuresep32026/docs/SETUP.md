# How to execute the whole setup

First open the project in the IDE: **File → Open Folder → `everpuresep32026`**
(or open `Everpure-Finance-Agent.code-workspace`). Details: [OPEN_IN_IDE.md](../OPEN_IN_IDE.md).

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

Download **`Everpure_Colab_Upload.ipynb`** from this folder (also under
`notebooks/`).

1. [colab.research.google.com](https://colab.research.google.com) → **Upload notebook**
2. Runtime → **Run all**
3. Ask *What was the revenue in Q1 FY2026?* in the Gradio cell ($118.0M on synthetic)
4. On interview day, run the **Interview-day files** upload cell and pick the two files they give you

The notebook clones this repo if you uploaded only the `.ipynb`. Synthetic
CSVs stay intact. Streamlit remains the Cursor UI.

## 5. Interview-day files (keep the synthetic CSVs)

The code and `data/metrics.csv` / `data/events.csv` stay intact.

When they give you a folder or two files:

1. In Streamlit (http://localhost:8501) or Gradio (http://localhost:7860),
   open the sidebar / top panel.
2. Paste the **folder path they give you** and click **Use this folder**,
   **or** upload the two files.
3. Ask the same questions again (`What was the revenue in Q1 FY2026?`,
   a trend, an anomaly).
4. Click **Restore synthetic data** if you want the demo files back.

CLI / env alternative:

```bash
export FINAGENT_DATA_DIR="/path/they/give/you"
# or
export FINAGENT_METRICS_PATH="/path/metrics.csv"
export FINAGENT_EVENTS_PATH="/path/events.csv"
```

You can also copy the two files into `data/interview/` (do not overwrite
`data/metrics.csv` or `data/events.csv`). Column names are aliased;
wide KPI tables are melted automatically.

## Ports

| App | Port | Script |
| --- | --- | --- |
| Streamlit | 8501 | `./run.sh` |
| Gradio | 7860 | `./run_gradio.sh` |
