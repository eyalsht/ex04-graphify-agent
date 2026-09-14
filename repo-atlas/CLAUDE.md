# CLAUDE.md — repo-atlas

This file is the project constitution. Every planning doc (`docs/PRD.md`, `docs/PLAN.md`,
`docs/adr/*`, `docs/TODO.md`) and all code must comply with it. If a rule here conflicts with
another doc, this file wins.

## 1. Project Overview

`repo-atlas` answers one question for an arbitrary Python repository: **"how does this thing work,
and what is everything in it?"** — without dumping the whole source tree into an LLM's context.

The pipeline is:

```
repo -> extractor (AST) -> graph.json -> graph_reader -> vault (index/notes/hot) -> brief (LLM) -> BRIEF.md
```

Comprehension is the whole product. There is **no bug-finding and no auto-fixing** — that scope
belonged to the origin project and was deliberately dropped (`docs/adr/0002-*`).

Forked from `ex04-graphify-agent` (University of Haifa EX04, Dr. Yoram Segal). That project proved
graph-guided retrieval beats a naive full-source dump on token cost, but was welded to one vendored
target repo and depended on an external, undocumented `graphify` CLI for graph extraction. This
fork keeps the proven parts — the graph reader, the Obsidian vault writer, the API gatekeeper, the
token-comparison evidence discipline — and replaces the target-specific parts with its own AST
extractor (`docs/adr/0001-*`).

## 2. Tech Stack & Tooling

- **Package/env manager: `uv` ONLY.** `pip`, `venv`, and `python -m ...` are forbidden.
  All commands run via `uv run ...` / `uv add ...` / `uv sync`.
- **Linting: `ruff`** — must report **0 violations** before any commit.
- **Typing: `mypy --strict`** — must report **0 errors** on `src/`.
- **Testing: `pytest`** with coverage — must be **≥90%**.
- **LLM provider/model: config-driven, never hardcoded.** Provider + model id live in
  `config/atlas.json`. The gatekeeper is provider-agnostic and dispatches on `provider`; an
  `offline` provider must always exist so the whole tool runs with no network. Secrets come from
  `os.environ` only, via the env-var name given by `api_key_env`.
- **Agent framework: LangGraph.**
- **Target languages: Python** for AST extraction; every other file is indexed as a file node only.

## 3. Hard Rules (Non-Negotiable)

- **File size:** Python files (including tests) must be **≤150 lines**. If a file grows past this,
  split it — never compress or minify to fit.
- **`uv` ONLY** — `pip`/`venv`/`python -m` are forbidden anywhere in this repo (scripts, docs, CI).
- **ruff: 0 violations.** `mypy --strict`: 0 errors on `src/`.
- **Coverage ≥ 90%.**
- **TDD strict: RED → GREEN → REFACTOR.** Tests are written first, must fail, then the minimum code
  to pass is written, then refactored. Tests are committed **before or with** the code they test.
- **No hardcoded config or values.** All configuration comes from `config/*.json` or the CLI.
  Secrets come from `os.environ` only — never literals, never committed.
- **No target-repo literals in `src/`.** No graph node id, no repo-relative source path, no target
  file name may appear as a string literal in library code. This is the rule whose absence made the
  origin project unreusable; `scripts/check_no_hardcoded.py` enforces it mechanically.
- **Every path is a parameter.** No module may discover the repo root by walking up the filesystem
  looking for its own config. Paths enter through `RunPaths`, built from CLI arguments.
- **SDK-first architecture.** All business logic lives behind `src/repo_atlas/sdk.py`.
  `cli.py` (and any future GUI) is a thin wrapper with **zero** business logic.
- **API Gatekeeper.** Every external LLM-provider call goes through `gatekeeper/` — rate-limit,
  retry, queue, logging, token counters. No module talks to a provider SDK directly.
- **No `NotImplementedError` on `main`.**
- **No mock classes shadowing real imports.**
- **Continuous commit history.** No mass-commits. **Conventional Commits** (`feat:`, `fix:`,
  `test:`, `docs:`, `refactor:`, `chore:`), each commit **≤~300 lines**.
- **Keyless-by-default test strategy.** The full test suite must pass with **no API key** — the
  gatekeeper falls back to `MockClient` when the configured key env var is unset.
- **Evidence, not estimates.** Any token or cost number in a report must trace back to a stored
  gatekeeper log entry. `_assert_logs_agree` is not optional.

## 4. Claim Discipline

Every graph-derived claim — in a module, a vault note, or the brief — is tagged
**EXTRACTED / INFERRED / AMBIGUOUS**, and the language strength must match the tag:

| Tag | Means | Language |
|---|---|---|
| `EXTRACTED` | Read directly off the AST | assertive, no hedging |
| `INFERRED` | Resolved by heuristic (attribute call, star-import, name match) | "may", "suggests", "likely" |
| `AMBIGUOUS` | Could not be resolved | explicitly flags that a human must check |

An `INFERRED` or `AMBIGUOUS` claim that is acted upon must first show a source-validation step —
open the `source_file` and confirm.

## 5. Directory Layout

```
repo-atlas/
├── CLAUDE.md
├── pyproject.toml, uv.lock
├── config/atlas.json            <- provider/model/pricing/limits/thresholds
├── docs/
│   ├── PRD.md, PLAN.md, TODO.md, KNOWN_LIMITATIONS.md
│   └── adr/
├── scripts/                     <- CI gates (check_*.py)
├── src/repo_atlas/              <- see §6
└── tests/                       <- mirrors src/, plus fixtures/ and evals/
```

Generated output never lands in the repo tree: `atlas` writes to the `--out` directory the caller
chooses (default `.atlas/` inside the target repo, gitignored).

## 6. Module Structure (SDK-First)

| Module | Responsibility |
|---|---|
| `extractor/` | Walk a Python repo, build `graph.json` + `manifest.json` + `GRAPH_REPORT.md` from the AST |
| `graph_reader/` | Parse `graph.json`; degree/betweenness; filter by confidence; community queries |
| `vault/` | Generate `index.md`, `community-*.md`, per-node notes, `hot.md` |
| `brief/` | LangGraph flow that turns the graph + vault into `BRIEF.md` |
| `gatekeeper/` | Provider-agnostic LLM wrapper: rate-limit, retry, logging, token counters |
| `token_comparison/` | Graph-guided vs naive-dump runs; evidence-backed comparison report |
| `sdk.py` | Top-level façade — all business logic lives behind this |
| `cli.py` | Thin Typer CLI, zero business logic |

## 7. Workflow

### Running the gates
```
uv run ruff check . && uv run ruff format --check .
uv run mypy --strict src/
uv run python scripts/check_file_sizes.py
uv run python scripts/check_no_hardcoded.py
uv run python scripts/check_anti_patterns.py
uv run pytest --cov=src --cov-fail-under=90
```

### Testing against graphs
Tests build synthetic graphs with `tests/fixtures/graph_factory.py`. Only the extractor's
golden-regression test may read `tests/fixtures/golden/`. Never pin the suite to one real artifact —
that is precisely what made the origin project impossible to retarget.

### Real runs
Token-comparison numbers require a real provider key (per `config/atlas.json` `api_key_env`) and are
run manually. Their output is committed as static evidence so nothing in CI needs a key.
