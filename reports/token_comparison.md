# Token Comparison - Graph-Guided vs Naive Baseline

| Run | Input tok | Output tok | Total | Files read | Iterations | # LLM calls | Duration (s) | Correctness | Notes |
|---|---|---|---|---|---|---|---|---|---|
| graph_guided | 1559 | 1020 | 2579 | 3 | 1 | 2 | 29.11 | pass | hot.md + polygons.py only |
| naive | 3670 | 2684 | 6354 | 8 | 1 | 2 | 35.64 | fail | full data/broken-python/** dump |

> **Columns `Files read` and `Iterations` are mandated by R5.6.5 (PDF §5.6)** - not optional. `Files read` = distinct files/textual units that entered the LLM context; `Iterations` = hypothesize->validate rounds. Together with `Duration` and `Correctness` they answer R5.6.5 (d) ("quality and speed of reaching root cause").

## R4.1 - Token reduction
Graph-guided used 57.5% fewer input tokens than naive (1559 vs 3670), because the `fix` node received only index.md + hot.md + polygons.py instead of the full data/broken-python/** dump.

## R4.2 - Accuracy cost
graph_guided passed correctness while naive failed - token savings came with improved (not worse) localization.

## Cost (USD)
Model: `gemini-2.5-flash`. Rates (config-driven, `config/agent.json` `pricing`): $0.3/1M input, $2.5/1M output. Token counts trace to the gatekeeper JSONL ledger (`artifacts/runs/`); cost = logged tokens x these rates.

| Run | Cost (USD) |
|---|---|
| graph_guided | $0.0030 |
| naive | $0.0078 |

Graph-guided cost **$0.0030** vs naive **$0.0078** — **61.4% lower total cost**.

> This is the keyed live run. The keyless, reproducible input-context delta (76.7%, `uv run pytest -m eval`) and the full model-switching log are in [`run_journey.md`](run_journey.md).
