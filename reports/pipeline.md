# Pipeline & Research-Question Answers (R5.5 / R4)

End-to-end story of how a knowledge graph turned a pile of source into a localized,
verified fix — plus direct answers to the assignment's research questions. Diagrams live in
[`diagrams.md`](diagrams.md); this page is the narrative.

## Inference-discipline legend (PART-C / R4.4)

Every graph-derived claim in these reports carries a confidence tag:

| Tag | Meaning | Language strength |
|---|---|---|
| **EXTRACTED** | Read directly from `graph.json` / source (a fact). | "is", "calls", "has degree 4" |
| **INFERRED** | Derived by a heuristic or metric; plausible, not certain. | "suggests", "may", "likely" |
| **AMBIGUOUS** | Cannot be settled from the graph alone; needs a human/source check. | "unclear", "requires validation" |

INFERRED/AMBIGUOUS claims are not actionable until a **source-validation** step confirms
them against `polygons.py`. (None of the 20 PRE-FIX edges are AMBIGUOUS; 2 are INFERRED.)

## The pipeline, stage by stage (R5.5.1) with inspectable artifacts (R5.5.2)

| # | Stage | Produces | Inspectable artifact | Confidence |
|---|---|---|---|---|
| 1 | **Source** | the bug | [`data/broken-python/polygons/polygons.py`](../data/broken-python/polygons/polygons.py) (now POST-FIX; PRE-FIX in git/clone) | — |
| 2 | **Graph (PRE-FIX)** | 23 nodes / 20 edges / 6 communities | [`artifacts/graphify/graph.json`](../artifacts/graphify/graph.json) + [`GRAPH_REPORT.md`](../artifacts/graphify/GRAPH_REPORT.md) + [Fig. 1](screenshots.md) | EXTRACTED |
| 3 | **Vault** | navigation layer | [`obsidian/index.md`](../obsidian/index.md), [`obsidian/hot.md`](../obsidian/hot.md) | EXTRACTED (rank metric disclosed) |
| 4 | **Agent (graph-guided)** | localized + validated hypothesis | LangGraph `read_vault→hypothesize→validate` ([`diagrams.md`](diagrams.md) §3) | INFERRED → EXTRACTED after validate |
| 5 | **Fix** | corrected source | [`reports/diff_polygons.md`](diff_polygons.md) (passes correctness gate) | EXTRACTED (executed + checked) |
| 6 | **Graph (POST-FIX)** | structural proof | [`artifacts/graphify_post_fix/graph.json`](../artifacts/graphify_post_fix/graph.json) + [Fig. 2](screenshots.md) | EXTRACTED |
| 7 | **Reports** | evidence | this `reports/` directory | — |

## How the root cause was found *via the graph* (R5.5.3)

Not by reading files top-to-bottom — by following graph signal:

1. **Start at `hot.md`.** Its #1 entry is `Polygon` (ranked by centrality × proximity-to-bug).
   The agent's `read_vault` node loads `index.md` + `hot.md` only — **not** raw source.
2. **Hypothesize (`weakness_detector`).** Signals 1/5/6 fire on the polygons subgraph and
   emit a primary hypothesis: *"the `Polygon` god node is the core abstraction but is unused;
   the dict in `calc_polygon_details` duplicates it."* Tagged INFERRED.
3. **Validate (the discipline step).** The `validate` node opens the file named by
   `current_hypothesis.source_file` (`polygons/polygons.py`) and confirms the dict-shadows-
   class structure → hypothesis becomes EXTRACTED, `validated = True`.
4. **Fix → Report.** The `fix` node edits only what the validated hypothesis points at.

This is the whole thesis: **the graph proposes, the source disposes.** Raw source is read
once, late, and narrowly — at validation — instead of being dumped up front.

## Six-signal → root-cause convergence (R4.5)

Three of the six PART-C signals independently point at the same place; the other three are
correctly quiet here. One root cause, multiple corroborating signals:

| Signal | Fires? | Evidence | Points at |
|---|---|---|---|
| 1 — God node | **Yes (primary)** | `Polygon` degree 4, top betweenness | the core abstraction |
| 2 — Ambiguous/INFERRED edge | minor | 2 INFERRED edges (0.8 / 0.9), both in mathsquiz/README | *not* the polygons bug (secondary) |
| 3 — Broken / missing path | elsewhere | `mathsquiz-final.py` node, file absent on disk | mathsquiz (out of scope) |
| 4 — Critical-path break | **Yes (secondary)** | no `sides >= 3` validation before `calc_polygon_details`/`draw_polygon` | the `ZeroDivisionError` guard (now fixed) |
| 5 — Isolated cluster | **Yes** | `rationale_{18,33,50}` (degree 1) from the 3 TODOs | the exact functions to fix |
| 6 — Semantic duplication | **Yes** | dict keys ≡ `Polygon` constructor params | the dead-class duplication |

Signals **{1, 5, 6} converge** on the *root cause* — `Polygon` + `calc_polygon_details`; the
fix resolves all three at once, which is why the POST-FIX graph loses the rationale nodes
*and* gains the `calls→Polygon` edge ([`graph_diff.md`](graph_diff.md)). **Signal 4** is a
distinct, secondary defect on the same critical path (missing `sides >= 3` validation) — it
was initially deferred as "minor" but a code review correctly flagged that it crashes
(`ZeroDivisionError` at `sides=0`) on the live `input()` path, so the fix now raises
`ValueError` for `sides < 3` (see [`diff_polygons.md`](diff_polygons.md) #7,
[`oop_improvement.md`](oop_improvement.md)).

## Research questions

### R4.3 — Do "God Nodes" reveal core abstractions / coupling?

**Yes, decisively here.** The single highest-degree node (`Polygon`, degree 4) *was* the
intended core abstraction — and its graph neighbourhood (a `contains` edge from the module, a
`method` edge to `__init__`, an `inherits` edge, and the would-be usage from
`calc_polygon_details`) is exactly the coupling surface where the bug lived. Ranking by
degree took us to the right ~25 lines of a 76-line file without reading the rest. A god node
is "where the design's weight sits", so it is the highest-yield place to look first.

### R4.6 — How did Obsidian help?

The vault converts the graph into a *navigable reading order*. `hot.md` answers "where do I
look first?" (Polygon), and wikilinks let you walk Polygon → `calc_polygon_details` →
`draw_polygon` — the precise edit set — by clicking, never scrolling source. The graph-guided
agent automates this exact traversal. (Screenshots + detail in
[`screenshots.md`](screenshots.md).)

### R4.7 — AI usage, and where the agent diverged from a human

Full AI-usage disclosure is in [`docs/PROMPTS.md`](../docs/PROMPTS.md). Where the **agent**
diverges from a **human** debugger:

- A human skims the file top-to-bottom and often fixes the *first* error they hit (the
  `NameError` on line 3), symptom by symptom. The agent instead ranks by graph centrality and
  goes to the *structurally* most important node first, so it frames the dict-vs-class
  duplication as the **root cause** rather than patching five symptoms independently.
- A human "just knows" `Object` should be `object`; the agent must *validate* each INFERRED
  claim against source before acting (the discipline step) — slower per step, but it makes
  every claim auditable (the EXTRACTED/INFERRED tags above).

## Why the naive baseline is the right control — "Lost in the Middle" (R1.4 / ADR-0004)

The naive route (`plan → dump_repo → fix → report`, [`diagrams.md`](diagrams.md) §4) dumps
**all** of `data/broken-python/**` into the prompt. That reproduces the "Lost in the Middle"
failure mode from PART-B: with the relevant 25 lines buried in the middle of multiple files,
attention degrades and token cost balloons. It shares the identical `plan/fix/report` nodes
and the same gatekeeper instrumentation as the graph-guided route, so the **only** variable
is context strategy (curated vault vs raw dump). The measured cost of that difference is in
[`token_comparison.md`](token_comparison.md).
