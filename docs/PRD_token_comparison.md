# PRD: token_comparison.py (+ reports/ output)

> Runs the graph-guided vs naive baseline workflows, measures token usage from the
> gatekeeper's logs (not estimates — brief §6 EX04 additions, R10.5), checks the fix is
> correct, and emits `reports/token_comparison.md`. Also owns the PRE-FIX vs POST-FIX
> `graph.json` diff for R5.6.3.

---

## Purpose

Produce the evidence-based answer to R4.1/R4.2: does graph-guided navigation cut token
consumption vs a naive whole-repo dump, by how much, and at what cost to fix correctness
(R3.3, R5.6.2, R5.6.4, R7.8). All quantitative claims trace to a stored artifact
(R10.5).

## Inputs

- Two completed `AgentState`s (graph-guided + naive) from `agent_workflow/`, each with
  `token_usage: list[TokenRecord]` (per-node, populated by `gatekeeper.py`) and
  `fix_diff`.
- The gatekeeper per-call log (authoritative token source; `token_usage` mirrors it).
- The fixed `polygons.py` content (from each run's `fix_diff`) for the correctness check.
- For the graph diff: `artifacts/graphify/graph.json` (PRE-FIX baseline) and
  `artifacts/graphify_post_fix/graph.json` (POST-FIX, produced externally — see below).
- The chosen provider's API key (config-driven, likely `GEMINI_API_KEY`; D6) is required
  ONLY for the real-numbers run (manual, once); the test suite is keyless with mocked
  gatekeeper logs (ADR-0005).

## Outputs

- `reports/token_comparison.md` — the graded comparison report (table + narrative).
- A `ComparisonResult` object (also returned in-process for tests).
- `reports/graph_diff.md` (or a section) — the PRE-FIX vs POST-FIX structural diff
  (R5.6.3).

## What is measured (per R5.6.x / R7.8)

For **each** run (`graph_guided`, `naive`) — the first three groups below are the
**mandated §5.6 / R5.6.5 metrics** and must appear as explicit report columns:
- **(a) tokens** — total **input tokens** (sum of `TokenRecord.input_tokens`), total
  **output tokens**, total tokens;
- **(b) files / textual units read** — `files_read`: the count of distinct source files
  (and, where relevant, vault notes) that entered the LLM context across the run. For
  `graph_guided` this is small (index.md + hot.md + the single source-validated
  `polygons.py`); for `naive` it is the whole `data/broken-python/**` dump. **This is a
  required column, not implied by token counts** (R5.6.5 (b)).
- **(c) iterations / investigation rounds** — `iterations`: the number of
  hypothesize→validate→(re-hypothesize) rounds the agent took to reach the fix. For
  `graph_guided` this is the count of weakness-findings tried before source-validation
  confirmed one (≥1); for `naive` it is the dump→fix pass count (typically 1). **Required
  column** (R5.6.5 (c)).
- **(d) quality & speed of reaching root cause** — `correctness` (pass/fail, automated,
  see below) plus `duration_s` (wall-clock) and `iterations` together operationalize "how
  well and how fast each approach reached the root cause" (R5.6.5 (d)).
- supporting: **per-node breakdown** (from the gatekeeper per-call log — e.g.
  graph-guided's `fix` node vs naive's `fix` node) and **number of LLM calls**.

### Correctness check (automated, against the three TODO resolutions)
Load the fixed `polygons.py` and assert all three resolutions from brief §2:
1. **`calc_polygon_details` generalized (TODO@L18):** `calc_polygon_details(5)` →
   `internal_angles_sum == 540`, `internal_angle == 108` (pentagon);
   `calc_polygon_details(6)` → `internal_angles_sum == 720`, `internal_angle == 120`
   (hexagon). (Formulas: `sum = (sides-2)*180`, `each = sum/sides`.)
2. **`Polygon` class is valid + used (TODO@L33):** the module imports without `NameError`
   (`Object`→`object`) / `SyntaxError` (`new` removed), and `calc_polygon_details`
   returns/consumes a `Polygon` rather than a bare dict.
3. **`draw_polygon` generalized (TODO@L50):** with a **mocked turtle**, calling
   `draw_polygon` for a pentagon issues 5 `forward`/`right` iterations (not a hardcoded
   6) — assert the mocked-turtle `forward` call count equals `sides` and each turn is
   `360/sides`.

A run is `correctness == pass` only if all three hold.

## Public interface (sketch — signatures only, no implementation)

```python
from dataclasses import dataclass

@dataclass
class RunMetrics:
    run_type: str                 # "graph_guided" | "naive"
    input_tokens: int
    output_tokens: int
    total_tokens: int
    files_read: int               # R5.6.5 (b) — distinct files/textual units in context
    iterations: int               # R5.6.5 (c) — hypothesize→validate rounds (≥1)
    num_llm_calls: int
    duration_s: float
    correctness: bool
    per_node: list[dict]          # [{node, input_tokens, output_tokens}, ...]
    files_read_list: list[str]    # the actual paths counted by files_read (evidence)

@dataclass
class ComparisonResult:
    graph_guided: RunMetrics
    naive: RunMetrics
    input_token_reduction_pct: float    # answers R4.1
    correctness_delta: str              # answers R4.2

class TokenComparison:
    def __init__(self, agent_config: str = "config/agent.json") -> None: ...
    def metrics_from_state(self, state: "AgentState", duration_s: float,
                           fixed_source: str) -> RunMetrics: ...
    def check_correctness(self, fixed_source: str) -> bool: ...
    def compare(self, graph_guided: "AgentState", naive: "AgentState") -> ComparisonResult: ...
    def render_report(self, result: ComparisonResult) -> str: ...     # markdown
    def write_report(self, result: ComparisonResult,
                     path: str = "reports/token_comparison.md") -> str: ...

def diff_graphs(pre_fix: str, post_fix: str) -> "GraphDiff": ...       # R5.6.3
```

## Output artifact: `reports/token_comparison.md`

A markdown table (rows = runs, columns = metrics) plus a narrative:

```markdown
# Token Comparison — Graph-Guided vs Naive Baseline

| Run          | Input tok | Output tok | Total | Files read | Iterations | # LLM calls | Duration (s) | Correctness | Notes |
|--------------|-----------|------------|-------|-----------|-----------|-------------|--------------|-------------|-------|
| graph_guided | <n>       | <n>        | <n>   | <n>       | <n>       | <n>         | <n>          | pass/fail   | hot.md + polygons.py only |
| naive        | <n>       | <n>        | <n>   | <n>       | <n>       | <n>         | <n>          | pass/fail   | full data/broken-python/** dump |

> **Columns `Files read` and `Iterations` are mandated by R5.6.5 (PDF §5.6)** — not
> optional. `Files read` = distinct files/textual units that entered the LLM context;
> `Iterations` = hypothesize→validate rounds. Together with `Duration` and `Correctness`
> they answer §5.6's "quality and speed of reaching root cause" requirement (R5.6.5 (d)).

## R4.1 — Token reduction
Graph-guided used <X>% fewer input tokens than naive (<a> vs <b>), because the `fix`
node received only index.md + hot.md + polygons.py (~76 lines) instead of all 9 files
under data/broken-python/.

## R4.2 — Accuracy cost
Both runs produced a correctness=<pass/pass> fix / graph-guided passed while naive
<...> — token savings came at no cost to (or improved) localization.
```
Placeholder numbers are acceptable at PRD stage; real numbers come from the Phase-6
keyed run and are captured as a static artifact (ADR-0005, R10.5).

## PRE-FIX vs POST-FIX graph diff (R5.6.3)

- `artifacts/graphify_post_fix/graph.json` is produced by **re-running Graphify (an
  external black-box tool — out of scope per PRD.md)** on the fixed
  `data/broken-python/`. It is written to a **separate** directory so the PRE-FIX baseline
  under `artifacts/graphify/` is never overwritten (brief §6 EX04 additions).
- `diff_graphs(pre, post)` compares node count, edge count, communities, and confidence
  mix, and emits the diff into the report.
- **Falsifiable prediction to state in the PRD:** after the fix resolves the three TODOs,
  the three `rationale_*` nodes
  (`polygons_polygons_rationale_18`, `_33`, `_50`) **disappear** from the POST-FIX graph
  (they are `# TODO` rationale nodes; resolving the TODOs removes the comments). Net
  predicted change: nodes 23 → 20, Community 1 loses its three weakly-connected nodes,
  and the `Polygon` god node should now be *used* (a real `calls`/usage edge from
  `calc_polygon_details`/`draw_polygon` to `Polygon` rather than the dead class). This is
  concrete and checkable.

## Edge cases

- **TC-E1 (keyless).** No API key → tests run on fixture gatekeeper logs; the real-numbers
  path is a separate, manual, non-test script (ADR-0005).
- **TC-E2 (naive fix fails correctness).** If the naive run mislocates the bug ("Lost in
  the Middle") and fails the correctness check, the report must still render with
  `correctness=fail` and the narrative notes it (supports R4.2).
- **TC-E3 (post-fix graph absent).** If `artifacts/graphify_post_fix/graph.json` doesn't
  exist yet, `diff_graphs` fails loud / the report marks the diff section "pending
  re-run" — never fabricates a diff.
- **TC-E4 (zero-division on reduction %).** If naive input tokens == 0 (mock edge),
  reduction % must not divide-by-zero.
- **TC-E5 (token source authority).** Numbers must come from gatekeeper logs; if
  `token_usage` and the gatekeeper log disagree, fail loud (R10.5 — no estimates).

## Test cases (for TDD — Given/When/Then; keyless, fixture gatekeeper logs)

- **TC-T1 (table generation).** Given two fixture `AgentState`s with known
  `token_usage`, When `render_report(compare(...))`, Then the markdown contains a table
  with rows `graph_guided` and `naive` and the correct per-run input/output/total sums.
- **TC-T2 (R4.1 narrative).** Given fixture graph_guided input=1,200 and naive
  input=8,000 tokens, When `compare(...)`, Then `input_token_reduction_pct == 85.0` and
  the narrative states "85% fewer input tokens".
- **TC-T3 (R4.2 narrative).** Given both fixtures `correctness=True`, When `compare(...)`,
  Then `correctness_delta` states savings came at no accuracy cost.
- **TC-T4 (correctness pass).** Given a correctly-fixed `polygons.py`, When
  `check_correctness(src)`, Then returns `True` (pentagon 540/108, hexagon 720/120,
  mocked-turtle 5 sides for a pentagon).
- **TC-T5 (correctness fail).** Given the original broken `polygons.py` (else-branch
  1000/200, hardcoded 6-sided draw), When `check_correctness(src)`, Then returns `False`.
- **TC-T6 (per-node breakdown).** Given fixtures, When `metrics_from_state(...)`, Then
  `per_node` lists each node's input/output tokens (e.g. graph-guided `fix` node distinct
  from `report` node).
- **TC-T7 (graph diff prediction).** Given `artifacts/graphify/graph.json` (PRE, 23
  nodes) and a fixture POST-FIX graph with the three `rationale_*` nodes removed, When
  `diff_graphs(pre, post)`, Then the diff reports `nodes: 23 → 20` and lists
  `polygons_polygons_rationale_{18,33,50}` as removed.
- **TC-T8 (real-numbers path gated).** Given the configured provider key env var is unset
  (e.g. no `GEMINI_API_KEY`), When the manual real-run script is invoked, Then it exits with
  a clear "key required" message (the test suite never triggers this path — ADR-0005).
- **TC-T9 (mandated §5.6 columns present).** Given two fixture `AgentState`s where the
  graph-guided run touched 3 files/units (index.md, hot.md, polygons.py) over 1 validated
  iteration and the naive run dumped 9 files over 1 iteration, When
  `render_report(compare(...))`, Then the markdown table contains **both** a `Files read`
  column (3 vs 9) **and** an `Iterations` column (1 vs 1), and `RunMetrics.files_read` /
  `.iterations` are populated for each run (R5.6.5 (b)/(c)).
- **TC-T10 (files_read evidence list).** Given the graph-guided fixture, When
  `metrics_from_state(...)`, Then `files_read_list` equals the actual paths counted (so the
  number is auditable, not asserted — R10.5).

## Requirement traceability (ASSIGNMENT.md)

- **R5.6.1** — consumes the metric-derived `hot.md` (the graph-guided context).
- **R5.6.2** — measures both the graph-guided and naive baseline runs.
- **R5.6.3** — PRE-FIX vs POST-FIX `graph.json` diff (rationale-node disappearance
  prediction).
- **R5.6.4 / R7.8** — reports concrete input/output token + call-count numbers.
- **R5.6.5** — the report includes the mandated first-class columns: tokens (a),
  `files_read` (b), `iterations` (c), and correctness+duration as "quality & speed to root
  cause" (d).
- **R4.1** — quantifies the token reduction.
- **R4.2** — reports the accuracy/correctness cost (or gain) of that reduction.
- **R10.5** — every number is backed by a stored artifact (gatekeeper log →
  `reports/token_comparison.md`).

## Dependencies on other modules

- **Depends on:** `agent_workflow/` (drives both runs, supplies `AgentState`),
  `gatekeeper.py` (authoritative token log), `config/agent.json`, and the external
  Graphify tool (out of scope) for `artifacts/graphify_post_fix/graph.json`.
- **Depended on by:** `sdk.py` / `cli.py` (expose the comparison command); the README
  (R8.6) cites `reports/token_comparison.md`.
