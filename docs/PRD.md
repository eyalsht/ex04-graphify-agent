# PRD — EX04: Graphify + Obsidian Reverse-Engineering Agent

> **Status:** Draft for project owner review.
> **Scope:** This is the top-level Product Requirements Document. Mechanism-level detail is
> deferred to the four sub-PRDs (`PRD_graph_reader.md`, `PRD_weakness_detector.md`,
> `PRD_agent_workflow.md`, `PRD_token_comparison.md`) and to the ADRs under `docs/adr/`.
> Every section cites the `docs/ASSIGNMENT.md` requirement IDs (R#.#) it covers.

---

## 1. Summary

This project builds a **graph-guided LangGraph agent** that locates, explains, and fixes a
real, single-root-cause bug in `martinpeck/broken-python`'s `polygons/polygons.py`. Rather
than dumping the unfamiliar repository into an LLM context window, the agent navigates a
**pre-generated Graphify knowledge graph** (`artifacts/graphify/graph.json` +
`GRAPH_REPORT.md`) surfaced through an **Obsidian vault** (`index.md` + a to-be-produced
`hot.md`) as its primary context, reading source files only on demand to validate
hypotheses. The deliverable **proves measurable token savings** by running the same fix
task twice — once graph-guided, once with a naive dump-all-files baseline — and reporting
input/output token counts, call counts, and whether each run reaches the same root cause.
This demonstrates the core thesis (R1.4) that a compressed, prioritized graph "map" avoids
the *"Lost in the Middle"* failure mode while preserving or improving bug-localization
accuracy.
*Covers:* R1.1, R1.2, R1.3, R1.4, R1.5.

---

## 2. Chosen repo + bug + why

**Chosen repo:** `martinpeck/broken-python` — small, intentionally broken/incomplete Python
scripts for debugging practice; needs no Docker/virtualenv (unlike `soarsmu/BugsInPy`).
Selection and the rejected alternatives (`soarsmu/BugsInPy`, `andela/buggy-python`) are
recorded in **ADR-0003**. The chosen repo and the rationale are documented here and in the
README per R2.2.
*Covers:* R2.1, R2.2.

**Target file:** `data/broken-python/polygons/polygons.py` (vendored copy, 76 lines).

**Root cause (single root cause, per R5.2.2 / R4.5):** the script was left half-finished.
The author began a `Polygon` class to hold a polygon's geometry but never wired it in:

- `class Polygon(Object):` — `Object` is undefined (the built-in is lowercase `object`);
  capital `Object` does not exist → `NameError` at class-definition time.
- `poly = new Polygon(...)` (L29) — `new` is not Python (a Java/C++ habit) →
  `SyntaxError`, so the file cannot even be imported.
- Because the class was never used, `calc_polygon_details()` instead returns a hand-rolled
  `dict` with `sides` / `internal_angles_sum` / `internal_angles` keys — duplicating the
  fields the `Polygon` class was meant to hold (**TODO@L33:** "perhaps I should use the
  class Polygon instead!").
- `calc_polygon_details(sides)` (L13–36) computes correct values only for `sides == 3`
  (sum=180, each=60) and `sides == 4` (sum=360, each=90); the `else` branch hardcodes
  `sum=1000, each=200` for **any other polygon** — wrong for all pentagons, hexagons, etc.
  (**TODO@L18:** "find a better way to work this stuff out"). Correct general formulas:
  `internal_angles_sum = (sides - 2) * 180`, `internal_angle = internal_angles_sum / sides`.
- `draw_polygon(polygon_details)` (L41–54) **ignores** `polygon_details["sides"]` — it
  hardcodes `for i in range(0, 6): t.forward(50); t.right(60)`, always drawing a hexagon
  (**TODO@L50:** "make this work for any type of polygon"). Correct general version:
  `for i in range(sides): t.forward(50); t.right(360 / sides)`.

**Fix scope (the before/after deliverable, R5.2.4 / R7.6):**
1. Make `Polygon` valid Python and actually used (remove `Object`/`new`; make it the data
   object both functions operate on — resolves TODO@L33).
2. Generalize `calc_polygon_details` with the correct formulas for arbitrary `sides >= 3`
   (resolves TODO@L18).
3. Generalize `draw_polygon` to use the polygon's `sides` (resolves TODO@L50).
4. **OOP improvement (R3.4 / R5.2.3):** `Polygon` becomes the single source of truth;
   `calc_polygon_details` becomes a constructor/classmethod or folds into `Polygon.__init__`.

**The six-signal mapping — how the graph points here** (evidentiary heart; reused verbatim
in `PRD_weakness_detector.md`):

| Signal (PART-C) | Evidence in `artifacts/graphify/graph.json` | What it means here |
|---|---|---|
| 1. God node / bottleneck | `Polygon` (`polygons_polygons_polygon`) has degree 4 — highest in the graph (GRAPH_REPORT.md "God Nodes" #1) — bridges Community 4 (`Polygon`, `object`, `.__init__()`, `calc_polygon_details()`) and Community 1 (`polygons.py`, `draw_polygon()`, the 3 TODO rationale nodes) | Investigate this node first — it's both the most-referenced abstraction AND (per source) currently broken/unused |
| 2. Ambiguous/inferred edge | `mathsquiz_readme_maths_quiz --conceptually_related_to--> readme_broken_python` (INFERRED, confidence 0.9); `mathsquiz_mathsquiz_final_py --semantically_similar_to--> mathsquiz_mathsquiz` (INFERRED, confidence 0.8) | Secondary example only — open `source_file` to confirm before treating as fact |
| 3. Broken/missing path | `mathsquiz-final.py` is a graph node (referenced by `mathsquiz/README.md`, `references` EXTRACTED edge) but **the file does not exist** in `data/broken-python/mathsquiz/` (only `mathsquiz.py`, `mathsquiz-step1/2/3.py` exist) | Secondary/optional test fixture for weakness_detector — documents a PRD→code gap in the *mathsquiz* community, not the primary fix |
| 4. Critical-path break | `polygons.py` has no validation that `sides >= 3` before calling `calc_polygon_details`/`draw_polygon` | Minor; mention in OOP-improvement summary, not a blocking fix |
| 5. Isolated cluster | Community 1's three `rationale_*` nodes (`# TODO: find a better way...`, `# TODO: perhaps I should use the class Polygon...`, `# TODO: make this work for any type of polygon`) are weakly connected (each has exactly 1 edge — `rationale_for` → `polygons.py`) per GRAPH_REPORT.md "Knowledge Gaps" | These three TODOs **are** the bug — the developer's own notes describing exactly the incompleteness above |
| 6. Semantic duplicate | `calc_polygon_details()`'s returned dict (`sides`, `internal_angles_sum`, `internal_angles`) duplicates the fields of the unused `Polygon` class (`sides`, `internal_angles_sum`, `internal_angle`) | TODO@L33 names this explicitly — "two impls", one (dict) used, one (class) dead |

*Covers:* R2.1, R2.2, R5.2.2, R4.5. *See also:* ADR-0003 (rejected alternatives).

---

## 3. Graphify graph generation

Graphify is consumed as a **black-box tool**; this project does not regenerate its
internals. The repository ships a **pre-generated, PRE-FIX baseline** under
`artifacts/graphify/`:

- `graph.json` — the knowledge graph,
- `GRAPH_REPORT.md` — human-readable report,
- `manifest.json` — run manifest.

**Graph facts (from `GRAPH_REPORT.md`, reused verbatim):** **23 nodes · 20 edges · 6
communities**; extraction quality **90% EXTRACTED / 10% INFERRED / 0% AMBIGUOUS** (2
INFERRED edges, avg confidence 0.85); **1 isolated node** (`MIT License`); **no import
cycles**. God nodes (descending degree): `Polygon` (4), `Maths Quiz Documentation` (3),
`calc_polygon_details()` (2), `Broken Python Project` (2).

These three files are **read-only graded artifacts** — they must never be overwritten by a
re-run. A separate **POST-FIX graph** must be produced after the bug fix (into a distinct
location such as `artifacts/graphify_post_fix/`, exact name decided in PLAN.md) and
**diffed against the PRE-FIX baseline** as evidence of the refactor's structural impact
(R5.6.3).
*Covers:* R5.1.1, R5.6.3.

---

## 4. The Obsidian vault (`index.md` / `hot.md` navigation)

The repository ships a **PRE-FIX Obsidian vault** under `obsidian/`: one Markdown note per
graph node (file / function / concept / TODO-rationale), each cross-linked with Obsidian
wikilinks (`[[...]]`), plus a navigation hub `index.md` (29 files total). `index.md` lists
all six communities and all nodes as wikilinks — the agent's structural map of the repo.

**`hot.md` does not exist yet** — it is a **project deliverable** (Phase 4), derived from a
**graph metric** (centrality and/or proximity to the bug location), not arbitrarily ordered
(R5.6.1). The exact metric is specified in `PRD_graph_reader.md` /
`PRD_token_comparison.md` and generated by `obsidian_writer.py`.

Together, `index.md` (full breadth: every node + community) and `hot.md` (prioritized "where
to look first") function as the agent's **compressed map that replaces raw file dumps**: the
agent reads the map first to localize, then reads only the implicated source file(s) on
demand — the mechanism by which token cost is reduced without losing bug-localization
accuracy. Both vault files must stay consistent with `graph.json` (a TODO/CI check enforces
this).
*Covers:* R5.1.2, R5.1.3, R5.1.4, R5.5.1.

---

## 5. Graph-guided vs naive agent workflow

The agent is built with **LangGraph** (ADR-0001) with an explicitly typed state schema
(R6.1.4). It runs the **same fix task twice** for the comparison:

- **Graph-guided run** — given `index.md` + `hot.md` as primary context, then reads
  individual source files **on demand** as hypotheses require validation. The graph is the
  navigation backbone (R6.2.1 — no LLM-only-without-graph workflow).
- **Naive baseline run** — given the **entire repository dumped** into context, no graph.

The LangGraph node sequence (Plan → Retrieve(graph) → Hypothesize → Validate(source) → Fix
→ Report), tools, and stop conditions are detailed in `PRD_agent_workflow.md`. Both runs
route every LLM call through `gatekeeper.py` so token usage is captured identically.
*Covers:* R5.3.1, R5.3.2, R5.3.3, R6.2.1.

---

## 6. The six-weakness detection method

`weakness_detector.py` applies the six PART-C signals (verbatim below) to **this** graph,
mapping each to a bug-class hypothesis via the table in §2:

1. **God node / bottleneck** (high degree) → coupling bug, blast-radius point. *Here:*
   flags `Polygon` (degree 4) as investigate-first — the broken, unused core abstraction.
2. **Ambiguous / inferred edge** (low confidence) → unclear logic bug — open `source_file`
   first. *Here:* flags the 2 INFERRED mathsquiz edges as confirm-before-trusting (secondary).
3. **Broken / missing path** (PRD→code gap) → unimplemented / partial requirement. *Here:*
   flags `mathsquiz-final.py` (referenced node, file absent) as a documented PRD→code gap.
4. **Critical-path break** (missing validate/check) → skipped validation / unenforced
   policy. *Here:* flags the absent `sides >= 3` guard (minor, OOP-summary only).
5. **Isolated cluster** (few edges, no `tested_by`) → dead / untested code. *Here:* flags
   the three weakly-connected `rationale_*` TODO nodes — which *are* the bug's own notes.
6. **Semantic duplicate** (`similar_to`, high score) → two impls drifted; one fixed, one
   not. *Here:* flags the `calc_polygon_details` dict vs. the unused `Polygon` fields.

**Inference discipline (PART-C 5-step pipeline):** every claim follows **Observe → Relation
→ Confidence → Context → Source-validation**. Language strength must track evidence
strength using a consistent vocabulary: **`EXTRACTED`** states facts, **`INFERRED`**
suggests, **`AMBIGUOUS`** = manual check required. The graph proposes a *hypothesis*; only
reading the `source_file` makes it a *conclusion*. Any module or agent step asserting from
the graph must tag the claim EXTRACTED/INFERRED/AMBIGUOUS and, for INFERRED/AMBIGUOUS, show
the source-validation step.
*Covers:* R4.3, R5.2.1. *See:* `PRD_weakness_detector.md` for the full detector spec.

---

## 7. Token-comparison metrics

The comparison harness (`token_comparison.py`, driven by `gatekeeper.py` logs — **not
estimates**) measures, per run (graph-guided vs naive baseline):

- **input tokens** and **output tokens**,
- **per-node token breakdown** via the gatekeeper choke point,
- **LLM call counts**,
- **wall-clock time**,
- (qualitatively) **whether each run correctly identifies the same root cause** — i.e.
  whether the token saving costs bug-localization accuracy.

Results are reported with **concrete numbers** (R5.6.4) and stored as static artifacts
under `reports/` so grading does not require an API key (ADR-0005). Full metric definitions
and the report format are in `PRD_token_comparison.md`.
*Covers:* R5.6.1, R5.6.2, R5.6.3, R5.6.4, R7.8, R4.1, R4.2.

---

## 8. Research questions (R4.1–R4.7)

| RQ | How this project answers it |
|---|---|
| **R4.1** — token reduction vs naive baseline, and by how much? | Answered quantitatively by `reports/token_comparison.md` (produced Phase 6) from `gatekeeper.py` token logs for both runs (§7). |
| **R4.2** — does the reduction cost / improve bug-localization accuracy? | Answered by the same comparison report: each run's root-cause identification is checked for correctness against the §2 root cause (§7). |
| **R4.3** — what do God Nodes reveal about core abstractions / coupling risk? | Answered by `weakness_detector.py` signal 1 + GRAPH_REPORT.md: `Polygon` (degree 4) is the core, cross-community, currently-broken abstraction (§2, §6). |
| **R4.4** — what OOP improvements does the graph suggest, and were they applied? | Answered by the OOP-improvement summary (R7.7): `Polygon` as single source of truth, removing the dict/class duplication (signal 6), applied in the fix (§2). |
| **R4.5** — how did the graph identify the root cause (not a symptom)? | Answered by §2's six-signal mapping + `PRD_weakness_detector.md`: the God-node + isolated-TODO-cluster + semantic-duplicate signals converge on the half-finished `Polygon` class. |
| **R4.6** — how did Obsidian concretely help the agent / student? | Answered by §4 plus Obsidian graph-view screenshots/diagrams (R5.4.1 / R7.9), produced in the documentation phase. |
| **R4.7** — how was AI used (disclosure), and where did the agent diverge from a human? | Answered by `docs/PROMPTS.md` (AI-usage disclosure, R8.8) and the README AI-disclosure section. |

*Covers:* R4.1, R4.2, R4.3, R4.4, R4.5, R4.6, R4.7.

---

## 9. Locked decisions

| # | Decision | ADR | Rationale |
|---|---|---|---|
| D1 | **LangGraph**, not CrewAI | [`adr/0001-langgraph-over-crewai.md`](adr/0001-langgraph-over-crewai.md) | Typed state + per-node token instrumentation needed for R5.6 token comparison; tighter control of LLM call count/cost than CrewAI's crew abstraction. |
| D2 | **Gatekeeper present** | [`adr/0002-gatekeeper-present-or-omitted.md`](adr/0002-gatekeeper-present-or-omitted.md) | Real LLM calls happen (graph-guided + naive runs); the gatekeeper is the single choke point for rate-limit/retry/queue/logging AND where token counts are captured for R5.6/R7.8. |
| D3 | **Target repo = `martinpeck/broken-python`, bug = `polygons/polygons.py`** | [`adr/0003-target-repo-and-bug.md`](adr/0003-target-repo-and-bug.md) | Full root-cause writeup in §2; small repo, no special env. |
| D4 | **Graph-guided retrieval over naive dump** is the core thesis | [`adr/0004-graph-guided-retrieval-over-naive-dump.md`](adr/0004-graph-guided-retrieval-over-naive-dump.md) | Cites PART-B (context engineering / "Lost in the Middle") and PART-C (six-signal inference discipline). |
| D5 | **Keyless-by-default test strategy** | [`adr/0005-keyless-by-default-test-strategy.md`](adr/0005-keyless-by-default-test-strategy.md) | Full test suite + `self_grade` pass with NO API key (the LLM client is mocked, provider-agnostically). Real runs (for actual R5.6/R7.8 numbers) need the provider's API key (likely `GEMINI_API_KEY`), are run manually once, results stored as static artifacts. |
| D6 | **LLM provider/model config-driven, decided later (no hardcoded default; NOT Haiku)** | (D6, ADR-0001 context) | Provider+model live in `config/agent.json`, never hardcoded. Likely provider = **Google Gemini** (key already present in the Graphify env), but kept open; the gatekeeper is provider-agnostic. The final model choice + its R6.1.5 justification is recorded when the run is performed (Phase 6). |
| D7 | **uv-only**, `pyproject.toml` (not `requirements.txt`) | (CLAUDE.md §4; ASSIGNMENT R9.1) | Matches CLAUDE.md non-negotiables and is explicitly allowed by assignment §9. |

*Covers:* R6.1.4, R6.1.5, R9.1.

---

## 10. Out of scope

- **NOT regenerating Graphify's own internals.** Graphify is a black-box tool whose output
  (`artifacts/graphify/*`, `obsidian/*`) we consume; the PRE-FIX baseline is read-only and
  must not be overwritten.
- **NOT fixing `mathsquiz.py`'s Python-2 syntax errors.** The mathsquiz community is out of
  scope; `mathsquiz-final.py`'s broken/missing path is used only as a **secondary
  `weakness_detector` test fixture** (see ADR-0003 and §2 signal 3), not a fix target.
- **NOT achieving production-grade turtle-graphics rendering.** `draw_polygon` uses
  `turtle`, which requires a display; in CI/headless the tests must **mock/stub the turtle
  calls**. The fix is verified via `calc_polygon_details` outputs **plus a mocked
  `draw_polygon` call sequence** (correct `forward`/`right` arguments per side), **not**
  visual output.
- **NOT supporting CrewAI** (ADR-0001 — LangGraph chosen).
- **NOT requiring an API key for grading** (ADR-0005 — keyless-by-default; real-run numbers
  captured once as static artifacts).

---

## 11. Open items for the project owner

- **`pyproject.toml` `[project] authors`** — currently placeholders (brief §0): student IDs
  for Eyal Shtinmetz, and the full name + email + ID for the second author ("Imri
  <SURNAME>"). Must be filled with real names + IDs before any commit; tracked in
  `KNOWN_LIMITATIONS.md`.
- **Original `broken-python/` clone cleanup** — the pristine sibling clone (its own `.git`)
  is provenance-only, NOT part of the EX04 deliverable tree; it must be `.gitignore`'d or
  removed before submission (PLAN.md Phase note).
- **PDF Hebrew-extraction caveat** — `docs/ASSIGNMENT.md` was reconstructed from a Hebrew
  PDF whose body text does not extract cleanly (only English/technical terms do). The owner
  must **spot-check each numbered requirement against the original PDF** with a
  Hebrew-capable reader and flag any misreading as an ADR amendment if it changes scope.
