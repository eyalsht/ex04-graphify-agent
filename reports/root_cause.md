# Root-Cause Narrative — `polygons/polygons.py` (R4.5 / R5.2.2 / R7.7)

## One root cause, not five bugs

`polygons/polygons.py` looks like it has a handful of unrelated defects — a `NameError`, a
`SyntaxError`, a wrong-answer branch, a hardcoded drawing loop. It does not. They are all
**symptoms of a single root cause**:

> **The `Polygon` class was started as the program's central abstraction and then
> abandoned half-finished, so every downstream computation re-implements, by hand, the state
> that `Polygon` was supposed to own.**

The author left three `TODO:` breadcrumbs admitting exactly this — most tellingly
`# TODO: perhaps I should use the class Polygon instead!` (L33), written right above a
hand-built dictionary that duplicates the class. The graph found the same thing without
reading the comments (see "How the graph pointed here" below).

## How the graph pointed here (R5.5.3)

The agent did not start by reading source. It started at
[`obsidian/hot.md`](../obsidian/hot.md), whose top entry — ranked by centrality ×
proximity-to-bug — is `[[polygons_polygons_polygon|Polygon]]`:

1. **Signal 1 (god node).** `Polygon` has the highest degree (4) and betweenness in the
   graph: it is the core abstraction. **EXTRACTED** from `graph_reader.degree`. A god node is
   where coupling concentrates, so it is where a structural bug is most likely to hurt.
2. **Signal 5 (isolated cluster — the uncertainty markers).** Three `rationale` nodes
   (`polygons_polygons_rationale_{18,33,50}`), each degree 1, hang off the polygons subgraph
   — extracted from the three `TODO:` comments. They cluster on exactly the functions that
   compute polygon state.
3. **Signal 6 (semantic duplication).** `calc_polygon_details` returns a `dict` whose keys
   (`sides`, `internal_angles_sum`, `internal_angles`) mirror `Polygon`'s constructor
   parameters — the same concept expressed twice.

Signals {1, 5, 6} converge on one place: the `Polygon` class and the function that should
build it. The agent then ran the **inference discipline** — opened
`data/broken-python/polygons/polygons.py` (the `Validate` node) and confirmed the INFERRED
hypothesis against source, turning it EXTRACTED. The convergence is summarized in
[`pipeline.md`](pipeline.md).

## The five symptoms, traced to the one cause

Each symptom is what happens *because* `Polygon` was never finished:

1. **`class Polygon(Object)` → `NameError`.** Python's base object is lowercase `object`;
   `Object` is undefined. The class header itself never ran — a strong tell that nothing ever
   instantiated it. **Fix:** `class Polygon(object)`.

2. **`poly = new Polygon(...)` → `SyntaxError`.** `new` is a Java/JavaScript keyword; in
   Python the constructor is called directly. Because the file never parsed, this line had
   never executed either. **Fix:** `poly = Polygon(...)` (and the throwaway `print(poly)` is
   dropped).

3. **Hardcoded angle table with a nonsense `else` (1000° / 200°).** `calc_polygon_details`
   special-cases triangle and square and returns garbage for everything else — a placeholder
   the author meant to replace (`TODO@L18`). The real relationship is the standard formula:
   internal-angle sum = `(sides - 2) * 180`, each interior angle = `sum / sides`. **Fix:**
   replace the branch with the formula (pentagon → 540/108, hexagon → 720/120, verified by
   the correctness gate).

4. **A `dict` shadows the class (the actual root cause).** `calc_polygon_details` builds a
   `Polygon(...)` instance, **prints it, throws it away**, and returns a hand-built `dict`
   instead. So `Polygon` is *defined but dead*, and the program threads a dict everywhere the
   class should live (`TODO@L33`). **Fix:** return the `Polygon` instance; delete the dict.
   This is the edit that makes the other fixes cohere — once `Polygon` is the single source
   of truth, callers read `polygon.sides` instead of `details["sides"]`.

5. **`draw_polygon` hardcodes a hexagon.** `for i in range(0, 6): ... t.right(60)` draws six
   sides regardless of input (`TODO@L50`). Once a `Polygon` object flows in, the loop can ask
   it: `for i in range(0, polygon.sides): ... t.right(360 / polygon.sides)`. **Fix:** drive
   the loop from `polygon.sides`.

Symptoms 1–2 are *blocking* (the file will not even parse/run). Symptoms 3–5 are *latent*
(they produce wrong output once it does run). All five disappear the moment `Polygon` is
finished and actually used.

## Verification (not a claim — a gate)

The POST-FIX source is checked by `token_comparison.correctness.check_correctness`, which
asserts three independent properties against an *executed* copy of the module (mocked
`turtle`/`input`):

- **Angle formula:** `calc_polygon_details(5)` → (540, 108), `(6)` → (720, 120).
- **Polygon usage:** `calc_polygon_details(5)` returns an `isinstance(..., Polygon)`.
- **Generalized draw:** `draw_polygon(pentagon)` issues exactly 5 `forward`/`right` calls,
  each turning `360/5`.

PRE-FIX source fails immediately (`SyntaxError` on `new Polygon(...)`); POST-FIX returns
`True`. This gate is what the agent's `Validate`→`Fix` loop optimizes toward, and it is what
makes the "graph-guided run reached the correct fix" claim in
[`token_comparison.md`](token_comparison.md) checkable rather than asserted.

## See also

- [`diff_polygons.md`](diff_polygons.md) — the literal before/after diff, change-by-change.
- [`graph_diff.md`](graph_diff.md) — PRE/POST graph structure (rationale nodes removed,
  `Polygon` gains an inbound `calls` edge).
- [`oop_improvement.md`](oop_improvement.md) — why "finish the class" is the right OOP move.
- [`pipeline.md`](pipeline.md) — repo → graph → vault → agent → fix, end to end.
