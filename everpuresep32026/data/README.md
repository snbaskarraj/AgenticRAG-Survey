# Datasets

The agent always needs **two** files: business metrics and business events.

## Synthetic files (do not overwrite)

These stay in place so the app works before the interview files arrive.

- `metrics.csv`
- `events.csv`

Regenerate them with `python data/generate_data.py`.

## Interview-day files

Do **not** replace the synthetic CSVs. Load the files they give you in one of these ways:

1. Streamlit / Gradio sidebar: paste the folder path, or upload the two files
2. Copy the two files into `data/interview/`
3. Set `FINAGENT_DATA_DIR` or `FINAGENT_METRICS_PATH` + `FINAGENT_EVENTS_PATH`

Uploads go to `data/uploads/`. The active choice is stored in `data/active.json`.
**Restore synthetic data** switches back without deleting the interview files.

## Expected shapes

### metrics (long form)

| column | required | aliases |
| --- | --- | --- |
| period | yes | `month`, `date`, `as_of` |
| metric_name | yes | `metric`, `kpi`, `name` |
| metric_value | yes | `value`, `amount` |
| segment | no | defaults to `Company` |

A **wide** table (one column per KPI plus a date column) is accepted and melted.

### events

| column | required | aliases |
| --- | --- | --- |
| date | yes | `event_date`, `occurred_at` |
| title or description | yes | `name`, `details` |
