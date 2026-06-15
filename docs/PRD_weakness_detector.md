# PRD: weakness_detector.py

> The six PART-C signals → bug-class hypotheses. Each hypothesis carries an
> Observe → Relation → Confidence → Context → Source-validation trail (brief §5). Tags
> and language strength are locked: `EXTRACTED` states facts, `INFERRED` suggests,
> `AMBIGUOUS` = manual check required. All node ids/labels below are real, from
> `artifacts/graphify/graph.json`.

---

## Purpose

Turn the graph's structure into a ranked list of falsifiable bug hypotheses without
reading source first. It runs the six PART-C weakness signals (brief §5) over the
`GraphReader` queries, emits one `WeaknessFinding` per triggered signal, and tags each
with the correct confidence vocabulary so downstream `agent_workflow/` knows whether a
finding is fact (act on it), a suggestion (validate it), or ambiguous (manual check).
The detector *proposes* hypotheses; only a later source-read (in `agent_workflow`'s
`validate` node) promotes a hypothesis to a conclusion (R4.5, R5.2.1, R5.2.2).

## Inputs

- A constructed `GraphReader` (injected; the only graph access path).
- Thresholds from `config/weakness_thresholds.json` (config-driven, no hardcoded values).
  Default schema:
  ```json
  {
    "god_node_min_degree": 4,
    "ambiguous_confidence_max": 0.85,
    "isolated_cluster_max_edges": 1,
    "semantic_duplicate_min_score": 0.75,
    "missing_path_check": true
  }
  ```
  - `god_node_min_degree` — Signal 1 trigger (Polygon's degree 4 meets it).
  - `ambiguous_confidence_max` — Signal 2: INFERRED edges with `confidence_score` ≤ this
    are flagged "open source_file first".
  - `isolated_cluster_max_edges` — Signal 5: nodes whose degree ≤ this and that lack a
    `tested_by` edge form an isolated/dead cluster.
  - `semantic_duplicate_min_score` — Signal 6 similarity floor (note: this graph has no
    `similar_to` edge for the dict/class duplication — see Behavior §6 + Edge cases).
- For **Signal 6 only**, the detector additionally needs to read `source_file`
  (`polygons/polygons.py`) even to *hypothesize* — see edge case WD-E1.

## Outputs

- `list[WeaknessFinding]`, one per triggered signal, ranked (primary fix first). Each:
  - `signal: int` (1–6, per brief §5).
  - `nodes: list[str]` / `edges: list[tuple[str, str]]` — the real node ids / edge
    endpoints involved.
  - `tag: Literal["EXTRACTED", "INFERRED", "AMBIGUOUS"]`.
  - `hypothesis: str` — human-readable; **language strength must match `tag`**:
    EXTRACTED → "states" / "is"; INFERRED → "suggests" / "may"; AMBIGUOUS → "unclear —
    manual check required".
  - `priority: Literal["primary", "secondary"]`.
  - `source_file: str` — the file to validate against (e.g. `polygons/polygons.py`).
  - `source_validation: SourceValidation | None` — **initially `None` (pending)**;
    filled by `agent_workflow`'s `validate` node after reading `source_file`.

## Public interface (sketch — signatures only, no implementation)

```python
from dataclasses import dataclass
from typing import Literal

Tag = Literal["EXTRACTED", "INFERRED", "AMBIGUOUS"]
Priority = Literal["primary", "secondary"]

@dataclass
class SourceValidation:
    confirmed: bool
    note: str

@dataclass
class WeaknessFinding:
    signal: int
    tag: Tag
    hypothesis: str
    priority: Priority
    source_file: str
    nodes: list[str]
    edges: list[tuple[str, str]]
    source_validation: SourceValidation | None = None

class WeaknessDetector:
    def __init__(self, reader: "GraphReader", thresholds_path: str =
                 "config/weakness_thresholds.json") -> None: ...

    def detect(self) -> list[WeaknessFinding]: ...        # runs all six, ranked
    def signal_1_god_node(self) -> list[WeaknessFinding]: ...
    def signal_2_ambiguous_edge(self) -> list[WeaknessFinding]: ...
    def signal_3_broken_path(self) -> list[WeaknessFinding]: ...
    def signal_4_critical_path_break(self) -> list[WeaknessFinding]: ...
    def signal_5_isolated_cluster(self) -> list[WeaknessFinding]: ...
    def signal_6_semantic_duplicate(self) -> list[WeaknessFinding]: ...
```

## Behavior / algorithm

Ranking: **primary** findings (Signals 1, 5, 6 — these *are* the polygons.py bug) sort
above **secondary** findings (Signals 2, 3, 4 — mathsquiz-community noise / minor). Within
a priority band, higher degree / lower confidence first.

### Signal 1 — God node / bottleneck (EXTRACTED, primary)
- Rule: any node with `degree >= god_node_min_degree` (default 4).
- Fires on `polygons_polygons_polygon` (**Polygon**, degree 4 — highest in the graph,
  bridges Community 4 `{Polygon, object, .__init__(), calc_polygon_details()}` and
  Community 1 `{polygons.py, draw_polygon(), 3 rationale TODOs}`).
- Hypothesis (EXTRACTED language): *"`Polygon` (`polygons_polygons_polygon`) **is** the
  highest-degree node (degree 4) and **bridges** Community 4 and Community 1 — it is the
  core abstraction and the first place to investigate."*

### Signal 2 — Ambiguous / inferred edge (INFERRED, secondary)
- Rule: `reader.edges_with_confidence("INFERRED")`, flag those with `confidence_score <=
  ambiguous_confidence_max`.
- Fires on the two INFERRED edges, primarily
  `mathsquiz_readme_maths_quiz --conceptually_related_to--> readme_broken_python`
  (score 0.9) and `mathsquiz_mathsquiz_final_py --semantically_similar_to-->
  mathsquiz_mathsquiz` (score 0.8).
- Hypothesis (INFERRED language): *"The graph **suggests** `Maths Quiz Documentation`
  **may** be conceptually related to `Broken Python Project`; open `source_file`
  (mathsquiz/README.md) to confirm before treating as fact. Secondary — not the primary
  fix."*

### Signal 3 — Broken / missing path (EXTRACTED about the edge, but flags a gap; secondary)
- Rule: a node referenced by an EXTRACTED edge whose `source_file` does not exist on disk
  under `data/broken-python/`.
- Fires on `mathsquiz_mathsquiz_final_py` (**mathsquiz-final.py**): referenced by
  `mathsquiz_readme_maths_quiz --references--> mathsquiz_mathsquiz_final_py` (EXTRACTED),
  but `data/broken-python/mathsquiz/mathsquiz-final.py` does not exist (only
  `mathsquiz.py`, `mathsquiz-step1/2/3.py`).
- Hypothesis: *"`mathsquiz-final.py` **is** referenced by the mathsquiz README but the
  file **is** absent on disk — a PRD→code gap in the mathsquiz community. Secondary, not
  the primary fix."*

### Signal 4 — Critical-path break (INFERRED, secondary)
- Rule: a code node that performs computation/drawing with no preceding validation node /
  guard edge.
- Fires (weakly) on `polygons_polygons_calc_polygon_details` /
  `polygons_polygons_draw_polygon`: no `sides >= 3` validation exists before they run.
- Hypothesis (INFERRED language): *"`polygons.py` **may** lack a `sides >= 3` guard before
  `calc_polygon_details` / `draw_polygon`; mention in the OOP-improvement summary, not a
  blocking fix. Secondary."*

### Signal 5 — Isolated cluster / dead-untested code (EXTRACTED, primary)
- Rule: nodes with `degree <= isolated_cluster_max_edges` (default 1) and no `tested_by`
  edge, grouped by community.
- Fires on the three Community-1 rationale nodes
  `polygons_polygons_rationale_18` (*# TODO: find a better way to work this stuff out*),
  `polygons_polygons_rationale_33` (*# TODO: perhaps I should use the class Polygon
  instead!*), `polygons_polygons_rationale_50` (*# TODO: make this work for any type of
  polygon*) — each has exactly 1 edge (`rationale_for → polygons_polygons`).
- Hypothesis: *"Three weakly-connected `rationale_*` TODO nodes in Community 1 **are** the
  developer's own notes describing the incompleteness — they **are** the bug. Primary."*

### Signal 6 — Semantic duplicate (AMBIGUOUS → resolved by source-read; primary)
- **Noteworthy edge case:** there is **no `similar_to` / `semantically_similar_to` edge
  in `graph.json` for the polygons duplication** (the only semantic-similarity edge is in
  the mathsquiz community). So the detector **cannot** derive Signal 6 from graph edges
  alone for the real bug. Instead it derives it structurally + by a source-read:
  1. Observe that Community 4 holds both `polygons_polygons_polygon_init` (`.__init__()`,
     the `Polygon` data fields) and `polygons_polygons_calc_polygon_details`
     (`calc_polygon_details()`), both in `polygons/polygons.py`.
  2. Read `source_file` (`polygons/polygons.py`) and compare the `Polygon.__init__`
     field names against the dict literal keys returned by `calc_polygon_details()`:
     both carry `sides`, `internal_angles_sum`, and the near-identical
     `internal_angle(s)` field — a drifted duplicate (one used = the dict, one dead = the
     class). TODO@L33 names this explicitly.
- Because hypothesizing requires the source-read, the finding is tagged **AMBIGUOUS** until
  that read, then upgraded.
- Hypothesis (AMBIGUOUS language, pre-read): *"`calc_polygon_details()`'s returned dict
  **may** duplicate the unused `Polygon` class's fields — unclear from the graph alone;
  manual source check of `polygons/polygons.py` required."*

> **Discipline note (brief §5):** Signal 6 is the clearest illustration of "the graph
> proposes; only `source_file` concludes" — call this out in the OOP-improvement summary.

## Edge cases

- **WD-E1 (Signal 6 needs a source-read to even hypothesize).** Unlike Signals 1–5, which
  are graph-only, Signal 6 has no backing edge in this `graph.json`; the detector must
  read `polygons/polygons.py` to form the hypothesis at all. Document this as the one
  signal that breaks the "graph-only hypothesis" assumption.
- **WD-E2 (no AMBIGUOUS edges in graph).** Signal 2 must not crash on a graph with 0
  AMBIGUOUS edges; it works off INFERRED + threshold.
- **WD-E3 (duplicate labels).** Community 4's `.__init__()` and `calc_polygon_details()`
  must be addressed by `id`, never `label` (labels repeat across mathsquiz steps).
- **WD-E4 (missing file probe for Signal 3).** The on-disk existence check must resolve
  paths relative to `data/broken-python/`, not the repo root, and must not raise if the
  whole `mathsquiz/` dir is absent — it returns the finding either way.
- **WD-E5 (empty thresholds / missing config).** Missing `config/weakness_thresholds.json`
  → fail loud with a clear error (no silent defaults baked in code, per CLAUDE.md).

## Test cases (for TDD — Given/When/Then; run against the REAL graph.json)

- **WD-T1 (Signal 1 god node).** Given `GraphReader(artifacts/graphify/graph.json)`, When
  `signal_1_god_node()`, Then a finding with `signal==1`, `tag=="EXTRACTED"`,
  `priority=="primary"`, and `"polygons_polygons_polygon" in finding.nodes`; hypothesis
  text contains "Polygon" and uses "is"/"bridges" (not "may").
- **WD-T2 (Signal 5 isolated cluster).** Given the graph, When `signal_5_isolated_cluster()`,
  Then a finding whose `nodes` == `{polygons_polygons_rationale_18,
  polygons_polygons_rationale_33, polygons_polygons_rationale_50}`, `tag=="EXTRACTED"`,
  `priority=="primary"`.
- **WD-T3 (Signal 2 inferred edge, secondary).** Given the graph, When
  `signal_2_ambiguous_edge()`, Then ≥1 finding with `tag=="INFERRED"`,
  `priority=="secondary"`, referencing the
  `mathsquiz_readme_maths_quiz→readme_broken_python` edge; hypothesis uses "suggests"/"may".
- **WD-T4 (Signal 3 missing file).** Given the graph and a `data/broken-python/` tree with
  no `mathsquiz/mathsquiz-final.py`, When `signal_3_broken_path()`, Then a finding
  referencing `mathsquiz_mathsquiz_final_py`, `priority=="secondary"`.
- **WD-T5 (Signal 6 requires source-read).** Given the graph plus
  `polygons/polygons.py`, When `signal_6_semantic_duplicate()`, Then a finding with
  `signal==6` referencing `polygons_polygons_polygon_init` and
  `polygons_polygons_calc_polygon_details`; pre-read `tag=="AMBIGUOUS"` and hypothesis
  contains "manual ... check"; AND the detector demonstrably opened `polygons/polygons.py`
  (assert the file read occurred / fields compared).
- **WD-T6 (ranking).** Given the graph, When `detect()`, Then the first finding has
  `priority=="primary"` and is one of Signals {1,5,6}; all mathsquiz-community findings
  (Signals 2,3) are `priority=="secondary"` and rank below.
- **WD-T7 (language ↔ tag invariant).** Given any finding from `detect()`, Then EXTRACTED
  findings contain no hedging words ("may"/"suggests"), INFERRED findings contain a
  hedge, and AMBIGUOUS findings contain "manual check required".
- **WD-T8 (source_validation pending).** Given `detect()` output, Then every finding has
  `source_validation is None` (validation is `agent_workflow`'s job, not the detector's).

## Requirement traceability (ASSIGNMENT.md)

- **R4.3** — Signal 1 surfaces the God Node (`Polygon`) → core abstraction + coupling risk.
- **R4.5** — Signals collectively localize the **root cause** (the half-finished `Polygon`
  / dict duplication / un-generalized functions), not a symptom.
- **R5.2.1** — graph-driven understanding precedes any code change (detector reads the
  graph, not blind files — except the one disclosed Signal-6 source-peek).
- **R5.2.2** — produces the documented root-cause hypothesis that the fix resolves.

## Dependencies on other modules

- **Depends on:** `graph_reader.GraphReader` (all signals query through it);
  `config/weakness_thresholds.json`; for Signal 6 only, read access to
  `data/broken-python/polygons/polygons.py`.
- **Depended on by:** `agent_workflow/` — the `hypothesize` node calls `detect()`, and the
  `validate` node fills in each finding's `source_validation`.
