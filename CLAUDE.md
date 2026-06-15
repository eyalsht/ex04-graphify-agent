# CLAUDE.md — EX04: Graphify + Obsidian Reverse-Engineering Agent

This file is the project constitution. Every planning doc (`docs/PRD.md`, `docs/PLAN.md`,
`docs/adr/*`, `docs/TODO.md`) and all future code must comply with it. If a rule here
conflicts with another doc, this file wins.

## 1. Project Overview

EX04 is a University of Haifa agentic-AI course assignment (Dr. Yoram Segal, Lesson L07).
Goal: reverse-engineer `martinpeck/broken-python`'s `polygons/polygons.py` using
**Graphify** (knowledge-graph extraction) and **Obsidian** (graph-navigation vault), then
fix the identified bug with a **graph-guided LangGraph agent** that reads `index.md` /
`hot.md` / `graph.json` instead of dumping raw source files into context. The project must
produce concrete evidence — via `gatekeeper.py` token logs — that graph-guided navigation
uses fewer tokens than a naive "dump-all-files" baseline, without sacrificing
bug-localization accuracy. See `docs/PRD.md` for the full spec and `docs/ASSIGNMENT.md`
for the binding, requirement-ID-tagged source of truth.

## 2. Tech Stack & Tooling

- **Package/env manager: `uv` ONLY.** `pip`, `venv`, and `python -m ...` are forbidden.
  All commands run via `uv run ...` / `uv add ...` / `uv sync`.
- **Linting: `ruff`** — must report **0 violations** before any commit.
- **Typing: `mypy --strict`** — must report **0 errors** on `src/`.
- **Testing: `pytest`** with coverage — must be **≥90%** [TIGHTENED from the course's 85%
  baseline].
- **LLM provider/model: config-driven, decided later — never hardcoded.** Provider + model id
  live in `config/agent.json` (e.g. `{"provider": "...", "model": "..."}`); **no default is
  pinned in code, and specifically NOT a Claude Haiku default.** Likely provider = **Google
  Gemini** (a Gemini API key already exists in the Graphify environment and will probably be
  reused), but the choice is intentionally open. The gatekeeper (§4 / ADR-0002) must be
  **provider-agnostic**. Secrets via `os.environ` only; the API-key env-var name is itself
  config-driven (e.g. `GEMINI_API_KEY`).
- **Agent framework: LangGraph** (not CrewAI) — see `docs/adr/0001-langgraph-over-crewai.md`.

## 3. Hard Rules (Non-Negotiable)

Every rule below is reproduced from the course-wide CLAUDE.md non-negotiables. Each is
tagged `[TIGHTENED]` (stricter than the course baseline) or `[PROJECT-ADDED]`
(EX04-specific, not in the course baseline). Untagged rules are the course baseline as-is.

- **File size:** Python files (including tests) must be **≤150 lines**. `[TIGHTENED]`
  If a file grows past this, split it — never compress/minify to fit.
- **`uv` ONLY** — `pip`/`venv`/`python -m` are forbidden anywhere in this repo (scripts,
  docs, CI).
- **ruff: 0 violations.** `mypy --strict`: 0 errors on `src/`.
- **Coverage ≥ 90%.** `[TIGHTENED]` (course baseline is 85%).
- **TDD strict: RED → GREEN → REFACTOR.** Tests are written first, must fail, then the
  minimum code to pass is written, then refactored. Tests are committed **before or with**
  the code they test — never after.
- **No hardcoded config or values.** All configuration comes from JSON (`config/*.json`)
  or environment variables. Secrets (the provider API key, e.g. `GEMINI_API_KEY` — the env
  var name is itself config-driven via `config/agent.json` `api_key_env`) come from
  `os.environ` only — never literals, never committed.
- **SDK-first architecture.** All business logic lives behind `src/ex04_graphify_agent/sdk.py`.
  `cli.py` (and any future GUI) is a thin wrapper with **zero** business logic.
- **API Gatekeeper present (provider-agnostic).** Every external LLM-provider API call goes
  through `gatekeeper.py` (rate-limit, retry, queue, logging, token counters) — required
  because this project makes real LLM calls (graph-guided run + naive baseline run). The
  concrete provider (likely Gemini; per `config/agent.json`) is hidden behind the gatekeeper
  so it can be swapped without touching other modules. See
  `docs/adr/0002-gatekeeper-present-or-omitted.md`.
- **No `NotImplementedError` on `main`.** Nothing merged to `main` may contain stub
  exceptions for unimplemented behavior.
- **No mock classes shadowing real imports.** Test doubles must not redefine/shadow
  production class names in a way that masks import errors.
- **Continuous commit history.** No single mass-commit. **Conventional Commits**
  (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, etc.), each commit **≤~300 lines**.
- **`pyproject.toml` `authors`** contain real student names + IDs (never "AI Agent"):
  **Eyal Shtinmtez** (ID 314884834, `eyalshtinmetz@gmail.com`) and **Imree Cohen**
  (ID 312359284, email TBD). Use these when scaffolding `pyproject.toml`. Two minor
  follow-ups before the first commit (tracked in `docs/KNOWN_LIMITATIONS.md`): Imree's
  email, and confirming Eyal's Latin surname spelling ("Shtinmtez" vs the "shtinmetz" in
  his email).
- **Keyless-by-default test strategy.** The full test suite and `self_grade` must pass with
  **no API key** — all LLM-provider calls mocked at the gatekeeper boundary in tests. See
  `docs/adr/0005-keyless-by-default-test-strategy.md`.
- **Honest self-grade.** The final self-grade must be conservative, defensible, and
  cross-referenced against `docs/KNOWN_LIMITATIONS.md` — no inflated claims.

### EX04-specific additions `[PROJECT-ADDED]`

- Graphify outputs (`artifacts/graphify/*`) and the Obsidian vault (`obsidian/*`) are
  **graded artifacts**: never regenerate-and-overwrite the **PRE-FIX baseline**. Any
  POST-FIX graph regeneration goes into a separate directory
  (`artifacts/graphify_post_fix/` or equivalent — exact name decided in `docs/PLAN.md`).
- `obsidian/index.md` and `obsidian/hot.md` must stay consistent with `graph.json`
  (tracked as a `docs/TODO.md` checklist item).
- `reports/token_comparison.md` (or equivalent) numbers must come from **`gatekeeper.py`'s
  logs**, not estimates or hand-waving.
- Any graph-derived claim made by a module or the agent must be tagged
  **EXTRACTED / INFERRED / AMBIGUOUS** and follow the PART-C 5-step inference discipline:
  **Observe → Relation → Confidence → Context → Source-validation**. `INFERRED` and
  `AMBIGUOUS` claims must show the source-validation step before being treated as fact.

## 4. EX04-Specific Artifact Rules `[PROJECT-ADDED]`

- **PRE-FIX baseline is immutable.** `artifacts/graphify/graph.json`,
  `artifacts/graphify/GRAPH_REPORT.md`, `artifacts/graphify/manifest.json`, and all of
  `obsidian/*.md` (as currently vendored) represent the PRE-FIX state of
  `data/broken-python/`. Do not edit or regenerate these in place.
- **POST-FIX artifacts go in a separate directory** (e.g. `artifacts/graphify_post_fix/`),
  produced by re-running Graphify against the fixed `data/broken-python/polygons/polygons.py`.
  Both PRE-FIX and POST-FIX must be retained for `R5.6.3` (graph diff before/after).
- **`hot.md` is a Phase 4 deliverable**, not part of the vendored PRE-FIX vault. It must be
  generated from a documented graph metric — centrality and/or proximity to the bug
  location (`R5.6.1`) — not curated by hand or arbitrary ordering.
- **Token-comparison numbers are evidence-based.** Any number reported in
  `reports/token_comparison.md` (input/output tokens, call counts, naive vs. graph-guided)
  must trace back to a stored `gatekeeper.py` log entry. Do not substitute estimates.
- **Inference discipline applies everywhere graph facts are used.** Whenever
  `weakness_detector.py`, `agent_workflow/`, or any PRD references a fact from
  `graph.json`, it must be tagged EXTRACTED, INFERRED, or AMBIGUOUS, with language strength
  matching evidence strength. INFERRED/AMBIGUOUS claims require an explicit
  source-validation step (open `source_file` and confirm) before being acted on.

## 5. Directory Layout

```
HW4/                              <- project root (becomes its own git repo; not yet git-init'd)
├── CLAUDE.md                     <- this file
├── docs/                         <- EXISTS
│   ├── ASSIGNMENT.md             <- DONE (requirement IDs R#.#)
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
├── data/broken-python/           <- EXISTS — vendored target repo (mathsquiz/, polygons/, README.md, LICENSE.txt)
├── artifacts/graphify/           <- EXISTS — PRE-FIX graph.json, GRAPH_REPORT.md, manifest.json (read-only baseline)
├── obsidian/                      <- EXISTS — PRE-FIX vault: index.md + per-node *.md (hot.md = Phase 4 output)
├── reports/                       <- EXISTS, empty — final reports land here (Phase 6-7)
├── lec/                            <- EXISTS — course PDFs (reference only, not a deliverable)
├── broken-python/                 <- EXISTS — ORIGINAL pristine clone (provenance only; not part of deliverable tree)
│
│  ── Phase-1 scaffold only (not yet created) ──
├── pyproject.toml                 <- Phase 1 (authors placeholder per §3)
├── uv.lock                         <- Phase 1
├── src/ex04_graphify_agent/        <- Phase 1 (see §6 module table)
├── tests/                           <- Phase 1
├── config/                          <- Phase 1 (agent.json etc.)
└── .github/                         <- Phase 1 (CI, if used)
```

## 6. Module Structure (SDK-First)

Package: `src/ex04_graphify_agent/`

| Module | Responsibility | Primary PRD |
|---|---|---|
| `graph_reader.py` | Parse `graph.json`; compute degree/betweenness/centrality; filter by confidence (EXTRACTED/INFERRED/AMBIGUOUS) | `docs/PRD_graph_reader.md` |
| `weakness_detector.py` | The six PART-C signals → bug-class hypotheses, each with an Observe→Relation→Confidence→Context→Source-validation trail | `docs/PRD_weakness_detector.md` |
| `obsidian_writer.py` | Generate/update `index.md`, `hot.md`, per-node notes | `docs/PRD_graph_reader.md` (vault is graph_reader's output) |
| `agent_workflow/` | LangGraph graph: typed state schema + nodes (Plan → Retrieve(graph) → Hypothesize → Validate(source) → Fix → Report) | `docs/PRD_agent_workflow.md` |
| `gatekeeper.py` | Wraps every LLM-provider API call (provider-agnostic; provider per `config/agent.json`): rate-limit, retry, queue, logging, token counters | `docs/adr/0002-*.md`, `docs/PRD_token_comparison.md` |
| `token_comparison.py` | Runs graph-guided vs. naive baseline, produces comparison report | `docs/PRD_token_comparison.md` |
| `sdk.py` | Top-level façade — all business logic lives behind this | `docs/PLAN.md` |
| `cli.py` | Thin CLI (Typer/argparse), zero business logic | `docs/PLAN.md` |

## 7. Workflow

### TDD discipline
- Every change starts with a failing test (RED), then minimum code to pass (GREEN), then
  cleanup (REFACTOR). Tests are committed before or with the implementation, never after.
- Files (including test files) stay ≤150 lines — split early rather than letting a module
  grow.

### Commit cadence
- Small, continuous commits using Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`,
  `refactor:`, `chore:`), each ≤~300 lines diff.
- No mass-commits that bundle multiple unrelated changes.

### Running tests keyless (default)
- `uv run pytest --cov=src --cov-report=term-missing`
- All LLM-provider API calls are mocked — `gatekeeper.py`'s provider client is
  injected/mocked in tests so the full suite and `self_grade` pass with **no provider API
  key set** (e.g. no `GEMINI_API_KEY`).
- `uv run ruff check .` and `uv run mypy --strict src/` must both report clean before
  committing.

### Real runs for token-comparison numbers (separate, manual, future)
- The actual `R5.6`/`R7.8` token-comparison numbers (graph-guided vs. naive baseline)
  require a **real** provider API key (config-driven, likely `GEMINI_API_KEY`) and are run
  **manually, once** — not as part of the automated/keyless test suite.
- These runs produce static artifacts (e.g. `reports/token_comparison.md`,
  `artifacts/graphify_post_fix/*`, gatekeeper logs) that are committed and used for grading,
  so grading itself never requires an API key.
- See `docs/adr/0005-keyless-by-default-test-strategy.md` for the full rationale.

## 8. References

- `docs/PRD.md` — full product requirements, research questions, six-signal mapping.
- `docs/PLAN.md` — phased implementation plan, exact directory/module decisions.
- `docs/adr/` — Architecture Decision Records (0001 LangGraph, 0002 Gatekeeper, 0003
  target repo/bug, 0004 graph-guided retrieval, 0005 keyless testing).
- `docs/ASSIGNMENT.md` — binding requirements (requirement IDs R#.#), source of truth for
  scope.
- `docs/KNOWN_LIMITATIONS.md` — open items (incl. `pyproject.toml` authors placeholder),
  honest self-grade basis.
