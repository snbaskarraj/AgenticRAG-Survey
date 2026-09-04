# Open this project in Cursor / VS Code

This folder **is** the IDE project. Open it as the workspace root.

## Option A — Open the folder (simplest)

1. Cursor / VS Code → **File → Open Folder…**
2. Choose `everpuresep32026`
3. When prompted, install recommended extensions (Python, debugpy, Jupyter)

The explorer should look like this:

```text
Everpure Finance Agent
├── .vscode/                 ← Run and Debug, Tasks, Python path
├── app.py                   ← Streamlit chat (Cursor default)
├── gradio_app.py            ← Gradio chat
├── ask.py                   ← CLI
├── run.sh / run_gradio.sh
├── data/                    ← metrics.csv + events.csv
├── src/finagent/            ← LLM agent + tools
├── tests/
├── docs/
└── notebooks/
```

## Option B — Open the workspace file

- From this folder: open `Everpure-Finance-Agent.code-workspace`
- From the repo root: open `everpuresep32026.code-workspace`

## Then run

Do **not** type `.vscode/launch.json` in the terminal.

| Action | Where |
| --- | --- |
| Streamlit chat | **Run and Debug → Everpure Finance Agent (Streamlit)** or `./run.sh` |
| Gradio chat | **Run and Debug → Everpure Finance Agent (Gradio)** or `./run_gradio.sh` |
| Tests | Testing sidebar, or `python3 -m pytest -q` |
| Sample question | **Run and Debug → Ask a sample question** |

UIs:

- Streamlit: http://localhost:8501
- Gradio: http://localhost:7860

On interview day, keep the synthetic files. In the Streamlit sidebar (or
Gradio top panel) paste the folder they give you, or upload the two files.
**Restore synthetic data** switches back. Details: `data/interview/README.md`.
