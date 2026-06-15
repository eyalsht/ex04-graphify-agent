# ADR-0003: Target repo = `martinpeck/broken-python`, target bug = `polygons/polygons.py`

## Status
Accepted

## Context
R2.1 lists three approved source repositories (`soarsmu/BugsInPy`,
`martinpeck/broken-python`, `andela/buggy-python`) and requires picking exactly one; R2.2
requires the README to **document which repo was chosen and why**. R5.2.2 requires
identifying and fixing at least one real bug with a documented **root cause** (not a
symptom), R4.5 requires showing **how the graph helped find that root cause**, and R3.4 /
R5.2.3 require **OOP improvements** as part of the fix. The repo/bug choice must therefore
support not just "a bug" but a single, graph-locatable root cause that also has room for an
OOP refactor.

We chose `martinpeck/broken-python` and, within it, the file
`data/broken-python/polygons/polygons.py` (a 76-line vendored copy). A pre-fix Graphify run
already exists for this repo (`artifacts/graphify/graph.json`, `GRAPH_REPORT.md`), and it
points directly and unusually cleanly at this file — which is the strongest evidence for
the choice (the six-signal table below).

## Decision
**Target repo:** `martinpeck/broken-python`. **Target bug:** `polygons/polygons.py`.

### Root-cause analysis (single root cause, per R5.2.2 / R4.5)
The script was left in a **half-finished state**. The author began a `Polygon` class to
hold a polygon's geometry but never finished wiring it in:
- `class Polygon(Object):` — `Object` is undefined (Python's built-in is lowercase
  `object`; capital `Object` does not exist), a `NameError` at class-definition time.
- `poly = new Polygon(...)` (L29) — `new` is not Python (a Java/C++ habit), a `SyntaxError`,
  so the module cannot even be imported.
- Because the class was never wired in, `calc_polygon_details()` instead returns a
  hand-rolled `dict` with `sides` / `internal_angles_sum` / `internal_angles` keys —
  duplicating the very fields `Polygon` was meant to hold (TODO@L33: *"perhaps I should use
  the class Polygon instead!"*).
- `calc_polygon_details(sides)` (L13-36) only computes correct values for `sides == 3`
  (sum=180, each=60) and `sides == 4` (sum=360, each=90); the `else` branch hardcodes
  `sum=1000, each=200` for **any other polygon** — wrong for all pentagons, hexagons, etc.
  (TODO@L18: *"find a better way to work this stuff out"*). Correct general formulas:
  `internal_angles_sum = (sides - 2) * 180`, `internal_angle = internal_angles_sum / sides`.
- `draw_polygon(polygon_details)` (L41-54) **ignores** `polygon_details["sides"]` entirely —
  it hardcodes `for i in range(0, 6): t.forward(50); t.right(60)`, i.e. always draws a
  hexagon regardless of the requested polygon (TODO@L50: *"make this work for any type of
  polygon"*). Correct general version: `for i in range(sides): t.forward(50); t.right(360 /
  sides)`.

The fix (the before/after deliverable, R5.2.4 / R7.6): (1) make `Polygon` valid and
actually used; (2) generalize `calc_polygon_details` with the correct formulas for arbitrary
`sides >= 3`; (3) generalize `draw_polygon` to honour `sides`; (4) the OOP improvement
(R3.4 / R5.2.3) makes `Polygon` the single source of truth, folding `calc_polygon_details`
into a constructor/classmethod and removing the duplicated dict.

### How the graph points here (the six-signal mapping, PART-C)

| Signal (PART-C) | Evidence in `artifacts/graphify/graph.json` | What it means here |
|---|---|---|
| 1. God node / bottleneck | `Polygon` (`polygons_polygons_polygon`) has degree 4 — highest in the graph (GRAPH_REPORT.md "God Nodes" #1) — bridges Community 4 (`Polygon`, `object`, `.__init__()`, `calc_polygon_details()`) and Community 1 (`polygons.py`, `draw_polygon()`, the 3 TODO rationale nodes) | Investigate this node first — it's both the most-referenced abstraction AND (per source) currently broken/unused |
| 2. Ambiguous/inferred edge | `mathsquiz_readme_maths_quiz --conceptually_related_to--> readme_broken_python` (INFERRED, confidence 0.9); `mathsquiz_mathsquiz_final_py --semantically_similar_to--> mathsquiz_mathsquiz` (INFERRED, confidence 0.8) | Secondary example only — open `source_file` to confirm before treating as fact |
| 3. Broken/missing path | `mathsquiz-final.py` is a graph node (referenced by `mathsquiz/README.md`, `references` EXTRACTED edge) but **the file does not exist** in `data/broken-python/mathsquiz/` (only `mathsquiz.py`, `mathsquiz-step1/2/3.py` exist) | Secondary/optional test fixture for weakness_detector — documents a PRD→code gap in the *mathsquiz* community, not the primary fix |
| 4. Critical-path break | `polygons.py` has no validation that `sides >= 3` before calling `calc_polygon_details`/`draw_polygon` | Minor; mention in OOP-improvement summary, not a blocking fix |
| 5. Isolated cluster | Community 1's three `rationale_*` nodes (`# TODO: find a better way...`, `# TODO: perhaps I should use the class Polygon...`, `# TODO: make this work for any type of polygon`) are weakly connected (each has exactly 1 edge — `rationale_for` → `polygons.py`) per GRAPH_REPORT.md "Knowledge Gaps" | These three TODOs **are** the bug — the developer's own notes describing exactly the incompleteness above |
| 6. Semantic duplicate | `calc_polygon_details()`'s returned dict (`sides`, `internal_angles_sum`, `internal_angles`) duplicates the fields of the unused `Polygon` class (`sides`, `internal_angles_sum`, `internal_angle`) | TODO@L33 names this explicitly — "two impls", one (dict) used, one (class) dead |

The `mathsquiz-final.py` broken/missing-path finding (signal 3) is why `mathsquiz/` is
still worth including in the graph and vault even though it is **not** the primary fix
target: it is a clean secondary demonstration of a PRD→code gap for the weakness detector.

## Consequences
- **Enables R4.5 / R5.5.3:** the graph already, demonstrably, localizes the root cause — the
  agent's graph-first reasoning is illustrated end-to-end on `Polygon`.
- **Enables R3.4 / R5.2.3 / R7.7:** the dead `Polygon` class + duplicated dict gives a real,
  graph-suggested OOP refactor, not a contrived one.
- **No special environment** (R6.1.6 / R6.2.3 N/A): broken-python runs as plain scripts; no
  Docker/virtualenv needed for reproducibility.
- **Constrains** the fix scope to the four documented items above (keeps the before/after
  diff focused and reviewable, R5.2.4).
- **Implies work:** Phase 4 generates `hot.md` centred on `Polygon`; Phase 5-6 run the
  agent against `data/broken-python/polygons/polygons.py`; Phase 6 captures the before/after
  `graph.json` diff (R5.6.3). See `docs/TODO.md` Phase 4-6.

## Alternatives Considered
- **`soarsmu/BugsInPy`** — *Rejected.* Heavier setup (Docker/virtualenv per R6.1.6) for a
  project whose focus is the graph/agent layer, not environment reproduction. Its much
  larger graph would also risk **burying** the "Lost in the Middle" demonstration in noise
  rather than illustrating it cleanly on a compact, comprehensible graph.
- **`andela/buggy-python`** — *Rejected.* No Graphify run exists for it, so we would lose the
  already-vendored pre-fix baseline. By contrast, broken-python's small, single-file,
  multi-bug `polygons.py` is uniquely suited to demonstrating **all six PART-C signals in
  one place** — a pedagogical advantage no other candidate offers.
- **Fixing `mathsquiz.py` instead (within broken-python)** — *Rejected.* `mathsquiz.py` is
  Python-2-syntax broken at the **parse level across its entire body** (`print "..."`, `if
  answer = 55`, `else if`), so "the bug" would really be "rewrite the whole file." That
  doesn't demonstrate graph-guided **root-cause localization** (R4.5) as cleanly as
  `polygons.py`'s three precisely TODO-flagged, graph-highlighted issues.
