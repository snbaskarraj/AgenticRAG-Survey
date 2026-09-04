# Interview-day drop folder

On the call you will be given two files (metrics and events) and a location.

Leave the synthetic files in `data/metrics.csv` and `data/events.csv` alone.

Use any one of these:

1. **Paste the given folder path** in the Streamlit/Gradio sidebar and click
   **Use this folder**.
2. **Copy the two files here** (`everpuresep32026/data/interview/`).
   Name them so one file has `metric` / `kpi` in the name and the other has
   `event`.
3. **Upload** the two files in the chat UI. Uploads are copied to
   `data/uploads/` and do not overwrite the synthetic CSVs.
4. Environment variables:

   ```bash
   export FINAGENT_DATA_DIR="/path/they/give/you"
   # or
   export FINAGENT_METRICS_PATH="/path/metrics.csv"
   export FINAGENT_EVENTS_PATH="/path/events.csv"
   ```

Click **Restore synthetic data** to go back to the built-in demo files.
