# Datasets

Two fictional files power the agent. Replace them with the interview sample files when they arrive.

## metrics.csv

One row per period / metric / segment.

| column | required | notes |
| --- | --- | --- |
| period | yes | `YYYY-MM` or a parseable date |
| metric_name | yes | aliases: `metric`, `kpi`, `name` |
| metric_value | yes | aliases: `value`, `amount` |
| segment | no | defaults to `Company` |
| unit | no | `USD`, `percent`, `count` |
| metric_kind | no | `flow` sums; `stock`/`rate` take last month |
| fiscal_year / fiscal_quarter | no | derived from period if omitted |

## events.csv

One row per business event.

| column | required | notes |
| --- | --- | --- |
| date | yes | aliases: `event_date`, `occurred_at` |
| title or description | yes | used for search |
| event_type | no | `product_launch`, `outage`, `competitor`, … |
| impact_area | no | metric names the event may have touched |
| severity / segment | no | |

Regenerate the synthetic files with:

```bash
python data/generate_data.py
```
