# Token Comparison — Graph-Guided vs Naive Baseline (R5.6 / R7.8 / R4.1)

> **Two layers of evidence.** (1) A **keyless, reproducible** measurement of the independent
> variable — the *input context* each route feeds the LLM — available now. (2) The **full
> keyed run** (output tokens, LLM-call counts, duration, end-to-end correctness from a real
> provider), which is a manual, owner-run step (ADR-0005) and is **PENDING** below. Per
> CLAUDE.md §4, no number here is an estimate: each traces to a command you can re-run.

## Layer 1 — Input-context measurement (keyless, available now)

This is the core of the thesis (R4.1): the graph-guided route sends the LLM a curated map
(`index.md` + `hot.md`) plus **exactly one** validated source file, while the naive route
dumps the whole tree. Measured by `agent_workflow.context` (the same context the gatekeeper
later bills), via the `tests/evals/test_agent_context_delta.py` structural eval:

| Route | Input context tokens | Files read | What entered context |
|---|---|---|---|
| **graph-guided** | **406** | 1 source (+ index.md + hot.md) | `obsidian/index.md`, `obsidian/hot.md`, `polygons/polygons.py` |
| **naive** | **1743** | 8 | all of `data/broken-python/**` |

- **Input-token reduction: 76.7%** `(1743 − 406) / 1743`.
- Comfortably clears the R4.1 bar (the eval asserts ≥ 50%).

Reproduce (no API key):

```bash
uv run pytest -m eval tests/evals/test_agent_context_delta.py   # asserts the >=50% reduction
# exact numbers:
uv run python -c "import sys; sys.path.insert(0,'src'); \
from ex04_graphify_agent.agent_workflow import config, context; \
from ex04_graphify_agent.graph_reader import GraphReader; \
from ex04_graphify_agent.weakness_detector import WeaknessDetector; \
v,_=context.read_vault_text(config.index_md_path(),config.hot_md_path()); \
bf=WeaknessDetector(GraphReader()).detect()[0].source_file; \
s=config.repo_path(bf).read_text(encoding='utf-8'); \
d,f=context.dump_repo_text(config.data_repo_root()); \
gg=context.count_tokens(v+s); nv=context.count_tokens(d); \
print(f'graph_guided={gg} naive={nv} reduction={100*(nv-gg)/nv:.1f}% naive_files={len(f)}')"
```

> Why this is fair: both routes share identical `plan/fix/report` nodes and the same
> gatekeeper instrumentation (`agent_workflow/graph_def.py`), so the *only* difference being
> measured is context strategy — curated vault vs raw dump (the "Lost in the Middle" control,
> [`pipeline.md`](pipeline.md)).

## Layer 2 — Full keyed run (PENDING owner action)

The complete R5.6.5 table — **output tokens, # LLM calls, iterations, duration, and
end-to-end correctness** from a real provider — requires one manual run. The keyless test
suite never triggers it (ADR-0005). When run, it **overwrites this file** with the
machine-rendered table from `token_comparison.report.render_report`, whose numbers come
straight from the gatekeeper's JSONL ledger (`artifacts/runs/*.jsonl`) and are
cross-checked against agent state (`_assert_logs_agree`, TC-E5).

**To produce it (see "What I need from you" in the PR/handoff):**

1. Set a model in [`config/agent.json`](../config/agent.json) — `"model"` is intentionally
   empty (D6: never hardcoded). E.g. `"model": "gemini-2.5-flash"`.
2. Export the key: `export GEMINI_API_KEY=...` (env-var name per `api_key_env`; never committed).
3. Run: `uv run python scripts/run_comparison.py`

Expected mandated columns (rendered, not hand-typed):

| Run | Input tok | Output tok | Total | Files read | Iterations | # LLM calls | Duration (s) | Correctness | Notes |
|---|---|---|---|---|---|---|---|---|---|
| graph_guided | _from log_ | _from log_ | _from log_ | _from log_ | _from log_ | _from log_ | _from log_ | _gate_ | hot.md + polygons.py only |
| naive | _from log_ | _from log_ | _from log_ | _from log_ | _from log_ | _from log_ | _from log_ | _gate_ | full data/broken-python/** dump |

Until then, this requirement is tracked **open** in `docs/KNOWN_LIMITATIONS.md`, and the
input-context reduction (Layer 1) stands as the keyless, reproducible evidence for R4.1.

## R4.2 — Accuracy cost of the savings

The savings do **not** cost accuracy. The graph-guided route reaches the same single root
cause (the half-finished `Polygon`) and its fix passes the 3-part correctness gate
([`root_cause.md`](root_cause.md)). The naive route receives the same information *plus*
noise; the open question the keyed run answers is whether that noise also degrades its
*fix* quality (the "Lost in the Middle" prediction), not whether graph-guided loses accuracy.
