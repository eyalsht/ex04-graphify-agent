# INTERNAL CONTEXT BRIEF (not a graded deliverable — delete before submission)

This file exists so every planning-doc subagent works from the **same locked decisions**.
Read this fully before writing your assigned file(s). Cite `docs/ASSIGNMENT.md` requirement
IDs (R5.1.1 etc.) wherever relevant — every PRD/PLAN/ADR claim should be traceable to a
requirement ID or to a locked decision below.

## 0. Project identity

- Project: **EX04 — Graphify + Obsidian Reverse-Engineering Agent**, University of Haifa,
  Dr. Yoram Segal's agentic-AI course (Lesson L07).
- Repo root = `HW4/` (this directory). Not yet `git init`'d — PLAN.md should note this is
  done in Phase 1 (scaffold), not this session.
- pyproject.toml `[project] authors` — **REAL IDENTITIES PROVIDED** (owner supplied
  2026-06-14). Use these verbatim when scaffolding `pyproject.toml` in Phase 1:
  ```toml
  authors = [
    { name = "Eyal Shtinmtez", email = "eyalshtinmetz@gmail.com" },   # ID 314884834 (HE: אייל שטינמץ)
    { name = "Imree Cohen", email = "" },                             # ID 312359284 (HE: אמרי כהן) — email still TODO
  ]
  ```
  - **ID 314884834** — Eyal Shtinmtez / אייל שטינמץ.
  - **ID 312359284** — Imree Cohen / אמרי כהן.
  - Two tiny open items remain: (a) Imree's email is not yet provided (needed for the
    `Co-Authored-By` trailer + pyproject author email); (b) Eyal's surname as typed
    ("Shtinmtez") differs from his email local-part ("shtinmetz") — confirm the intended
    Latin spelling before the first commit. Neither blocks scaffolding the rest.
  - **Never** use "AI Agent" or similar as an author (CLAUDE.md non-negotiable).

## 1. Locked decisions (treat as final — do not re-litigate)

| # | Decision | One-line rationale |
|---|---|---|
| D1 | **LangGraph**, not CrewAI | Typed state + per-node token instrumentation needed for R5.6 token comparison; tighter control of LLM call count/cost than CrewAI's crew abstraction. → ADR-0001 |
| D2 | **Gatekeeper present** | Real LLM calls happen (graph-guided run + naive baseline run); gatekeeper is the single choke point for rate-limit/retry/queue/logging AND the place token counts are captured for R5.6/R7.8. → ADR-0002 |
| D3 | **Target repo = `martinpeck/broken-python`, target bug = `polygons/polygons.py`** | See §2 below for full root-cause writeup. → ADR-0003 |
| D4 | **Graph-guided retrieval over naive dump** is the project's core thesis | Cite PART-B (context engineering / "Lost in the Middle") and PART-C (six-signal inference discipline). → ADR-0004 |
| D5 | **Keyless-by-default test strategy** | Full test suite + `self_grade` run with NO API key (LLM responses mocked provider-agnostically at the gatekeeper). Real runs (needed for the actual token-comparison numbers in R5.6/R7.8) require the chosen provider's API key (likely `GEMINI_API_KEY`; D6), are run manually/once, and results are captured as static artifacts under `reports/` + `artifacts/` so grading doesn't require a key. → ADR-0005 |
| D6 | **LLM provider/model = config-driven, DECIDED LATER (no hardcoded default)** | Provider+model live in `config/agent.json` and are NOT pinned in code. **Likely provider = Google Gemini** (a Gemini API key already exists in the Graphify environment and will probably be reused), but the choice is intentionally left open. The gatekeeper (D2) must be **provider-agnostic** — it wraps whatever provider `config/agent.json` names. **Do NOT pin a default model (and specifically NOT a Claude Haiku default).** Secrets via `os.environ` only (e.g. `GEMINI_API_KEY` / `GOOGLE_API_KEY`, or another provider's key) — the env-var name is itself config-driven. |
| D7 | **uv-only**, pyproject.toml (not requirements.txt) | Matches CLAUDE.md non-negotiables (§4) and is explicitly allowed by assignment §9. |

## 2. The chosen bug — full detail (ADR-0003 source material)

**File:** `data/broken-python/polygons/polygons.py` (vendored copy of
`broken-python/polygons/polygons.py`, 76 lines).

**Root cause (single root cause, per R5.2.2/R4.5):** The script was left in a
half-finished state. Its author started writing a `Polygon` class to hold a polygon's
geometry, but:
- `class Polygon(Object):` — `Object` is undefined (Python's built-in is lowercase
  `object`; capital `Object` does not exist) → `NameError` at class-definition time.
- `poly = new Polygon(sides, internal_angles_sum, internal_angles)` (L29) — `new` is not
  Python syntax (Java/C++ habit) → `SyntaxError`, so the file cannot even be imported.
- Because the class was never wired in, `calc_polygon_details()` instead returns a
  hand-rolled `dict` with `sides`/`internal_angles_sum`/`internal_angles` keys —
  duplicating the fields the `Polygon` class was meant to hold (TODO at L33: "perhaps I
  should use the class Polygon instead!").
- `calc_polygon_details(sides)` (L13-36) only computes correct values for `sides == 3`
  (triangle: sum=180, each=60) and `sides == 4` (square: sum=360, each=90); the `else`
  branch hardcodes `sum=1000, each=200` for **any other polygon** — wrong for all
  pentagons, hexagons, etc. TODO at L18: "find a better way to work this stuff out". The
  correct general formulas: `internal_angles_sum = (sides - 2) * 180`,
  `internal_angle = internal_angles_sum / sides`.
- `draw_polygon(polygon_details)` (L41-54) **completely ignores**
  `polygon_details["sides"]` — it hardcodes `for i in range(0, 6): t.forward(50);
  t.right(60)`, i.e. always draws a hexagon regardless of what the user asked for. TODO at
  L50: "make this work for any type of polygon". Correct general version: `for i in
  range(sides): t.forward(50); t.right(360 / sides)`.

**The fix (scope for the "before/after" deliverable):**
1. Fix the `Polygon` class so it's valid Python and actually used (remove `Object`/`new`;
   make `Polygon` the data object both functions operate on — resolves TODO@L33).
2. Generalize `calc_polygon_details` with the correct formulas for arbitrary `sides >= 3`
   — resolves TODO@L18.
3. Generalize `draw_polygon` to use `polygon_details["sides"]` (or the `Polygon` object)
   — resolves TODO@L50.
4. (OOP improvement, R3.4/R5.2.3) — `Polygon` becomes the single source of truth;
   `calc_polygon_details` becomes a constructor/classmethod or is folded into
   `Polygon.__init__`.

**How the graph points here (the six-signal mapping — give this exact table to
PRD_weakness_detector.md and reuse it in PRD.md):**

| Signal (PART-C) | Evidence in `artifacts/graphify/graph.json` | What it means here |
|---|---|---|
| 1. God node / bottleneck | `Polygon` (`polygons_polygons_polygon`) has degree 4 — highest in the graph (GRAPH_REPORT.md "God Nodes" #1) — bridges Community 4 (`Polygon`, `object`, `.__init__()`, `calc_polygon_details()`) and Community 1 (`polygons.py`, `draw_polygon()`, the 3 TODO rationale nodes) | Investigate this node first — it's both the most-referenced abstraction AND (per source) currently broken/unused |
| 2. Ambiguous/inferred edge | `mathsquiz_readme_maths_quiz --conceptually_related_to--> readme_broken_python` (INFERRED, confidence 0.9); `mathsquiz_mathsquiz_final_py --semantically_similar_to--> mathsquiz_mathsquiz` (INFERRED, confidence 0.8) | Secondary example only — open `source_file` to confirm before treating as fact |
| 3. Broken/missing path | `mathsquiz-final.py` is a graph node (referenced by `mathsquiz/README.md`, `references` EXTRACTED edge) but **the file does not exist** in `data/broken-python/mathsquiz/` (only `mathsquiz.py`, `mathsquiz-step1/2/3.py` exist) | Secondary/optional test fixture for weakness_detector — documents a PRD→code gap in the *mathsquiz* community, not the primary fix |
| 4. Critical-path break | `polygons.py` has no validation that `sides >= 3` before calling `calc_polygon_details`/`draw_polygon` | Minor; mention in OOP-improvement summary, not a blocking fix |
| 5. Isolated cluster | Community 1's three `rationale_*` nodes (`# TODO: find a better way...`, `# TODO: perhaps I should use the class Polygon...`, `# TODO: make this work for any type of polygon`) are weakly connected (each has exactly 1 edge — `rationale_for` → `polygons.py`) per GRAPH_REPORT.md "Knowledge Gaps" | These three TODOs **are** the bug — the developer's own notes describing exactly the incompleteness above |
| 6. Semantic duplicate | `calc_polygon_details()`'s returned dict (`sides`, `internal_angles_sum`, `internal_angles`) duplicates the fields of the unused `Polygon` class (`sides`, `internal_angles_sum`, `internal_angle`) | TODO@L33 names this explicitly — "two impls", one (dict) used, one (class) dead |

**Graph facts to reuse verbatim (from `artifacts/graphify/GRAPH_REPORT.md`):** 23 nodes ·
20 edges · 6 communities · 90% EXTRACTED / 10% INFERRED / 0% AMBIGUOUS (2 INFERRED edges,
avg confidence 0.85) · 1 isolated node (`MIT License`) · no import cycles.

**Pre-fix artifacts already vendored (read-only baselines — do not overwrite):**
- `artifacts/graphify/graph.json`, `GRAPH_REPORT.md`, `manifest.json` — the PRE-FIX graph.
- `obsidian/*.md` — PRE-FIX Obsidian vault (per-node notes + `index.md`). **`hot.md` does
  not exist yet** — generating it is a Phase 4 deliverable (see PRD_graph_reader.md /
  PRD_token_comparison.md for the centrality/proximity metric that drives it).
- `data/broken-python/` — vendored copy of the target repo source (the actual file the
  agent fixes is `data/broken-python/polygons/polygons.py`).
- The **original pristine clone** remains at `broken-python/` (sibling, has its own
  `.git`) — kept for provenance/diffing only; PLAN.md should note it is NOT part of the
  EX04 deliverable tree and should be `.gitignore`'d or removed before submission.

## 3. Directory structure (already created this session)

```
HW4/                              <- project root (becomes its own git repo, not yet init'd)
├── CLAUDE.md                     <- you may be writing this
├── docs/
│   ├── ASSIGNMENT.md             <- DONE — read this for requirement IDs (R#.#)
│   ├── _internal_context_brief.md <- THIS FILE — delete before submission
│   ├── PRD.md
│   ├── PLAN.md
│   ├── PROMPTS.md
│   ├── KNOWN_LIMITATIONS.md
│   ├── PRD_graph_reader.md
│   ├── PRD_weakness_detector.md
│   ├── PRD_agent_workflow.md
│   ├── PRD_token_comparison.md
│   ├── TODO.md
│   └── adr/
│       ├── 0001-langgraph-over-crewai.md
│       ├── 0002-gatekeeper-present-or-omitted.md
│       ├── 0003-target-repo-and-bug.md
│       ├── 0004-graph-guided-retrieval-over-naive-dump.md
│       └── 0005-keyless-by-default-test-strategy.md
├── data/broken-python/           <- vendored target repo source (mathsquiz/, polygons/, README.md, LICENSE.txt)
├── artifacts/graphify/           <- PRE-FIX graph.json, GRAPH_REPORT.md, manifest.json
├── obsidian/                      <- PRE-FIX vault: index.md + per-node *.md (hot.md = Phase 4 output)
├── reports/                       <- empty; final reports land here (Phase 6-7)
├── lec/                            <- course PDFs (reference only, not a deliverable)
└── broken-python/                 <- ORIGINAL pristine clone, provenance only (see note above)
```

**NOT created this session** (Phase 1 scaffold, document the intended layout in PLAN.md
but do not create the files): `pyproject.toml`, `src/`, `tests/`, `config/`, `.github/`,
`uv.lock`.

## 4. Module structure (SDK-first) — use these exact names everywhere

Package: `src/ex04_graphify_agent/`

| Module | Responsibility | Primary PRD |
|---|---|---|
| `graph_reader.py` | Parse `graph.json`; compute degree/betweenness/centrality; filter by confidence (EXTRACTED/INFERRED/AMBIGUOUS) | `PRD_graph_reader.md` |
| `weakness_detector.py` | The six PART-C signals → bug-class hypotheses, each with Observe→Relation→Confidence→Context→Source-validation trail | `PRD_weakness_detector.md` |
| `obsidian_writer.py` | Generate/update `index.md`, `hot.md`, per-node notes | `PRD_graph_reader.md` (vault is graph_reader's output) |
| `agent_workflow/` | LangGraph graph: state schema + nodes (Plan→Retrieve(graph)→Hypothesize→Validate(source)→Fix→Report) | `PRD_agent_workflow.md` |
| `gatekeeper.py` | Wraps every LLM-provider API call (provider-agnostic; provider per `config/agent.json`): rate-limit, retry, queue, logging, token counters | ADR-0002, `PRD_token_comparison.md` |
| `token_comparison.py` | Runs graph-guided vs naive baseline, produces comparison report | `PRD_token_comparison.md` |
| `sdk.py` | Top-level façade — all business logic lives behind this | PLAN.md |
| `cli.py` | Thin CLI (Typer/argparse), zero business logic | PLAN.md |

## 5. Six PART-C weakness signals (verbatim — reuse exactly, do not paraphrase differently across docs)

1. **God node / bottleneck** (high degree) → coupling bug, blast-radius point
2. **Ambiguous / inferred edge** (low confidence) → unclear logic bug — open `source_file`
   first
3. **Broken / missing path** (PRD→code gap) → unimplemented / partial requirement
4. **Critical-path break** (missing validate/check) → skipped validation / unenforced
   policy
5. **Isolated cluster** (few edges, no `tested_by`) → dead / untested code
6. **Semantic duplicate** (`similar_to`, high score) → two impls drifted; one fixed, one
   not

**Inference discipline (PART-C 5-step pipeline):** Observe → Relation → Confidence →
Context → Source-validation. Language strength follows evidence strength: `EXTRACTED`
states facts, `INFERRED` suggests, `AMBIGUOUS` = manual check required. The graph
proposes a hypothesis; only reading `source_file` makes it a conclusion. Every PRD that
discusses the agent's reasoning must use this vocabulary consistently.

## 6. CLAUDE.md non-negotiables (verbatim from project kickoff — copy/adapt into CLAUDE.md)

- Python files ≤150 lines (tests too); split, never compress.
- `uv` ONLY — pip/venv/`python -m` forbidden.
- ruff 0 violations; mypy --strict 0 errors on `src/`.
- coverage ≥90% (tightened above the course's 85%).
- TDD strict: RED → GREEN → REFACTOR. Tests committed before/with code, never after.
- No hardcoded values — config from JSON/env only. Secrets via `os.environ` only.
- SDK-first: all business logic behind `sdk.py`; CLI/GUI hold no logic.
- API Gatekeeper for every external LLM call (rate-limit, retry, queue, log) — present in
  this project (D2/ADR-0002), since there ARE external LLM calls.
- No `NotImplementedError` shipped to main. No mock classes shadowing real imports.
- Continuous commit history (no single mass-commit). Conventional Commits, ≤~300
  lines/commit.
- `pyproject.toml` `authors` = real student names + IDs (placeholders — see §0).
- Keyless-by-default: full test suite + `self_grade` pass with NO API keys (all mocked).
- Honest self-grade with `docs/KNOWN_LIMITATIONS.md`; conservative, defensible number.
- **EX04-specific additions** (the gate this brief exists to satisfy):
  - Graphify outputs (`artifacts/graphify/*`, `obsidian/*`) are graded **artifacts** —
    never regenerate-and-overwrite the PRE-FIX baseline; POST-FIX graph outputs go in a
    separate `artifacts/graphify_post_fix/` (or similar — PLAN.md decides exact name).
  - Obsidian vault is a graded deliverable — `index.md`/`hot.md` must stay consistent
    with `graph.json` (a TODO item should check this).
  - Token-comparison report (`reports/token_comparison.md` or similar) is graded —
    numbers must come from `gatekeeper.py`'s logs, not estimates.
  - Graph-literacy inference discipline (§5 above) — any module/agent step that makes a
    claim from the graph must tag it EXTRACTED/INFERRED/AMBIGUOUS and, for
    INFERRED/AMBIGUOUS, show the source-validation step.

## 7. Cross-doc consistency checklist (for the verification pass — just be aware)

- Every `docs/ASSIGNMENT.md` requirement ID (R#.#) should be traceable to ≥1 PRD section
  AND ≥1 `docs/TODO.md` task.
- Every module in §4 above must have a per-mechanism PRD section (4 PRDs cover 6
  modules: `obsidian_writer` folds into `PRD_graph_reader.md`; `sdk.py`/`cli.py` are
  covered in `PLAN.md` only, not a separate PRD).
- Every "Locked decision" (§1) must have a corresponding ADR file.
