# TODO.md — EX04: Graphify + Obsidian Reverse-Engineering Agent

> The atomic, phased, execute-from task list. Every task is one checkable unit of work.
> Source-of-truth docs: `docs/ASSIGNMENT.md` (R#.#), `docs/PRD*.md` (test-case IDs),
> `docs/PLAN.md` (modules/config), `docs/adr/*` (decisions), `docs/_internal_context_brief.md`.

## Legend

**Phases**
- **Phase 0 — Planning** (verification of the now-complete planning layer)
- **Phase 1 — Scaffold** (pyproject/uv, package + tests skeleton, config, tooling, git)
- **Phase 2 — graph_reader (TDD)** (parse graph.json, metrics, filters, obsidian_writer ranking)
- **Phase 3 — weakness_detector (TDD)** (six PART-C signals, thresholds, gatekeeper base)
- **Phase 4 — Obsidian vault build** (`hot.md` generation, wikilink consistency)
- **Phase 5 — LangGraph agent (TDD) + structural evals** (state, nodes, both run types, gatekeeper, `tests/evals/` keyless thesis evals)
- **Phase 6 — token comparison + evidence** (`token_comparison.py`, real run, post-fix graph)
- **Phase 7 — reports** (diagrams, OOP summary, before/after diff narrative)
- **Phase 8 — README + self-grade** (README sections, self_grade, screenshots, final commit)

**Priority**
- `P0` — blocking / critical path
- `P1` — required for grading, not blocking
- `P2` — nice-to-have / stretch

**Status**
- `[ ]` not started · `[x]` done (with ✅ note) — all unchecked except Phase-0 items already done this session.

**Task ID:** `PHASEN-NNN` sequential within phase.

## Task count per phase (best accurate count)

| Phase | Tasks |
|---|---|
| Phase 0 — Planning | 32 |
| Phase 1 — Scaffold | 86 |
| Phase 2 — graph_reader (TDD) | 121 |
| Phase 3 — weakness_detector (TDD) | 118 |
| Phase 4 — Obsidian vault build | 41 |
| Phase 5 — LangGraph agent (TDD) + structural evals | 145 |
| Phase 6 — token comparison + evidence | 90 |
| Phase 7 — reports | 47 |
| Phase 8 — README + self-grade | 71 |
| **Total** | **751** |

---

> **Progress (2026-06-17):** Phase 0 ✅ · Phase 1 ✅ · Phase 2 ✅ · Phase 3 ✅ · Phase 4 ✅ ·
> Phase 5 ✅ (PR #4 merged) · Phase 6 ✅ (PR #6 merged) · Phase 7 ✅ · **Phase 8 🚧 README done
> (branch `phase8/readme`)**.
> Repo live & **private** at `github.com/eyalsht/ex04-graphify-agent`. Branch protection
> enabler-ready (`scripts/enable_branch_protection.sh`) — blocked on GitHub free-private tier
> (see KNOWN_LIMITATIONS #9). All P0/P1 items for Phases 2.9–7 are ticked below; the Obsidian
> app screenshots (PHASE7-018..021) are now captured (Figs 3–6 in reports/screenshots.md).
> **Phase 8: the §8-compliant README (R8.1–R8.9, all inline) is rebuilt — hero/badges, embedded
> Mermaid + graph/Obsidian images, requirement-coverage map — and the MIT `LICENSE` added.**
> Remaining Phase-8 work: `scripts/self_grade.py` (8.3), final cleanup/verification (8.5), and
> the one owner-only keyed token run (KNOWN_LIMITATIONS #5).
>
> **Phase 2 (graph_reader) ✅ — PR #1 merged.** GR-T1..T7 typed query layer; review fixes:
> cached rankings, streamed JSON.
>
> **Phase 3 (weakness_detector + gatekeeper) ✅ — PR #2 merged.** Built by an Opus subagent
> (own worktree, parallel with Phase 4): all six PART-C signals with the
> EXTRACTED/INFERRED/AMBIGUOUS language↔tag invariant + Signal-6 disclosed source-peek,
> primary-above-secondary ranking (`source_validation` left `None`, WD-T8); provider-agnostic
> gatekeeper choke point (throttle→retry→JSONL token log, keyless `MockClient`, ADR-0002/0005).
> Antigravity review (3 perf findings) addressed before merge: **exponential backoff + full
> jitter**, **god_node degree-floor filter** (no full-ranking copy; file-roots still excluded),
> **`__dict__` token-log dump** (no `asdict` deep-copy). Merged green: ruff 0, mypy 0, 92 tests.
>
> **Phase 4 (obsidian_writer + PRE-FIX hot.md) ✅ — PR #3.** Built by a Sonnet subagent (own
> worktree): the leftover Phase-2 `obsidian_writer` ranking (OW-T1..5; PHASE2-089…121),
> `obsidian/hot.md`, the `check_vault_consistency.py` gate, and the `ex04 hot` CLI. Then the
> orchestrator applied the owner's **Option B** decision — re-rank `hot.md` by **centrality
> × proximity-to-bug-node** (new `obsidian_writer/ranking.py`: BFS hop-distance from the
> config-driven bug node; score = (0.6·degree + 0.4·betweenness, max-norm) × 1/(1+dist)).
> Result: all top-8 are the polygons subgraph (Polygon #1); the disconnected mathsquiz/README
> nodes drop to proximity 0 (satisfies R1.4 / PHASE4-030/031). Antigravity review (3 perf
> findings) addressed: **`@functools.cache` on config**, **set-based wikilink check**, and the
> composite ranking reads cached per-node metrics (no from-scratch degree sort). The `sdk.py`
> overlap with Phase 3 was reconciled into a single `Ex04Sdk` (`detect_weaknesses` +
> `generate_hot`, PLAN §4.7). Merged-into-`main` and re-verified green: ruff 0, mypy 0,
> **117 tests @ 97%**, all gates incl. vault-consistency.
>
> **Phase 5 (LangGraph agent_workflow + structural evals) — PR #4 OPEN.** Dispatched to an
> Opus subagent (own worktree); the subagent was cut off mid-task by a session limit after
> committing state/prompts/nodes, and the orchestrator finished it inline (build_graph
> typing, end-to-end run/routing tests, `Ex04Sdk.run_agent`, the AW-T1 eval). One
> parameterized `StateGraph` keyed on `run_type` (AW-T8): graph-guided
> `plan→read_vault→hypothesize→validate→fix→report` with a bounded validate→hypothesize loop
> (AW-E1/AW-T6); naive `plan→dump_repo→fix→report`; shared plan/fix/report node objects for
> instrumentation parity. The keyless **AW-T1 structural eval proves the thesis**:
> graph-guided fix-context **458 tokens vs naive 1795 (~74% fewer)**. Gates green: ruff 0,
> mypy 0 (42 files), **165 tests @ 98%**, `-m eval` 4 passed, all gate scripts.
> ⏳ Awaiting review/approval. *(Honest note: the orchestrator-added parts were written
> tests+code together, not strict RED-first; the subagent's earlier units did follow RED→GREEN.)*
>
> **Phase 6 (token_comparison + evidence) — PR #5 OPEN (stacked on Phase 5's PR #4).**
> Dispatched to a Sonnet subagent whose worktree was based on the Phase-5 branch (not main),
> so it had the `agent_workflow` it measures; its PR targets the Phase-5 branch (auto-retargets
> to main once Phase 5 merges). Built `token_comparison/` — `RunMetrics`/`ComparisonResult`,
> `metrics_from_state` (per-node + #LLM calls), the 3-part automated correctness check
> (pentagon 540/108, hexagon 720/120, mocked-turtle sides), `compare` (reduction % + R4.1/R4.2
> narrative, zero-div guard), `render/write_report` with the mandated R5.6.5 `Files read` +
> `Iterations` columns, and `diff_graphs` (PRE/POST, predicts nodes 23->20 with the three
> `rationale_*` removed; fails loud if the POST-FIX graph is absent). Real R5.6/R7.8 numbers +
> `artifacts/graphify_post_fix/` are deferred to the manual key-gated `scripts/run_comparison.py`
> (ADR-0005 — not fabricated). Gates green (verified by orchestrator; CI doesn't run on a
> non-main base): ruff 0, mypy 0 (48 files), **217 tests @ 98%**, `-m eval` 4 passed, all gate
> scripts. ⏳ Awaiting review/approval. **— now merged via PR #6.**
>
> **Phase 7 (reports) ✅ — branch `phase7/reports`.** Done inline by the orchestrator (the
> reports are content-heavy and share one deep context — the bug, the graph, the agent — so
> spawning subagents would have re-derived it at a net token loss; decision recorded in
> PROMPTS.md). Applied the canonical, correctness-gated fix to
> `data/broken-python/polygons/polygons.py` (R5.2.2; pristine original preserved in git + the
> `broken-python/` clone); re-ran **Graphify v0.8.39** keylessly (`graphify update`, 0 tokens)
> → `artifacts/graphify_post_fix/` (23→23 nodes, 20→17 edges; the 3 `rationale_*` nodes
> removed and a new `calc_polygon_details -calls-> Polygon` usage edge — R5.6.3). Wrote eight
> reports under `reports/` (root_cause, diff_polygons, oop_improvement, graph_diff via the
> reused `diff_graphs` module, token_comparison, diagrams, pipeline, screenshots) + a
> `reports/README.md` index, all cross-linked from the top-level README. Diagrams are Mermaid
> (C4 + both agent routes, **topology-verified against `build_graph`**); `scripts/render_graph.py`
> (matplotlib dev-dep) renders committed PRE/POST graph PNGs with the `Polygon` god node
> ringed. **Keyless token evidence: graph-guided 406 vs naive 1743 input tokens = 76.7%
> reduction** (R4.1). A post-review fix added the Signal-4 `sides >= 3` guard (ValueError) to
> close a `ZeroDivisionError` on the live input path. Two owner-only items remain open
> (Obsidian app screenshots; the keyed full-table run) — see KNOWN_LIMITATIONS #5/#10.
>
> **Phase 8 (README glow-up) 🚧 — branch `phase8/readme`.** Done inline by the orchestrator after
> a `grill-me` interview that locked the design: confident + evidence-backed voice (not hype —
> the grader is an AI agent that rewards requirement coverage), all nine §8 sections **inline**
> with a requirement-coverage map, a hero/badge block (9 static badges), embedded Mermaid for
> both agent routes, and the committed graph/Obsidian images shown in-page. The headline **76.7%**
> stat is footnoted as the keyless input-context measurement (keyed run still pending,
> KNOWN_LIMITATIONS #5). Added the missing MIT `LICENSE` (pyproject already declared MIT; the old
> README linked a non-existent file). All referenced files/links verified to resolve.
>
> **Next:** Phase 8 — `scripts/self_grade.py` (8.3), final cleanup + verification (8.5), submission PR.

## Phase 0 — Planning

- [x] **P0** `PHASE0-001` planning: create `docs/ASSIGNMENT.md` with requirement IDs R1.1–R10.5 — DoD: file exists, all sections numbered — ✅ done this session
- [x] **P0** `PHASE0-002` planning: create `CLAUDE.md` project constitution — DoD: non-negotiables + module table present — ✅ done this session
- [x] **P0** `PHASE0-003` planning: create `docs/PRD.md` top-level spec — DoD: covers R1–R10, six-signal table — ✅ done this session
- [x] **P0** `PHASE0-004` planning: create `docs/PLAN.md` (C4 diagrams, module structure, config) — DoD: §4/§8/§9 scaffold source present — ✅ done this session
- [x] **P0** `PHASE0-005` planning: create `docs/PRD_graph_reader.md` with GR-T1..7 / OW-T1..5 — DoD: test cases enumerated — ✅ done this session
- [x] **P0** `PHASE0-006` planning: create `docs/PRD_weakness_detector.md` with WD-T1..8 — DoD: six signals specified — ✅ done this session
- [x] **P0** `PHASE0-007` planning: create `docs/PRD_agent_workflow.md` with AW-T1..8 — DoD: state schema + nodes — ✅ done this session
- [x] **P0** `PHASE0-008` planning: create `docs/PRD_token_comparison.md` with TC-T1..8 — DoD: metrics + correctness check — ✅ done this session
- [x] **P0** `PHASE0-009` planning: create ADR-0001 (LangGraph over CrewAI) — DoD: accepted, rationale per R5.3.1 — ✅ done this session
- [x] **P0** `PHASE0-010` planning: create ADR-0002 (gatekeeper present) — DoD: accepted per D2 — ✅ done this session
- [x] **P0** `PHASE0-011` planning: create ADR-0003 (target repo + bug) — DoD: six-signal mapping per D3 — ✅ done this session
- [x] **P0** `PHASE0-012` planning: create ADR-0004 (graph-guided over naive) — DoD: core thesis per D4 — ✅ done this session
- [x] **P0** `PHASE0-013` planning: create ADR-0005 (keyless-by-default) — DoD: accepted per D5 — ✅ done this session
- [x] **P0** `PHASE0-014` planning: create `docs/TODO.md` (this file) — DoD: phased atomic task list — ✅ done this session
- [x] **P0** `PHASE0-015` owner: real identities recorded — Eyal Shtinmtez (ID 314884834, eyalshtinmetz@gmail.com) + Imree Cohen (ID 312359284, imree.c@gmail.com) in `pyproject.toml`. Only open: confirm Eyal's Latin surname spelling ("Shtinmtez" vs "shtinmetz") before submission — ✅ authors set
- [ ] **P0** `PHASE0-016` owner: spot-check `docs/ASSIGNMENT.md` against the original Hebrew PDF with a Hebrew-capable reader — DoD: each R#.# verified or corrected; misreads flagged as ADR amendment; ref ASSIGNMENT extraction note
- [ ] **P0** `PHASE0-017` owner: confirm Graphify CLI is available locally for the POST-FIX re-run — DoD: `graphify --version` (or equivalent) runs; if unavailable, note in KNOWN_LIMITATIONS; ref R5.6.3
- [ ] **P0** `PHASE0-018` owner: confirm Obsidian is installed for vault screenshots (R5.4.1/R7.9) — DoD: vault opens in Obsidian; graph view renders
- [ ] **P0** `PHASE0-019` owner: confirm the chosen provider's API key is available for the one manual real run (Phase 6) — likely `GEMINI_API_KEY` (the Gemini key already used by Graphify) — DoD: key present in env (named by `config/agent.json` `api_key_env`) for the manual run only; never committed; ref ADR-0005
- [ ] **P1** `PHASE0-020` verify: cross-check every module in PLAN.md §4 has a primary PRD — DoD: graph_reader, weakness_detector, obsidian_writer, agent_workflow, gatekeeper, token_comparison all mapped
- [ ] **P1** `PHASE0-021` verify: confirm `data/broken-python/polygons/polygons.py` is the vendored 76-line target and matches brief §2 bug description — DoD: `Object`, `new`, else-branch 1000/200, hardcoded range(0,6) all present
- [ ] **P1** `PHASE0-022` verify: confirm `artifacts/graphify/graph.json` has 23 nodes / 20 edges / 6 communities — DoD: counts match GRAPH_REPORT.md
- [ ] **P1** `PHASE0-023` verify: confirm `obsidian/hot.md` does NOT yet exist (Phase 4 output) — DoD: file absent; only index.md + per-node notes present
- [ ] **P1** `PHASE0-024` verify: confirm the 3 rationale node ids exist (`polygons_polygons_rationale_18/33/50`) — DoD: present in graph.json + obsidian/
- [ ] **P1** `PHASE0-025` verify: confirm 2 INFERRED edges exist (scores 0.8 + 0.9) in graph.json — DoD: matches GR-T5
- [ ] **P1** `PHASE0-026` verify: confirm `mathsquiz-final.py` node exists but file is absent on disk — DoD: node present, `data/broken-python/mathsquiz/mathsquiz-final.py` missing; ref signal 3
- [ ] **P1** `PHASE0-027` verify: confirm original pristine `broken-python/` clone is sibling with its own `.git` — DoD: present, to be `.gitignore`'d in Phase 1
- [ ] **P1** `PHASE0-028` planning: ensure `docs/PROMPTS.md` exists/seeded for AI-usage disclosure (R8.8/R4.7) — DoD: file exists with at least the planning-session disclosure
- [ ] **P1** `PHASE0-029` planning: ensure `docs/KNOWN_LIMITATIONS.md` exists with open items (authors placeholder, original-clone cleanup, keyless-run caveat) — DoD: file exists; three open items listed
- [ ] **P1** `PHASE0-030` verify: confirm provider+model are config-driven with NO hardcoded default (D6) — specifically NOT a Claude Haiku default; provider likely Gemini, decided at run time — DoD: no hardcoded provider/model in any planned code path; `config/agent.json` carries `provider`/`model`/`api_key_env`
- [ ] **P2** `PHASE0-031` planning: note delete-before-submission task for `docs/_internal_context_brief.md` — DoD: tracked here + in KNOWN_LIMITATIONS
- [ ] **P2** `PHASE0-032` verify: confirm `lec/` PDFs are reference-only and excluded from the deliverable tree — DoD: noted for `.gitignore` consideration

---

## Phase 1 — Scaffold

### 1.1 — uv project + pyproject

- [ ] **P0** `PHASE1-001` scaffold: `uv init` the project at repo root — DoD: `pyproject.toml` created, `uv` recognizes project; ref R9.1/D7
- [ ] **P0** `PHASE1-002` scaffold: set `[project] name = "ex04-graphify-agent"`, `requires-python = ">=3.11"` — DoD: fields present
- [x] **P0** `PHASE1-003` scaffold: real `[project] authors` set — `Eyal Shtinmtez` (eyalshtinmetz@gmail.com) + `Imree Cohen` (imree.c@gmail.com); IDs 314884834/312359284 in the file header comment — ✅ done; NOT "AI Agent"; ref brief §0
- [ ] **P0** `PHASE1-004` scaffold: configure src layout `src/ex04_graphify_agent/` in `[tool.hatch]`/build backend — DoD: package importable via `uv run python -c "import ex04_graphify_agent"`
- [ ] **P0** `PHASE1-005` scaffold: `uv add networkx` — DoD: dependency in pyproject; ref PRD_graph_reader dependency note
- [ ] **P0** `PHASE1-006` scaffold: `uv add langgraph` — DoD: dependency present; ref ADR-0001
- [ ] **P0** `PHASE1-007` scaffold: `uv add` the chosen provider SDK (likely `google-genai` for Gemini; decided at scaffold time per `config/agent.json` `provider`) — DoD: provider SDK dependency present, isolated behind `gatekeeper.py`; ref D6/ADR-0002
- [ ] **P0** `PHASE1-008` scaffold: `uv add typer` (thin CLI) — DoD: dependency present; ref PLAN.md §4.7
- [ ] **P0** `PHASE1-009` scaffold: `uv add --dev pytest pytest-cov` — DoD: dev deps present
- [ ] **P0** `PHASE1-010` scaffold: `uv add --dev ruff mypy` — DoD: dev deps present
- [ ] **P1** `PHASE1-011` scaffold: `uv add --dev pre-commit` — DoD: dev dep present
- [ ] **P0** `PHASE1-012` scaffold: `uv sync` and commit `uv.lock` — DoD: lockfile generated and committed
- [ ] **P1** `PHASE1-013` scaffold: add `[project.scripts] ex04 = "ex04_graphify_agent.cli:app"` entry point — DoD: `uv run ex04 --help` resolves (after cli stub)

### 1.2 — tooling config

- [ ] **P0** `PHASE1-014` scaffold: configure `[tool.ruff]` (line-length, select rules) — DoD: `uv run ruff check .` runs clean on empty package
- [ ] **P0** `PHASE1-015` scaffold: configure `[tool.mypy]` strict on `src/` — DoD: `uv run mypy --strict src/` runs clean on empty package
- [ ] **P0** `PHASE1-016` scaffold: configure `[tool.pytest.ini_options]` (testpaths, cov default) — DoD: `uv run pytest` collects 0 tests cleanly
- [ ] **P0** `PHASE1-017` scaffold: configure coverage fail-under = 90 — DoD: cov threshold set; ref CLAUDE.md ≥90%
- [ ] **P0** `PHASE1-018` scaffold: create `scripts/check_file_sizes.py` — fails (exit 1) if any `.py` under `src/`/`tests/`/`scripts/` exceeds 150 lines; prints offenders (matches agent-debate's committed CI script) — DoD: script runs standalone, exits 0 on clean tree, ≤150 lines itself; ref CLAUDE.md §3 / commit-discipline skill
- [ ] **P0** `PHASE1-018a` scaffold: TDD `scripts/check_file_sizes.py` — RED+GREEN unit test (`tests/scripts/test_check_file_sizes.py`) on a fixture over-long file → exit 1 — DoD: test fails then passes
- [ ] **P0** `PHASE1-018b` scaffold: create `scripts/check_no_hardcoded.py` — fails if a provider model id, API key literal, or absolute path appears outside `config/*.json` (matches agent-debate's committed CI script) — DoD: standalone, exits 0 clean, ≤150 lines; ref CLAUDE.md §3 (no-hardcoded rule)
- [ ] **P0** `PHASE1-018c` scaffold: TDD `scripts/check_no_hardcoded.py` — RED+GREEN test (`tests/scripts/test_check_no_hardcoded.py`) on a fixture with a hardcoded model/key → exit 1 — DoD: test fails then passes
- [ ] **P1** `PHASE1-018d` scaffold: create `scripts/check_anti_patterns.py` — fails on `NotImplementedError` on main, mock classes shadowing real imports, leftover `print()` debug, `--no-verify` traces (matches agent-debate's committed CI script + CLAUDE.md anti-patterns) — DoD: standalone, exits 0 clean, ≤150 lines
- [ ] **P1** `PHASE1-018e` scaffold: TDD `scripts/check_anti_patterns.py` — RED+GREEN test on a fixture containing `NotImplementedError` → exit 1 — DoD: test fails then passes
- [ ] **P0** `PHASE1-018f` scaffold: create `tests/scripts/` dir + `__init__.py` for the three check-script tests — DoD: pytest discovers them
- [ ] **P1** `PHASE1-019` scaffold: create `.pre-commit-config.yaml` with ruff + ruff-format + mypy + `scripts/check_file_sizes.py` + `scripts/check_no_hardcoded.py` + `scripts/check_anti_patterns.py` hooks (mirrors agent-debate's `.pre-commit-config.yaml`) — DoD: `uv run pre-commit run --all-files` executes all six
- [ ] **P1** `PHASE1-020` scaffold: install pre-commit hooks (`pre-commit install`) — DoD: `.git/hooks/pre-commit` present (post git init)

### 1.3 — package skeleton

- [ ] **P0** `PHASE1-021` scaffold: create `src/ex04_graphify_agent/__init__.py` — DoD: package imports
- [ ] **P0** `PHASE1-022` scaffold: create `src/ex04_graphify_agent/graph_reader/__init__.py` package — DoD: importable; ref PLAN.md §4.1
- [ ] **P0** `PHASE1-023` scaffold: create empty `graph_reader/models.py` (NodeView/EdgeView/Confidence placeholders, no logic) — DoD: file ≤150 lines, imports
- [ ] **P0** `PHASE1-024` scaffold: create empty `graph_reader/loader.py` — DoD: importable stub (no NotImplementedError shipped to main later)
- [ ] **P0** `PHASE1-025` scaffold: create empty `graph_reader/metrics.py` — DoD: importable stub
- [ ] **P0** `PHASE1-026` scaffold: create empty `graph_reader/filters.py` — DoD: importable stub
- [ ] **P0** `PHASE1-027` scaffold: create `weakness_detector/__init__.py` package — DoD: importable; ref PLAN.md §4.2
- [ ] **P0** `PHASE1-028` scaffold: create empty `weakness_detector/hypothesis.py` (WeaknessFinding/SourceValidation placeholders) — DoD: importable stub
- [ ] **P0** `PHASE1-029` scaffold: create empty `weakness_detector/signals.py` — DoD: importable stub
- [ ] **P0** `PHASE1-030` scaffold: create empty `weakness_detector/detector.py` — DoD: importable stub
- [ ] **P0** `PHASE1-031` scaffold: create `obsidian_writer/__init__.py` package — DoD: importable; ref PLAN.md §4.3
- [ ] **P0** `PHASE1-032` scaffold: create empty `obsidian_writer/notes.py` — DoD: importable stub
- [ ] **P0** `PHASE1-033` scaffold: create empty `obsidian_writer/index.py` — DoD: importable stub
- [ ] **P0** `PHASE1-034` scaffold: create empty `obsidian_writer/hot.py` — DoD: importable stub
- [ ] **P0** `PHASE1-035` scaffold: create `agent_workflow/__init__.py` package — DoD: importable; ref PLAN.md §4.4
- [ ] **P0** `PHASE1-036` scaffold: create empty `agent_workflow/state.py` (AgentState placeholder) — DoD: importable stub
- [ ] **P0** `PHASE1-037` scaffold: create empty `agent_workflow/nodes.py` — DoD: importable stub
- [ ] **P0** `PHASE1-038` scaffold: create empty `agent_workflow/graph_def.py` — DoD: importable stub
- [ ] **P0** `PHASE1-039` scaffold: create empty `agent_workflow/prompts.py` — DoD: importable stub
- [ ] **P0** `PHASE1-040` scaffold: create `gatekeeper/__init__.py` package — DoD: importable; ref PLAN.md §4.5
- [ ] **P0** `PHASE1-041` scaffold: create empty `gatekeeper/client.py` — DoD: importable stub
- [ ] **P0** `PHASE1-042` scaffold: create empty `gatekeeper/token_log.py` — DoD: importable stub
- [ ] **P0** `PHASE1-043` scaffold: create `token_comparison/__init__.py` package — DoD: importable; ref PLAN.md §4.6
- [ ] **P0** `PHASE1-044` scaffold: create empty `token_comparison/runner.py` — DoD: importable stub
- [ ] **P0** `PHASE1-045` scaffold: create empty `token_comparison/report.py` — DoD: importable stub
- [ ] **P0** `PHASE1-046` scaffold: create empty `sdk.py` (Ex04Sdk façade placeholder) — DoD: importable stub; ref PLAN.md §4.7
- [ ] **P0** `PHASE1-047` scaffold: create empty `cli.py` (Typer app placeholder, zero logic) — DoD: `uv run ex04 --help` works
- [ ] **P1** `PHASE1-048` scaffold: add `py.typed` marker to package — DoD: present for mypy consumers

### 1.4 — tests skeleton

- [ ] **P0** `PHASE1-049` scaffold: create `tests/__init__.py` + `tests/conftest.py` — DoD: pytest discovers tests dir
- [ ] **P0** `PHASE1-050` scaffold: add `conftest.py` fixture `graph_json_path` → `artifacts/graphify/graph.json` — DoD: fixture importable
- [ ] **P0** `PHASE1-051` scaffold: add `conftest.py` fixture `repo_root` → `data/broken-python/` — DoD: fixture importable
- [ ] **P0** `PHASE1-052` scaffold: add `conftest.py` mocked-gatekeeper fixture (deterministic LLMResponse, no key) — DoD: fixture returns canned response; ref ADR-0005
- [ ] **P0** `PHASE1-053` scaffold: create `tests/graph_reader/` dir mirroring src — DoD: dir present
- [ ] **P0** `PHASE1-054` scaffold: create `tests/weakness_detector/` dir — DoD: dir present
- [ ] **P0** `PHASE1-055` scaffold: create `tests/obsidian_writer/` dir — DoD: dir present
- [ ] **P0** `PHASE1-056` scaffold: create `tests/agent_workflow/` dir — DoD: dir present
- [ ] **P0** `PHASE1-057` scaffold: create `tests/gatekeeper/` dir — DoD: dir present
- [ ] **P0** `PHASE1-058` scaffold: create `tests/token_comparison/` dir — DoD: dir present
- [ ] **P0** `PHASE1-058a` scaffold: create `tests/evals/` dir + `__init__.py` — the keyless structural-eval suite (distinct from unit tests; proves the system does the *right thing*, per eval-harness skill) — DoD: dir present, discovered
- [ ] **P0** `PHASE1-058b` scaffold: register a `eval` pytest marker in `pyproject.toml` (`[tool.pytest.ini_options] markers`) so structural evals run via `uv run pytest -m eval` and behavioural via `-m behavioural` — DoD: markers registered, no "unknown marker" warning; ref eval-harness skill
- [ ] **P1** `PHASE1-059` scaffold: create `tests/test_sdk.py` placeholder — DoD: collects
- [ ] **P1** `PHASE1-060` scaffold: create `tests/test_cli.py` placeholder — DoD: collects

### 1.5 — config files (no-hardcoded-values rule)

- [ ] **P0** `PHASE1-061` scaffold: create `config/agent.json` (`provider`, `model`, `api_key_env`, temperature, max_tokens, retry/rate-limit, max_findings_tried, max_validation_attempts, stop conditions) — DoD: valid JSON; provider/model config-driven with NO hardcoded default and NOT Haiku (likely `provider: gemini`, `api_key_env: GEMINI_API_KEY`); ref PLAN.md §9 / D6
- [ ] **P0** `PHASE1-062` scaffold: create `config/paths.json` (graph.json, obsidian dir, data root, reports dir, artifacts/runs dir, graphify_post_fix dir) — DoD: valid JSON; all paths repo-relative; ref PLAN.md §9
- [ ] **P0** `PHASE1-063` scaffold: create `config/weakness_thresholds.json` (god_node_min_degree=4, ambiguous_confidence_max=0.85, isolated_cluster_max_edges=1, semantic_duplicate_min_score=0.75, missing_path_check=true, hot.md weights) — DoD: valid JSON; ref PRD_weakness_detector inputs
- [ ] **P1** `PHASE1-064` scaffold: add `config/` schema validation note / loader contract — DoD: loaders fail loud on missing config (ref WD-E5)

### 1.6 — git + gitignore + CI

- [ ] **P0** `PHASE1-065` scaffold: create `.gitignore` (`.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`) — DoD: file present
- [ ] **P0** `PHASE1-066` scaffold: `.gitignore` the original `broken-python/` pristine clone — DoD: clone excluded from deliverable tree; ref brief §2/§3
- [ ] **P1** `PHASE1-067` scaffold: `.gitignore` secrets/env (`.env`, never commit any provider API key, e.g. `GEMINI_API_KEY`) — DoD: no secret path tracked; ref CLAUDE.md §3
- [ ] **P2** `PHASE1-068` scaffold: decide `.gitignore` for `lec/` PDFs (reference-only) — DoD: decision recorded
- [ ] **P0** `PHASE1-069` scaffold: `git init` at repo root — DoD: `.git/` created (NOT done in planning session; ref brief §0)
- [ ] **P0** `PHASE1-070` scaffold: stage + initial commit of planning docs + scaffold (`chore: scaffold project`) — DoD: clean commit ≤300 lines or split; Conventional Commits
- [ ] **P1** `PHASE1-071` scaffold: create `.github/workflows/ci.yml` running `uv sync`, `ruff check`, `mypy --strict src/`, `pytest --cov` (≥90%), **and the three standalone gate scripts by name** (`python scripts/check_file_sizes.py`, `python scripts/check_no_hardcoded.py`, `python scripts/check_anti_patterns.py`) — mirrors agent-debate's CI — DoD: workflow file valid; all gates wired; keyless (no key in CI); ref ADR-0005
- [ ] **P1** `PHASE1-072` scaffold: ensure CI runs keyless (no provider API key present) — DoD: workflow has no secret reference for test job
- [ ] **P1** `PHASE1-073` scaffold: create public GitHub repo + push initial commit — DoD: repo public; ref R7.1
- [ ] **P1** `PHASE1-074` scaffold: verify `uv run pytest` green on empty suite — DoD: 0 failures
- [ ] **P1** `PHASE1-075` scaffold: verify `uv run ruff check .` clean — DoD: 0 violations
- [ ] **P1** `PHASE1-076` scaffold: verify `uv run mypy --strict src/` clean — DoD: 0 errors
- [ ] **P2** `PHASE1-077` scaffold: add `README.md` stub with title (R1.1) — DoD: title present; expanded in Phase 8
- [ ] **P2** `PHASE1-078` scaffold: confirm directory tree matches PLAN.md §8 — DoD: src/tests/config/.github present, baselines untouched

---

## Phase 2 — graph_reader (TDD)

> Each PRD_graph_reader.md test case (GR-T1..7, OW-T1..5) → RED + GREEN (+ REFACTOR where noted),
> plus interface-scaffolding tasks for models/loader/metrics/filters and obsidian_writer ranking.

### 2.1 — models + loader interface

- [x] **P0** `PHASE2-001` graph_reader: RED — test `Confidence` enum has EXTRACTED/INFERRED/AMBIGUOUS members — DoD: test fails with AttributeError, not ImportError; ref PLAN.md §4.1
- [x] **P0** `PHASE2-002` graph_reader: GREEN — implement `Confidence(str, Enum)` — DoD: test passes
- [x] **P0** `PHASE2-003` graph_reader: RED — test `NodeView` is frozen dataclass with id/label/file_type/source_file/source_location/community/degree/betweenness — DoD: test fails; ref PRD_graph_reader public interface
- [x] **P0** `PHASE2-004` graph_reader: GREEN — implement `NodeView` frozen dataclass — DoD: test passes
- [x] **P0** `PHASE2-005` graph_reader: RED — test `EdgeView` frozen dataclass with source/target/relation/confidence/confidence_score/weight — DoD: test fails
- [x] **P0** `PHASE2-006` graph_reader: GREEN — implement `EdgeView` frozen dataclass — DoD: test passes
- [x] **P1** `PHASE2-007` graph_reader: REFACTOR — keep `models.py` ≤150 lines, split if needed — DoD: file budget honored
- [x] **P0** `PHASE2-008` graph_reader: RED — test `GraphReader(graph_path)` constructs without error on real graph.json — DoD: test fails (no class yet)
- [x] **P0** `PHASE2-009` graph_reader: GREEN — implement `GraphReader.__init__` loading JSON via `networkx.node_link_graph(data, edges="links")` — DoD: test passes; ref PRD_graph_reader behavior §1
- [x] **P0** `PHASE2-010` graph_reader: RED — test default `graph_path` resolves from `config/paths.json` (not hardcoded literal in logic) — DoD: test fails; ref CLAUDE.md no-hardcoded
- [x] **P0** `PHASE2-011` graph_reader: GREEN — implement config-driven default path — DoD: test passes
- [ ] **P1** `PHASE2-012` graph_reader: RED — test constructor raises clear error on missing graph file — DoD: test fails
- [ ] **P1** `PHASE2-013` graph_reader: GREEN — implement fail-loud missing-file handling — DoD: test passes
- [x] **P1** `PHASE2-014` graph_reader: REFACTOR — keep `loader.py` ≤150 lines — DoD: file budget honored

### 2.2 — GR-T1 load (23 nodes / 20 edges)

- [x] **P0** `PHASE2-015` graph_reader: RED — test `len(all_nodes()) == 23` — DoD: test fails with AttributeError; ref GR-T1
- [x] **P0** `PHASE2-016` graph_reader: GREEN — implement `all_nodes()` returning list[NodeView] — DoD: GR-T1 node count passes
- [x] **P0** `PHASE2-017` graph_reader: RED — test total edges == 20 (`len(all_edges())`/`G.number_of_edges()`) — DoD: test fails; ref GR-T1
- [x] **P0** `PHASE2-018` graph_reader: GREEN — implement edge count accessor — DoD: GR-T1 edge count passes
- [x] **P0** `PHASE2-019` graph_reader: RED — test `node("polygons_polygons_polygon")` returns NodeView with label "Polygon" — DoD: test fails
- [x] **P0** `PHASE2-020` graph_reader: GREEN — implement `node(node_id)` (raises KeyError on miss) — DoD: test passes
- [x] **P0** `PHASE2-021` graph_reader: RED — test `node()` on missing id raises `KeyError` — DoD: test fails; ref edge case "unknown node id"
- [x] **P0** `PHASE2-022` graph_reader: GREEN — implement KeyError on missing id — DoD: test passes
- [x] **P0** `PHASE2-023` graph_reader: RED — test `node_exists("nope")` is False, `node_exists("object")` is True — DoD: test fails
- [x] **P0** `PHASE2-024` graph_reader: GREEN — implement `node_exists(node_id)` safe probe — DoD: test passes
- [x] **P1** `PHASE2-025` graph_reader: RED — test NodeView accepts `source_location is None` (document nodes) — DoD: test fails; ref edge case null source_location
- [x] **P1** `PHASE2-026` graph_reader: GREEN — implement None-tolerant source_location — DoD: test passes
- [x] **P1** `PHASE2-027` graph_reader: RED — test `object` node has empty `source_file == ""` (not a real path) — DoD: test fails; ref edge case Object empty source_file
- [x] **P1** `PHASE2-028` graph_reader: GREEN — implement empty-source_file passthrough — DoD: test passes

### 2.3 — GR-T2 degree (god node = 4)

- [x] **P0** `PHASE2-029` graph_reader: RED — test `degree("polygons_polygons_polygon") == 4` — DoD: test fails with AttributeError, not ImportError; ref GR-T2
- [x] **P0** `PHASE2-030` graph_reader: GREEN — implement `degree(node_id)` via `G.degree` — DoD: GR-T2 passes
- [ ] **P0** `PHASE2-031` graph_reader: RED — test `degree("mathsquiz_readme_maths_quiz") == 3` — DoD: test fails; ref PRD §2 expected degrees
- [ ] **P0** `PHASE2-032` graph_reader: GREEN — degree covered by impl — DoD: test passes
- [ ] **P0** `PHASE2-033` graph_reader: RED — test `degree("polygons_polygons_calc_polygon_details") == 2` — DoD: test fails
- [ ] **P0** `PHASE2-034` graph_reader: GREEN — degree covered — DoD: test passes
- [x] **P0** `PHASE2-035` graph_reader: RED — test each `polygons_polygons_rationale_{18,33,50}` has degree 1 — DoD: test fails; ref signal 5
- [x] **P0** `PHASE2-036` graph_reader: GREEN — degree covered for rationale nodes — DoD: test passes
- [x] **P1** `PHASE2-037` graph_reader: RED — test `degree()` on missing id raises KeyError — DoD: test fails
- [x] **P1** `PHASE2-038` graph_reader: GREEN — implement KeyError for degree miss — DoD: test passes
- [x] **P0** `PHASE2-039` graph_reader: RED — test `all_nodes()` items carry computed `degree` field — DoD: test fails
- [x] **P0** `PHASE2-040` graph_reader: GREEN — populate degree into NodeView — DoD: test passes

### 2.4 — betweenness

- [x] **P0** `PHASE2-041` graph_reader: RED — test `betweenness("polygons_polygons_polygon")` ≈ 0.056 (highest bridge) — DoD: test fails; ref PRD behavior §3
- [x] **P0** `PHASE2-042` graph_reader: GREEN — implement `betweenness(node_id)` via `networkx.betweenness_centrality` — DoD: test passes within tolerance
- [ ] **P0** `PHASE2-043` graph_reader: RED — test `betweenness()` is highest for the Polygon node across all nodes — DoD: test fails
- [ ] **P0** `PHASE2-044` graph_reader: GREEN — betweenness covered — DoD: test passes
- [x] **P1** `PHASE2-045` graph_reader: GREEN — populate betweenness into NodeView — DoD: NodeView.betweenness set
- [x] **P1** `PHASE2-046` graph_reader: REFACTOR — cache betweenness computation (compute once) — DoD: metrics.py ≤150 lines, single compute

### 2.5 — GR-T3 top-N by degree

- [x] **P0** `PHASE2-047` graph_reader: RED — test `top_n_by_degree(1)[0].id == "polygons_polygons_polygon"` and label "Polygon" — DoD: test fails; ref GR-T3
- [x] **P0** `PHASE2-048` graph_reader: GREEN — implement `top_n_by_degree(n)` sorted (degree DESC, betweenness DESC, id ASC) — DoD: GR-T3 passes
- [x] **P0** `PHASE2-049` graph_reader: RED — test tie-break order deterministic (betweenness DESC then id ASC) — DoD: test fails; ref interface tie-break note
- [x] **P0** `PHASE2-050` graph_reader: GREEN — implement deterministic tie-break — DoD: test passes
- [ ] **P1** `PHASE2-051` graph_reader: RED — test `top_n_by_degree(n)` with n > 23 returns all 23, no padding — DoD: test fails; ref edge case n > node count
- [ ] **P1** `PHASE2-052` graph_reader: GREEN — implement no-padding behavior — DoD: test passes
- [x] **P0** `PHASE2-053` graph_reader: RED — test `top_n_by_betweenness(1)[0]` is the Polygon bridge node — DoD: test fails
- [x] **P0** `PHASE2-054` graph_reader: GREEN — implement `top_n_by_betweenness(n)` — DoD: test passes
- [ ] **P1** `PHASE2-055` graph_reader: RED — test isolated `license_mit_license` still returned deterministically via id tie-break — DoD: test fails; ref edge case isolated node
- [ ] **P1** `PHASE2-056` graph_reader: GREEN — ensure isolated node never crashes ranking — DoD: test passes

### 2.6 — GR-T4 community grouping

- [x] **P0** `PHASE2-057` graph_reader: RED — test `nodes_in_community(1)` ids == {polygons_polygons, polygons_polygons_draw_polygon, rationale_18, rationale_33, rationale_50} — DoD: test fails; ref GR-T4
- [x] **P0** `PHASE2-058` graph_reader: GREEN — implement `nodes_in_community(community)` — DoD: GR-T4 passes
- [x] **P0** `PHASE2-059` graph_reader: RED — test `communities()` returns dict with keys 0..5 — DoD: test fails; ref behavior §4
- [x] **P0** `PHASE2-060` graph_reader: GREEN — implement `communities()` bucketing — DoD: test passes
- [ ] **P1** `PHASE2-061` graph_reader: RED — test `nodes_in_community(4)` contains Polygon, object, __init__, calc_polygon_details — DoD: test fails; ref signal 1 Community 4
- [ ] **P1** `PHASE2-062` graph_reader: GREEN — community grouping covered — DoD: test passes
- [ ] **P1** `PHASE2-063` graph_reader: RED — test `nodes_in_community(99)` returns `[]` (no crash) — DoD: test fails
- [ ] **P1** `PHASE2-064` graph_reader: GREEN — implement empty-community tolerance — DoD: test passes

### 2.7 — GR-T5/T6/T7 confidence filtering

- [x] **P0** `PHASE2-065` graph_reader: RED — test `edges_with_confidence("INFERRED")` returns exactly 2 edges — DoD: test fails; ref GR-T5
- [x] **P0** `PHASE2-066` graph_reader: GREEN — implement `edges_with_confidence(level)` — DoD: GR-T5 count passes
- [x] **P0** `PHASE2-067` graph_reader: RED — test the 2 INFERRED edges are the mathsquiz_final→mathsquiz (0.8) and readme_maths_quiz→readme_broken_python (0.9) — DoD: test fails; ref GR-T5
- [x] **P0** `PHASE2-068` graph_reader: GREEN — edge identity covered — DoD: test passes
- [x] **P0** `PHASE2-069` graph_reader: RED — test `inferred_edges_below(0.85)` returns exactly 1 (the 0.8 semantically_similar_to) — DoD: test fails; ref GR-T6
- [x] **P0** `PHASE2-070` graph_reader: GREEN — implement `inferred_edges_below(threshold)` (INFERRED and score < threshold) — DoD: GR-T6 passes
- [x] **P0** `PHASE2-071` graph_reader: RED — test `edges_with_confidence("AMBIGUOUS")` returns `[]` (not raise) — DoD: test fails; ref GR-T7
- [x] **P0** `PHASE2-072` graph_reader: GREEN — implement AMBIGUOUS-empty tolerance — DoD: GR-T7 passes
- [x] **P0** `PHASE2-073` graph_reader: RED — test `edges_with_confidence("EXTRACTED")` returns 18 edges (90% of 20) — DoD: test fails
- [x] **P0** `PHASE2-074` graph_reader: GREEN — EXTRACTED filter covered — DoD: test passes
- [x] **P1** `PHASE2-075` graph_reader: REFACTOR — keep `filters.py` ≤150 lines — DoD: file budget honored

### 2.8 — edges_of + edge-case coverage

- [x] **P0** `PHASE2-076` graph_reader: RED — test `edges_of("polygons_polygons_polygon")` returns its 4 incident edges — DoD: test fails
- [x] **P0** `PHASE2-077` graph_reader: GREEN — implement `edges_of(node_id)` — DoD: test passes
- [ ] **P1** `PHASE2-078` graph_reader: RED — test `edges_of` on isolated node returns its single edge — DoD: test fails
- [ ] **P1** `PHASE2-079` graph_reader: GREEN — edges_of isolated covered — DoD: test passes
- [ ] **P1** `PHASE2-080` graph_reader: RED — test duplicate labels (welcome_message ×2) addressed by distinct ids — DoD: test fails; ref edge case duplicate labels
- [ ] **P1** `PHASE2-081` graph_reader: GREEN — ensure node keying by id not label — DoD: test passes
- [x] **P1** `PHASE2-082` graph_reader: RED — test EdgeView accepts null `source_location` — DoD: test fails
- [x] **P1** `PHASE2-083` graph_reader: GREEN — implement null-tolerant EdgeView — DoD: test passes
- [ ] **P2** `PHASE2-084` graph_reader: REFACTOR — extract shared sort helper for top_n_by_* — DoD: no duplicated sort logic
- [x] **P1** `PHASE2-085` graph_reader: verify — `mypy --strict` clean on graph_reader package — DoD: 0 errors
- [x] **P1** `PHASE2-086` graph_reader: verify — `ruff check` clean on graph_reader package — DoD: 0 violations
- [x] **P1** `PHASE2-087` graph_reader: verify — coverage ≥90% for graph_reader package — DoD: cov report green
- [ ] **P1** `PHASE2-088` graph_reader: commit — `feat: graph_reader query layer (GR-T1..7)` — DoD: tests committed with code; Conventional Commits

### 2.9 — obsidian_writer ranking (OW-T1..T3)

- [x] **P0** `PHASE2-089` obsidian_writer: RED — test `ObsidianWriter(reader)` constructs with injected GraphReader — DoD: test fails; ref PRD interface
- [x] **P0** `PHASE2-090` obsidian_writer: GREEN — implement `ObsidianWriter.__init__(reader, vault_dir)` — DoD: test passes
- [x] **P0** `PHASE2-091` obsidian_writer: RED — test `rank_hot_nodes(5)[0].id == "polygons_polygons_polygon"` — DoD: test fails; ref OW-T1
- [x] **P0** `PHASE2-092` obsidian_writer: GREEN — implement `rank_hot_nodes` sorted (degree DESC, betweenness DESC, id ASC) — DoD: OW-T1 passes; ref R5.6.1
- [x] **P0** `PHASE2-093` obsidian_writer: RED — test `rank_hot_nodes(5)` returns exactly 5 nodes — DoD: test fails
- [x] **P0** `PHASE2-094` obsidian_writer: GREEN — top_k truncation covered — DoD: test passes
- [x] **P0** `PHASE2-095` obsidian_writer: RED — test `wikilink(polygon_node) == "[[polygons_polygons_polygon|Polygon]]"` — DoD: test fails; ref OW-T2
- [x] **P0** `PHASE2-096` obsidian_writer: GREEN — implement `wikilink(node)` = `f"[[{node.id}|{node.label}]]"` — DoD: OW-T2 passes
- [x] **P0** `PHASE2-097` obsidian_writer: RED — test `render_hot_md(5)` contains `[[polygons_polygons_polygon|Polygon]]` — DoD: test fails; ref OW-T3
- [x] **P0** `PHASE2-098` obsidian_writer: GREEN — implement `render_hot_md` with heading + ordered list — DoD: OW-T3 link assertion passes
- [x] **P0** `PHASE2-099` obsidian_writer: RED — test `render_hot_md` output discloses metric line (degree DESC, betweenness DESC) — DoD: test fails; ref OW-T3 / R5.6.1
- [x] **P0** `PHASE2-100` obsidian_writer: GREEN — implement metric-disclosure line — DoD: test passes
- [x] **P1** `PHASE2-101` obsidian_writer: RED — test each list item shows `degree=D · bw=B · community=C · source_file:loc` — DoD: test fails; ref behavior §3
- [x] **P1** `PHASE2-102` obsidian_writer: GREEN — implement per-item metadata rendering — DoD: test passes
- [x] **P1** `PHASE2-103` obsidian_writer: RED — test null `source_location` rendered gracefully (omit `:Lxx`) — DoD: test fails; ref edge case null loc
- [x] **P1** `PHASE2-104` obsidian_writer: GREEN — implement graceful null-loc rendering — DoD: test passes

### 2.10 — obsidian_writer write + baseline safety (OW-T4/T5)

- [x] **P0** `PHASE2-105` obsidian_writer: RED — test `write_hot_md()` creates `obsidian/hot.md` and returns its path — DoD: test fails; ref OW-T4 (use temp vault dir)
- [x] **P0** `PHASE2-106` obsidian_writer: GREEN — implement `write_hot_md(top_k)` writing to vault dir — DoD: test passes
- [x] **P0** `PHASE2-107` obsidian_writer: RED — test writing twice is byte-identical (deterministic) — DoD: test fails; ref OW-T4
- [x] **P0** `PHASE2-108` obsidian_writer: GREEN — ensure deterministic output (stable ordering, no timestamps) — DoD: OW-T4 passes
- [x] **P0** `PHASE2-109` obsidian_writer: RED — test `write_hot_md()` leaves `index.md` + `polygons_polygons_polygon.md` mtime/hash unchanged — DoD: test fails; ref OW-T5
- [x] **P0** `PHASE2-110` obsidian_writer: GREEN — ensure only `hot.md` is written (baselines untouched) — DoD: OW-T5 passes; ref brief §6
- [x] **P1** `PHASE2-111` obsidian_writer: RED — test `write_hot_md` never overwrites `graph.json`/`GRAPH_REPORT.md` — DoD: test fails
- [x] **P1** `PHASE2-112` obsidian_writer: GREEN — restrict writer to hot.md only — DoD: test passes
- [x] **P1** `PHASE2-113` obsidian_writer: REFACTOR — keep `hot.py` ≤150 lines — DoD: file budget honored
- [ ] **P2** `PHASE2-114` obsidian_writer: RED — test `render_node_note` produces wikilinked note (for consistency checks) — DoD: test fails; ref notes.py
- [ ] **P2** `PHASE2-115` obsidian_writer: GREEN — implement `render_node_note(node, neighbors)` — DoD: test passes
- [ ] **P2** `PHASE2-116` obsidian_writer: RED — test `render_index` lists 6 communities + all nodes as wikilinks — DoD: test fails; ref R5.1.3
- [ ] **P2** `PHASE2-117` obsidian_writer: GREEN — implement `render_index` — DoD: test passes
- [x] **P1** `PHASE2-118` obsidian_writer: verify — mypy/ruff clean, coverage ≥90% on obsidian_writer — DoD: gates green
- [x] **P1** `PHASE2-119` obsidian_writer: commit — `feat: obsidian_writer hot.md ranking (OW-T1..5)` — DoD: tests with code
- [x] **P1** `PHASE2-120` graph_reader/obsidian_writer: wire into `sdk.py` (`load_graph`, `generate_hot` façade methods) — DoD: sdk delegates, no logic in sdk
- [x] **P1** `PHASE2-121` graph_reader/obsidian_writer: REFACTOR pass — confirm no module re-parses graph.json except graph_reader — DoD: single read path (R5.2.1)

---

## Phase 3 — weakness_detector (TDD)

> One RED/GREEN pair per signal (1–6) per WD-T1..8, plus hypothesis/SourceValidation
> scaffolding, ranking, language↔tag invariant, thresholds config, and gatekeeper base
> (built here per ADR-0002 before agent Phase 5).

### 3.1 — hypothesis model + thresholds

- [x] **P0** `PHASE3-001` weakness_detector: RED — test `SourceValidation(confirmed, note)` dataclass exists — DoD: test fails; ref interface
- [x] **P0** `PHASE3-002` weakness_detector: GREEN — implement `SourceValidation` dataclass — DoD: test passes
- [x] **P0** `PHASE3-003` weakness_detector: RED — test `WeaknessFinding` has signal/tag/hypothesis/priority/source_file/nodes/edges/source_validation — DoD: test fails
- [x] **P0** `PHASE3-004` weakness_detector: GREEN — implement `WeaknessFinding` dataclass with `source_validation=None` default — DoD: test passes
- [x] **P0** `PHASE3-005` weakness_detector: RED — test `tag` constrained to Literal[EXTRACTED,INFERRED,AMBIGUOUS] — DoD: mypy/test fails
- [x] **P0** `PHASE3-006` weakness_detector: GREEN — implement Tag/Priority Literals — DoD: test passes
- [x] **P0** `PHASE3-007` weakness_detector: RED — test `WeaknessDetector(reader, thresholds_path)` loads `config/weakness_thresholds.json` — DoD: test fails
- [x] **P0** `PHASE3-008` weakness_detector: GREEN — implement `WeaknessDetector.__init__` loading thresholds — DoD: test passes
- [x] **P0** `PHASE3-009` weakness_detector: RED — test missing thresholds config fails loud (clear error) — DoD: test fails; ref WD-E5
- [x] **P0** `PHASE3-010` weakness_detector: GREEN — implement fail-loud on missing config — DoD: test passes
- [x] **P1** `PHASE3-011` weakness_detector: REFACTOR — keep `hypothesis.py` ≤150 lines — DoD: file budget honored

### 3.2 — Signal 1 god node (WD-T1)

- [x] **P0** `PHASE3-012` weakness_detector: RED — test `signal_1_god_node()` returns a finding with signal==1 — DoD: test fails with AttributeError; ref WD-T1
- [x] **P0** `PHASE3-013` weakness_detector: GREEN — implement `signal_1_god_node()` (degree >= god_node_min_degree) — DoD: test passes
- [x] **P0** `PHASE3-014` weakness_detector: RED — test finding has `"polygons_polygons_polygon" in nodes` — DoD: test fails; ref WD-T1
- [x] **P0** `PHASE3-015` weakness_detector: GREEN — node identity covered — DoD: test passes
- [x] **P0** `PHASE3-016` weakness_detector: RED — test `tag=="EXTRACTED"` and `priority=="primary"` — DoD: test fails; ref WD-T1
- [x] **P0** `PHASE3-017` weakness_detector: GREEN — set EXTRACTED/primary on signal 1 — DoD: test passes
- [x] **P0** `PHASE3-018` weakness_detector: RED — test hypothesis text contains "Polygon" and uses "is"/"bridges" (no "may") — DoD: test fails; ref WD-T1
- [x] **P0** `PHASE3-019` weakness_detector: GREEN — author EXTRACTED-language hypothesis string — DoD: test passes
- [x] **P1** `PHASE3-020` weakness_detector: RED — test threshold-driven: god_node_min_degree from config (not hardcoded 4) — DoD: test fails
- [x] **P1** `PHASE3-021` weakness_detector: GREEN — read threshold from config — DoD: test passes
- [x] **P1** `PHASE3-022` weakness_detector: RED — test `source_file == "polygons/polygons.py"` on the finding — DoD: test fails; ref AW-T4
- [x] **P1** `PHASE3-023` weakness_detector: GREEN — set source_file on finding — DoD: test passes

### 3.3 — Signal 2 ambiguous/inferred edge (WD-T3)

- [x] **P0** `PHASE3-024` weakness_detector: RED — test `signal_2_ambiguous_edge()` returns ≥1 finding tag=="INFERRED" — DoD: test fails; ref WD-T3
- [x] **P0** `PHASE3-025` weakness_detector: GREEN — implement `signal_2_ambiguous_edge()` over `edges_with_confidence("INFERRED")` ≤ ambiguous_confidence_max — DoD: test passes
- [x] **P0** `PHASE3-026` weakness_detector: RED — test finding `priority=="secondary"` — DoD: test fails; ref WD-T3
- [x] **P0** `PHASE3-027` weakness_detector: GREEN — set secondary priority — DoD: test passes
- [x] **P0** `PHASE3-028` weakness_detector: RED — test references `mathsquiz_readme_maths_quiz→readme_broken_python` edge — DoD: test fails; ref WD-T3
- [x] **P0** `PHASE3-029` weakness_detector: GREEN — populate edge endpoints — DoD: test passes
- [x] **P0** `PHASE3-030` weakness_detector: RED — test hypothesis uses "suggests"/"may" (INFERRED language) — DoD: test fails; ref WD-T3
- [x] **P0** `PHASE3-031` weakness_detector: GREEN — author INFERRED-language hypothesis — DoD: test passes
- [x] **P0** `PHASE3-032` weakness_detector: RED — test signal 2 does not crash on 0 AMBIGUOUS edges — DoD: test fails; ref WD-E2
- [x] **P0** `PHASE3-033` weakness_detector: GREEN — implement AMBIGUOUS-empty tolerance — DoD: test passes

### 3.4 — Signal 3 broken/missing path (WD-T4)

- [x] **P0** `PHASE3-034` weakness_detector: RED — test `signal_3_broken_path()` references `mathsquiz_mathsquiz_final_py` — DoD: test fails; ref WD-T4
- [x] **P0** `PHASE3-035` weakness_detector: GREEN — implement `signal_3_broken_path(repo_root)` (referenced node whose source_file is absent) — DoD: test passes
- [x] **P0** `PHASE3-036` weakness_detector: RED — test finding `priority=="secondary"` — DoD: test fails; ref WD-T4
- [x] **P0** `PHASE3-037` weakness_detector: GREEN — set secondary priority — DoD: test passes
- [x] **P0** `PHASE3-038` weakness_detector: RED — test existence check resolves relative to `data/broken-python/`, not repo root — DoD: test fails; ref WD-E4
- [x] **P0** `PHASE3-039` weakness_detector: GREEN — implement repo-root-relative path resolution — DoD: test passes
- [x] **P1** `PHASE3-040` weakness_detector: RED — test no raise when whole `mathsquiz/` dir absent — DoD: test fails; ref WD-E4
- [x] **P1** `PHASE3-041` weakness_detector: GREEN — implement missing-dir tolerance — DoD: test passes
- [x] **P1** `PHASE3-042` weakness_detector: RED — test hypothesis states file "is" referenced but "is" absent (EXTRACTED about edge) — DoD: test fails
- [x] **P1** `PHASE3-043` weakness_detector: GREEN — author signal-3 hypothesis — DoD: test passes

### 3.5 — Signal 4 critical-path break

- [x] **P0** `PHASE3-044` weakness_detector: RED — test `signal_4_critical_path_break()` fires on calc_polygon_details/draw_polygon (no sides>=3 guard) — DoD: test fails; ref signal 4
- [x] **P0** `PHASE3-045` weakness_detector: GREEN — implement `signal_4_critical_path_break()` — DoD: test passes
- [x] **P0** `PHASE3-046` weakness_detector: RED — test `tag=="INFERRED"`, `priority=="secondary"` — DoD: test fails
- [x] **P0** `PHASE3-047` weakness_detector: GREEN — set INFERRED/secondary — DoD: test passes
- [x] **P0** `PHASE3-048` weakness_detector: RED — test hypothesis uses "may" and mentions OOP-summary-only — DoD: test fails; ref signal 4 language
- [x] **P0** `PHASE3-049` weakness_detector: GREEN — author signal-4 hypothesis — DoD: test passes

### 3.6 — Signal 5 isolated cluster (WD-T2)

- [x] **P0** `PHASE3-050` weakness_detector: RED — test `signal_5_isolated_cluster()` nodes == {rationale_18, rationale_33, rationale_50} — DoD: test fails; ref WD-T2
- [x] **P0** `PHASE3-051` weakness_detector: GREEN — implement `signal_5_isolated_cluster()` (degree ≤ isolated_cluster_max_edges, no tested_by) — DoD: test passes
- [x] **P0** `PHASE3-052` weakness_detector: RED — test `tag=="EXTRACTED"`, `priority=="primary"` — DoD: test fails; ref WD-T2
- [x] **P0** `PHASE3-053` weakness_detector: GREEN — set EXTRACTED/primary — DoD: test passes
- [x] **P0** `PHASE3-054` weakness_detector: RED — test hypothesis: TODOs "are" the bug (EXTRACTED, no hedge) — DoD: test fails; ref WD-T2
- [x] **P0** `PHASE3-055` weakness_detector: GREEN — author signal-5 hypothesis — DoD: test passes
- [x] **P1** `PHASE3-056` weakness_detector: RED — test grouping by community (Community 1) — DoD: test fails
- [x] **P1** `PHASE3-057` weakness_detector: GREEN — implement community grouping in signal 5 — DoD: test passes
- [x] **P1** `PHASE3-058` weakness_detector: RED — test threshold isolated_cluster_max_edges read from config — DoD: test fails
- [x] **P1** `PHASE3-059` weakness_detector: GREEN — config-driven threshold — DoD: test passes

### 3.7 — Signal 6 semantic duplicate + source-read (WD-T5)

- [x] **P0** `PHASE3-060` weakness_detector: RED — test `signal_6_semantic_duplicate()` returns finding signal==6 referencing polygon_init + calc_polygon_details — DoD: test fails; ref WD-T5
- [x] **P0** `PHASE3-061` weakness_detector: GREEN — implement `signal_6_semantic_duplicate()` structural detection (both nodes Community 4, same source_file) — DoD: test passes
- [x] **P0** `PHASE3-062` weakness_detector: RED — test pre-read `tag=="AMBIGUOUS"` — DoD: test fails; ref WD-T5
- [x] **P0** `PHASE3-063` weakness_detector: GREEN — set AMBIGUOUS tag pre-read — DoD: test passes
- [x] **P0** `PHASE3-064` weakness_detector: RED — test hypothesis contains "manual ... check" (AMBIGUOUS language) — DoD: test fails; ref WD-T5
- [x] **P0** `PHASE3-065` weakness_detector: GREEN — author AMBIGUOUS-language hypothesis — DoD: test passes
- [x] **P0** `PHASE3-066` weakness_detector: RED — test detector demonstrably opens `polygons/polygons.py` (source-read occurred / fields compared) — DoD: test fails; ref WD-T5 / WD-E1
- [x] **P0** `PHASE3-067` weakness_detector: GREEN — implement the disclosed Signal-6 source-peek (read + compare dict keys vs __init__ fields) — DoD: test passes
- [x] **P1** `PHASE3-068` weakness_detector: RED — test source-read compares `sides`/`internal_angles_sum`/`internal_angle(s)` fields — DoD: test fails; ref behavior §6
- [x] **P1** `PHASE3-069` weakness_detector: GREEN — implement field comparison — DoD: test passes
- [x] **P1** `PHASE3-070` weakness_detector: RED — test signal 6 addresses nodes by id not label — DoD: test fails; ref WD-E3
- [x] **P1** `PHASE3-071` weakness_detector: GREEN — ensure id-keyed access — DoD: test passes

### 3.8 — detect() orchestration + ranking (WD-T6/T7/T8)

- [x] **P0** `PHASE3-072` weakness_detector: RED — test `detect()` runs all six and returns ranked list — DoD: test fails; ref interface
- [x] **P0** `PHASE3-073` weakness_detector: GREEN — implement `detect()` calling all six signals — DoD: test passes
- [x] **P0** `PHASE3-074` weakness_detector: RED — test first finding `priority=="primary"` and is one of signals {1,5,6} — DoD: test fails; ref WD-T6
- [x] **P0** `PHASE3-075` weakness_detector: GREEN — implement primary-above-secondary ranking — DoD: WD-T6 passes
- [x] **P0** `PHASE3-076` weakness_detector: RED — test mathsquiz signals (2,3) rank below as secondary — DoD: test fails; ref WD-T6
- [x] **P0** `PHASE3-077` weakness_detector: GREEN — implement within-band ordering (degree DESC / confidence ASC) — DoD: test passes
- [x] **P0** `PHASE3-078` weakness_detector: RED — test EXTRACTED findings contain no hedge ("may"/"suggests") — DoD: test fails; ref WD-T7
- [x] **P0** `PHASE3-079` weakness_detector: GREEN — enforce language↔tag invariant for EXTRACTED — DoD: test passes
- [x] **P0** `PHASE3-080` weakness_detector: RED — test INFERRED findings contain a hedge — DoD: test fails; ref WD-T7
- [x] **P0** `PHASE3-081` weakness_detector: GREEN — enforce hedge in INFERRED — DoD: test passes
- [x] **P0** `PHASE3-082` weakness_detector: RED — test AMBIGUOUS findings contain "manual check required" — DoD: test fails; ref WD-T7
- [x] **P0** `PHASE3-083` weakness_detector: GREEN — enforce AMBIGUOUS phrasing — DoD: test passes
- [x] **P0** `PHASE3-084` weakness_detector: RED — test every `detect()` finding has `source_validation is None` — DoD: test fails; ref WD-T8
- [x] **P0** `PHASE3-085` weakness_detector: GREEN — ensure detector never fills source_validation — DoD: WD-T8 passes
- [x] **P1** `PHASE3-086` weakness_detector: REFACTOR — split signals across files if `signals.py` > 150 lines — DoD: file budget honored
- [x] **P1** `PHASE3-087` weakness_detector: REFACTOR — keep `detector.py` ≤150 lines — DoD: file budget honored
- [x] **P1** `PHASE3-088` weakness_detector: verify — mypy/ruff clean, coverage ≥90% on weakness_detector — DoD: gates green
- [x] **P1** `PHASE3-089` weakness_detector: wire `detect_weaknesses` into `sdk.py` façade — DoD: sdk delegates, no logic
- [x] **P1** `PHASE3-090` weakness_detector: commit — `feat: six-signal weakness_detector (WD-T1..8)` — DoD: tests with code

### 3.9 — gatekeeper base (ADR-0002) built before agent

- [x] **P0** `PHASE3-091` gatekeeper: RED — test `TokenRecord` dataclass has run_id/run_type/node/input_tokens/output_tokens/model — DoD: test fails; ref PLAN.md §4.5
- [x] **P0** `PHASE3-092` gatekeeper: GREEN — implement `TokenRecord` — DoD: test passes
- [x] **P0** `PHASE3-093` gatekeeper: RED — test `TokenLogger.record(r)` appends a record — DoD: test fails
- [x] **P0** `PHASE3-094` gatekeeper: GREEN — implement `TokenLogger.record` — DoD: test passes
- [x] **P0** `PHASE3-095` gatekeeper: RED — test `TokenLogger.dump(path)` writes JSONL to `artifacts/runs/<run_id>.jsonl` — DoD: test fails
- [x] **P0** `PHASE3-096` gatekeeper: GREEN — implement `TokenLogger.dump` — DoD: test passes
- [x] **P0** `PHASE3-097` gatekeeper: RED — test `Gatekeeper(cfg, logger)` constructs from `config/agent.json` — DoD: test fails
- [x] **P0** `PHASE3-098` gatekeeper: GREEN — implement `Gatekeeper.__init__` (model/rate-limit/retry from config) — DoD: test passes
- [x] **P0** `PHASE3-099` gatekeeper: RED — test `call(messages, system, run_id, node)` returns LLMResponse and records tokens — DoD: test fails (mocked client)
- [x] **P0** `PHASE3-100` gatekeeper: GREEN — implement `call()` wrapping the (mocked) provider client behind a provider-agnostic interface, recording TokenRecord tagged {run_type,node} — DoD: test passes; ref ADR-0002
- [x] **P0** `PHASE3-101` gatekeeper: RED — test keyless mode (no provider key present) injects/uses mock client — DoD: test fails; ref ADR-0005 / AW-E3
- [x] **P0** `PHASE3-102` gatekeeper: GREEN — implement mock-client selection when key absent — DoD: test passes
- [x] **P0** `PHASE3-103` gatekeeper: RED — test the provider API key (env var named by `config/agent.json` `api_key_env`) is read from `os.environ` only (never from config files) — DoD: test fails; ref CLAUDE.md §3
- [x] **P0** `PHASE3-104` gatekeeper: GREEN — implement env-only secret read — DoD: test passes
- [x] **P1** `PHASE3-105` gatekeeper: RED — test retry-with-backoff on simulated rate-limit error — DoD: test fails
- [x] **P1** `PHASE3-106` gatekeeper: GREEN — implement retry/backoff per config — DoD: test passes
- [x] **P1** `PHASE3-107` gatekeeper: RED — test request queueing respects rate-limit config — DoD: test fails
- [x] **P1** `PHASE3-108` gatekeeper: GREEN — implement queue/rate-limit — DoD: test passes
- [x] **P1** `PHASE3-109` gatekeeper: RED — test structured log entry per call — DoD: test fails
- [x] **P1** `PHASE3-110` gatekeeper: GREEN — implement structured logging — DoD: test passes
- [x] **P1** `PHASE3-111` gatekeeper: RED — test no module bypasses gatekeeper (single seam assertion) — DoD: test fails
- [x] **P1** `PHASE3-112` gatekeeper: GREEN — document/assert single choke point — DoD: test passes; ref ADR-0002
- [x] **P1** `PHASE3-113` gatekeeper: REFACTOR — keep `client.py` + `token_log.py` ≤150 lines each — DoD: file budget honored
- [x] **P1** `PHASE3-114` gatekeeper: verify — mypy/ruff clean, coverage ≥90% on gatekeeper — DoD: gates green
- [x] **P1** `PHASE3-115` gatekeeper: commit — `feat: gatekeeper choke point + token logging (ADR-0002)` — DoD: tests with code
- [ ] **P2** `PHASE3-116` weakness_detector: RED — test `detect()` is deterministic across runs (stable ordering) — DoD: test fails
- [ ] **P2** `PHASE3-117` weakness_detector: GREEN — ensure deterministic ordering — DoD: test passes
- [ ] **P2** `PHASE3-118` weakness_detector: RED — test full six-signal convergence on the Polygon root cause (integration) — DoD: signals {1,5,6} all point at polygons.py; ref R4.5

---

## Phase 4 — Obsidian vault build

> `obsidian_writer` already unit-tested (Phase 2). Phase 4 = generate the real PRE-FIX
> `obsidian/hot.md`, verify wikilink consistency with existing vault, commit it as an artifact.

- [x] **P0** `PHASE4-001` vault: run `ObsidianWriter.write_hot_md()` against PRE-FIX `artifacts/graphify/graph.json` → `obsidian/hot.md` — DoD: file created; ref R5.1.4
- [x] **P0** `PHASE4-002` vault: verify `hot.md` top entry is `[[polygons_polygons_polygon|Polygon]]` (degree 4) — DoD: matches OW-T1; ref R5.6.1
- [x] **P0** `PHASE4-003` vault: verify `hot.md` discloses the ranking metric (degree DESC, betweenness DESC) — DoD: metric line present; ref R5.6.1
- [x] **P0** `PHASE4-004` vault: verify every wikilink in `hot.md` resolves to an existing `obsidian/<id>.md` note — DoD: all 5 targets exist; no dangling links
- [x] **P0** `PHASE4-005` vault: verify `hot.md` is distinct from `index.md` (prioritized subset, not a copy) — DoD: content differs; ref R5.1.4
- [x] **P0** `PHASE4-006` vault: confirm PRE-FIX baselines (`graph.json`, `GRAPH_REPORT.md`, `index.md`, per-node notes) unmodified by the run — DoD: mtime/hash unchanged; ref brief §6
- [x] **P1** `PHASE4-007` vault: verify `index.md` lists all 6 communities (0–5) — DoD: each community section present; ref R5.1.3
- [x] **P1** `PHASE4-008` vault: verify `index.md` lists all 23 nodes as wikilinks — DoD: 23 `[[...]]` entries; ref R5.1.2
- [x] **P1** `PHASE4-009` vault: spot-check per-node note `polygons_polygons_polygon.md` has wikilinks to its 4 neighbors — DoD: neighbor links present; ref R5.1.2
- [x] **P1** `PHASE4-010` vault: cross-check `hot.md` node count == `top_k` config value — DoD: matches config
- [x] **P1** `PHASE4-011` vault: write a `scripts/check_vault_consistency.py` that asserts every `[[id]]` in index/hot resolves to a note file — DoD: script exits 0; ref CLAUDE.md vault-consistency TODO
- [x] **P1** `PHASE4-012` vault: add the consistency check to CI / pre-commit (keyless) — DoD: check runs in CI
- [x] **P1** `PHASE4-013` vault: RED — test consistency checker flags an intentionally-dangling wikilink — DoD: test fails then checker catches it
- [x] **P1** `PHASE4-014` vault: GREEN — checker correctly reports dangling link — DoD: test passes
- [x] **P0** `PHASE4-015` vault: commit `obsidian/hot.md` as a graded artifact — DoD: committed; `docs: add PRE-FIX hot.md (R5.1.4)`
- [x] **P1** `PHASE4-016` vault: document the hot.md metric in README §R8.3 stub — DoD: metric described
- [x] **P1** `PHASE4-017` vault: verify `hot.md` includes per-item `degree/bw/community/source_file:loc` metadata — DoD: present
- [x] **P1** `PHASE4-018` vault: confirm null `source_location` nodes (e.g. license) render gracefully if they appear — DoD: no `:None`
- [x] **P1** `PHASE4-019` vault: confirm `hot.md` excludes the isolated `license_mit_license` from the top-k (degree 1) unless k is large — DoD: ranking correct
- [ ] **P2** `PHASE4-020` vault: regenerate per-node notes to a SCRATCH dir and diff vs committed baseline (consistency, no overwrite) — DoD: scratch matches baseline structure
- [ ] **P2** `PHASE4-021` vault: confirm `obsidian_writer.write_hot_md` targets `obsidian/` for PRE-FIX and post-fix path for POST-FIX — DoD: path config-driven
- [x] **P1** `PHASE4-022` vault: verify deterministic re-render (byte-equal) supports clean R5.6.3 diff later — DoD: two renders identical; ref OW-T4
- [x] **P0** `PHASE4-023` vault: wire `generate_hot()` into `sdk.py` + `cli.py` command `ex04 hot` — DoD: `uv run ex04 hot` writes hot.md
- [x] **P1** `PHASE4-024` vault: RED — test `cli.py` `hot` command delegates to sdk only (zero logic) — DoD: test fails
- [x] **P1** `PHASE4-025` vault: GREEN — implement thin `hot` CLI command — DoD: test passes; ref SDK-first
- [x] **P1** `PHASE4-026` vault: verify `ex04 hot` is keyless (no LLM) — DoD: runs without API key
- [x] **P1** `PHASE4-027` vault: README link to `obsidian/index.md` + `obsidian/hot.md` — DoD: links present (R8.3)
- [ ] **P2** `PHASE4-028` vault: confirm wikilink format matches real vault (`[[id|Label]]`) exactly — DoD: spot-check 3 notes
- [ ] **P2** `PHASE4-029` vault: confirm no duplicate-label collisions in hot.md (id-keyed) — DoD: ids unique
- [x] **P1** `PHASE4-030` vault: verify `hot.md` ranks Community-4 abstractions above mathsquiz nodes — DoD: Polygon/calc_polygon_details rank high
- [x] **P1** `PHASE4-031` vault: confirm `hot.md` answers "where to look first" → polygons community — DoD: top entries all polygons; ref R1.4
- [x] **P1** `PHASE4-032` vault: commit consistency script + tests — DoD: `test: vault wikilink consistency`
- [ ] **P2** `PHASE4-033` vault: add an Obsidian graph-view note to README pointing at hot.md as entry — DoD: described (R10.3)
- [x] **P1** `PHASE4-034` vault: verify `hot.md` heading is `# Hot — Where to look first` — DoD: heading matches behavior §3
- [x] **P1** `PHASE4-035` vault: confirm `obsidian_writer` does NOT touch `graph.json` during hot generation — DoD: read-only on graph
- [ ] **P2** `PHASE4-036` vault: snapshot-test `hot.md` content for regression — DoD: golden file committed
- [x] **P1** `PHASE4-037` vault: ensure `hot.md` is reproducible from repo alone (config paths) — DoD: third-party rerun works; ref R1.5
- [x] **P1** `PHASE4-038` vault: document hot.md generation step in the end-to-end pipeline (R5.5.1) — DoD: pipeline stage 3 covered
- [ ] **P2** `PHASE4-039` vault: verify `hot.md` proximity-to-bug interpretation noted (betweenness as bridge proxy) — DoD: noted in metric disclosure
- [x] **P1** `PHASE4-040` vault: final keyless smoke: `ex04 hot` + consistency check both green — DoD: both pass
- [x] **P1** `PHASE4-041` vault: commit `feat: Phase 4 vault build complete` — DoD: hot.md + checks committed

---

## Phase 5 — LangGraph agent (TDD)

> State schema + each node as its own RED/GREEN(/REFACTOR) cycle per PRD_agent_workflow.md
> (AW-T1..8 + AW-E1..5). Both run types via one parameterized graph. Gatekeeper already built (Phase 3).

### 5.1 — typed state schema

- [x] **P0** `PHASE5-001` agent: RED — test `AgentState` TypedDict has run_type/messages/vault_context/dumped_context/current_hypothesis/validated_source/validated/findings_tried/fix_diff/token_usage — DoD: test fails; ref PRD state schema / R6.1.4
- [x] **P0** `PHASE5-002` agent: GREEN — implement `AgentState` TypedDict — DoD: test passes
- [x] **P0** `PHASE5-003` agent: RED — test `run_type` is Literal["graph_guided","naive"] — DoD: mypy/test fails
- [x] **P0** `PHASE5-004` agent: GREEN — implement Literal run_type — DoD: test passes
- [x] **P0** `PHASE5-005` agent: RED — test `TokenRecord` state type (node/input_tokens/output_tokens) — DoD: test fails
- [x] **P0** `PHASE5-006` agent: GREEN — implement TokenRecord in state — DoD: test passes
- [x] **P1** `PHASE5-007` agent: RED — test state is typed not ad-hoc dict (no untyped fields) — DoD: mypy strict fails on violation; ref R6.1.4
- [x] **P1** `PHASE5-008` agent: GREEN — finalize typed state — DoD: mypy clean
- [x] **P1** `PHASE5-009` agent: REFACTOR — keep `state.py` ≤150 lines — DoD: file budget honored

### 5.2 — plan node

- [x] **P0** `PHASE5-010` agent: RED — test `plan(state)` sets run_type and initializes state — DoD: test fails; ref PRD nodes
- [x] **P0** `PHASE5-011` agent: GREEN — implement `plan` node (tiny system prompt context) — DoD: test passes
- [x] **P0** `PHASE5-012` agent: RED — test `plan` routes graph_guided vs naive by run_type — DoD: test fails
- [x] **P0** `PHASE5-013` agent: GREEN — implement plan routing decision — DoD: test passes
- [x] **P1** `PHASE5-014` agent: RED — test `plan` LLM call goes through gatekeeper (token recorded) — DoD: test fails (mocked)
- [x] **P1** `PHASE5-015` agent: GREEN — route plan call via gatekeeper — DoD: test passes

### 5.3 — read_vault node (graph-guided)

- [x] **P0** `PHASE5-016` agent: RED — test `read_vault(state)` loads `index.md` + `hot.md` into `vault_context` — DoD: test fails; ref PRD read_vault
- [x] **P0** `PHASE5-017` agent: GREEN — implement `read_vault` (no source files read) — DoD: test passes; ref R5.3.2
- [x] **P0** `PHASE5-018` agent: RED — test `read_vault` reads NO source files — DoD: test fails; ref R1.3
- [x] **P0** `PHASE5-019` agent: GREEN — ensure no source reads in read_vault — DoD: test passes
- [x] **P0** `PHASE5-020` agent: RED — test `read_vault` fails loud if `hot.md` missing ("run obsidian_writer first") — DoD: test fails; ref AW-E2
- [x] **P0** `PHASE5-021` agent: GREEN — implement fail-loud-on-missing-hot.md (no silent dump fallback) — DoD: test passes
- [x] **P1** `PHASE5-022` agent: RED — test `vault_context` is non-empty and contains the Polygon wikilink — DoD: test fails
- [x] **P1** `PHASE5-023` agent: GREEN — populate vault_context correctly — DoD: test passes

### 5.4 — hypothesize node (AW-T4)

- [x] **P0** `PHASE5-024` agent: RED — test `hypothesize(state)` sets `current_hypothesis` to top-ranked finding — DoD: test fails; ref PRD hypothesize
- [x] **P0** `PHASE5-025` agent: GREEN — implement `hypothesize` calling `WeaknessDetector.detect()` — DoD: test passes
- [x] **P0** `PHASE5-026` agent: RED — test `current_hypothesis.source_file == "polygons/polygons.py"` and `priority=="primary"` — DoD: test fails; ref AW-T4
- [x] **P0** `PHASE5-027` agent: GREEN — select primary finding (Signal 1 Polygon) — DoD: AW-T4 passes
- [x] **P1** `PHASE5-028` agent: RED — test hypothesis carries EXTRACTED/INFERRED/AMBIGUOUS tag into state — DoD: test fails
- [x] **P1** `PHASE5-029` agent: GREEN — propagate tag into current_hypothesis — DoD: test passes
- [x] **P1** `PHASE5-030` agent: RED — test `hypothesize` LLM call routed via gatekeeper — DoD: test fails
- [x] **P1** `PHASE5-031` agent: GREEN — route hypothesize call via gatekeeper — DoD: test passes

### 5.5 — validate node (AW-T5, AW-T2)

- [x] **P0** `PHASE5-032` agent: RED — test `validate(state)` reads `current_hypothesis.source_file` into `validated_source` — DoD: test fails; ref PRD validate
- [x] **P0** `PHASE5-033` agent: GREEN — implement `validate` reading polygons.py (~76 lines) — DoD: test passes
- [x] **P0** `PHASE5-034` agent: RED — test `validated == True` and `current_hypothesis.source_validation is not None` after validate — DoD: test fails; ref AW-T5
- [x] **P0** `PHASE5-035` agent: GREEN — fill source_validation + set validated — DoD: AW-T5 passes
- [x] **P0** `PHASE5-036` agent: RED — test `validated_source` contains ONLY polygons.py (no mathsquiz content) — DoD: test fails; ref AW-T2
- [x] **P0** `PHASE5-037` agent: GREEN — restrict validate to single source file — DoD: AW-T2 passes
- [x] **P0** `PHASE5-038` agent: RED — test source contradicting hypothesis routes back to hypothesize — DoD: test fails; ref PLAN.md §3a
- [x] **P0** `PHASE5-039` agent: GREEN — implement re-hypothesize conditional edge — DoD: test passes
- [x] **P1** `PHASE5-040` agent: RED — test inference discipline: INFERRED/AMBIGUOUS not actionable until validated — DoD: test fails; ref brief §5
- [x] **P1** `PHASE5-041` agent: GREEN — gate fix on validated for INFERRED/AMBIGUOUS — DoD: test passes

### 5.6 — fix node (graph-guided)

- [x] **P0** `PHASE5-042` agent: RED — test `fix(state)` makes one gatekeeper LLM call with system+vault_context+validated_source+hypothesis — DoD: test fails; ref PRD fix
- [x] **P0** `PHASE5-043` agent: GREEN — implement `fix` node producing corrected content → `fix_diff` — DoD: test passes
- [x] **P0** `PHASE5-044` agent: RED — test no mathsquiz file content appears in any fix-node prompt (graph-guided) — DoD: test fails; ref AW-T2
- [x] **P0** `PHASE5-045` agent: GREEN — ensure minimal context at fix — DoD: AW-T2 passes
- [x] **P0** `PHASE5-046` agent: RED — test `fix_diff` is a unified diff vs original polygons.py — DoD: test fails
- [x] **P0** `PHASE5-047` agent: GREEN — implement unified-diff generation — DoD: test passes
- [x] **P1** `PHASE5-048` agent: RED — test empty/no usable diff → report records failure (no crash) — DoD: test fails; ref AW-E5
- [x] **P1** `PHASE5-049` agent: GREEN — handle empty-fix gracefully — DoD: test passes

### 5.7 — report node

- [x] **P0** `PHASE5-050` agent: RED — test `report(state)` summarizes root cause + finding + validation + diff — DoD: test fails; ref PRD report
- [x] **P0** `PHASE5-051` agent: GREEN — implement `report` node — DoD: test passes
- [x] **P1** `PHASE5-052` agent: RED — test report node makes no LLM call (no gatekeeper) — DoD: test fails
- [x] **P1** `PHASE5-053` agent: GREEN — ensure report is deterministic/no-LLM — DoD: test passes

### 5.8 — dump_repo node (naive, AW-T3)

- [x] **P0** `PHASE5-054` agent: RED — test `dump_repo(state)` reads all files under `data/broken-python/` into `dumped_context` — DoD: test fails; ref PRD dump_repo
- [x] **P0** `PHASE5-055` agent: GREEN — implement `dump_repo` (no graph, no hot.md) — DoD: test passes
- [x] **P0** `PHASE5-056` agent: RED — test `dumped_context` includes polygons.py + 5 mathsquiz scripts + 2 READMEs + LICENSE.txt — DoD: test fails; ref AW-T3
- [x] **P0** `PHASE5-057` agent: GREEN — ensure full-tree dump — DoD: AW-T3 passes
- [x] **P0** `PHASE5-058` agent: RED — test dump is deterministic (sorted paths) — DoD: test fails; ref AW-E4
- [x] **P0** `PHASE5-059` agent: GREEN — implement sorted-path concatenation — DoD: test passes
- [x] **P1** `PHASE5-060` agent: RED — test naive `fix` prompt = system + entire dumped_context (no hypothesis, no map) — DoD: test fails; ref context table
- [x] **P1** `PHASE5-061` agent: GREEN — implement naive fix context assembly — DoD: test passes

### 5.9 — graph_def + parameterization (AW-T8)

- [x] **P0** `PHASE5-062` agent: RED — test `build_graph("graph_guided")` compiles a CompiledGraph — DoD: test fails; ref PRD graph_def
- [x] **P0** `PHASE5-063` agent: GREEN — implement `build_graph` graph-guided topology (plan→read_vault→hypothesize→validate→fix→report) — DoD: test passes; ref R5.5.1
- [x] **P0** `PHASE5-064` agent: RED — test `build_graph("naive")` compiles (plan→dump_repo→fix→report) — DoD: test fails
- [x] **P0** `PHASE5-065` agent: GREEN — implement naive topology with conditional edges — DoD: test passes
- [x] **P0** `PHASE5-066` agent: RED — test both routes share the SAME plan/fix/report node objects (AW-T8) — DoD: test fails; ref AW-T8
- [x] **P0** `PHASE5-067` agent: GREEN — implement single parameterized graph (no duplicated node impls) — DoD: AW-T8 passes
- [x] **P1** `PHASE5-068` agent: RED — test conditional edge selects path by `run_type` — DoD: test fails
- [x] **P1** `PHASE5-069` agent: GREEN — implement run_type conditional routing — DoD: test passes
- [x] **P1** `PHASE5-070` agent: REFACTOR — keep `graph_def.py` ≤150 lines — DoD: file budget honored
- [x] **P1** `PHASE5-071` agent: REFACTOR — split `nodes.py` into nodes_graph/nodes_naive if > 150 lines — DoD: file budget honored

### 5.10 — stop conditions + AMBIGUOUS fall-through (AW-T6, AW-E1)

- [x] **P0** `PHASE5-072` agent: RED — test graph-guided stops after fix+report when `validated==True` — DoD: test fails; ref stop conditions
- [x] **P0** `PHASE5-073` agent: GREEN — implement validated-stop condition — DoD: test passes
- [x] **P0** `PHASE5-074` agent: RED — test AMBIGUOUS top finding that fails to confirm falls through to next finding (findings_tried++) — DoD: test fails; ref AW-E1
- [x] **P0** `PHASE5-075` agent: GREEN — implement fall-through to next-ranked finding — DoD: test passes
- [x] **P0** `PHASE5-076` agent: RED — test `findings_tried <= max_findings_tried` and graph terminates (no infinite loop) — DoD: test fails; ref AW-T6
- [x] **P0** `PHASE5-077` agent: GREEN — implement bounded loop (max_findings_tried from config) — DoD: AW-T6 passes
- [x] **P0** `PHASE5-078` agent: RED — test "no confirmable finding" report after exhausting findings — DoD: test fails; ref stop conditions
- [x] **P0** `PHASE5-079` agent: GREEN — implement exhaustion report — DoD: test passes
- [x] **P1** `PHASE5-080` agent: RED — test `max_validation_attempts` honored (default 1 from config) — DoD: test fails
- [x] **P1** `PHASE5-081` agent: GREEN — implement validation-attempt bound — DoD: test passes
- [x] **P0** `PHASE5-082` agent: RED — test naive stops after fix+report (single pass, no validation loop) — DoD: test fails; ref stop conditions
- [x] **P0** `PHASE5-083` agent: GREEN — implement single-pass naive stop — DoD: test passes

### 5.11 — context-minimization thesis (AW-T1)

- [x] **P0** `PHASE5-084` agent: RED — test `count_tokens(vault_context + validated_source) < count_tokens(dumped_context)` (structural, no real LLM) — DoD: test fails; ref AW-T1 (core thesis)
- [x] **P0** `PHASE5-085` agent: GREEN — confirm graph-guided context strictly smaller than naive dump — DoD: AW-T1 passes; ref R1.4
- [x] **P1** `PHASE5-086` agent: RED — test the context delta is at the fix node specifically — DoD: test fails; ref PRD context-minimization
- [x] **P1** `PHASE5-087` agent: GREEN — confirm fix-node context delta — DoD: test passes

### 5.12 — structural evals (`tests/evals/`, keyless, pass^k=100%) — promote the thesis

> The core thesis must not live as one buried unit test. Per the `eval-harness` skill,
> these are **known-answer, keyless invariants** that prove the system does the *right
> thing* (not just runs). They run in CI via `uv run pytest -m eval` and each must hold on
> **every** run (`pass^k = 100%`, not a statistical rate). This is the agent-debate
> credibility signature (structural evals + committed evidence) ported to EX04.

- [x] **P0** `PHASE5-E01` evals: create `tests/evals/test_thesis_context_delta.py` (`@pytest.mark.eval`) — the AW-T1 token-delta promoted to a first-class structural eval (graph-guided context < naive context, no API key) — DoD: eval passes; runs under `-m eval`; ref AW-T1/R1.4 (highest-leverage)
- [x] **P0** `PHASE5-E02` evals: create `tests/evals/test_known_answer_weakness.py` — known-answer eval against the REAL `artifacts/graphify/graph.json`: detector finds Signal 1 (god node = `polygons_polygons_polygon`, degree 4) AND Signal 5 (isolated cluster = the three `rationale_*` nodes) — DoD: both findings asserted; ref WD-T1/WD-T5, brief §2
- [x] **P0** `PHASE5-E03` evals: create `tests/evals/test_hot_ranks_god_node.py` — `obsidian/hot.md` ranks `polygons_polygons_polygon` at/near the top (PRE-FIX metric) — DoD: eval passes; ref OW-T*/R5.6.1
- [x] **P0** `PHASE5-E04` evals: create `tests/evals/test_graph_schema.py` — `graph.json` conforms to the PLAN.md data contract (node/edge fields, confidence ∈ {EXTRACTED,INFERRED,AMBIGUOUS}) — DoD: schema eval passes; ref PLAN.md data contract
- [x] **P0** `PHASE5-E05` evals: create `tests/evals/test_fixed_polygons_correct.py` — the correctness invariant (pentagon 540/108, hexagon 720/120; mocked-turtle loop depends on `sides`) as a known-answer eval — DoD: passes on a fixed-source fixture, fails on the original; ref TC-T4/TC-T5
- [x] **P1** `PHASE5-E06` evals: create `tests/evals/test_report_wellformed.py` — given mocked gatekeeper-log fixtures, `reports/token_comparison.md` has the mandated columns incl. `Files read` + `Iterations` (R5.6.5) — DoD: passes; ref TC-T9
- [x] **P1** `PHASE5-E07` evals: add a `tests/evals/README.md` documenting the structural/behavioural split + `pass^k=100%` bar + how to run (`-m eval`) — DoD: present; ref eval-harness skill
- [x] **P1** `PHASE5-E08` evals: ensure `tests/evals/` runs in CI keyless and is reported separately from unit tests — DoD: CI step `uv run pytest -m eval` green; ref PHASE1-071
- [x] **P1** `PHASE5-E09` evals: commit — `test(evals): keyless structural evals proving the graph-guided thesis (pass^k)` — DoD: evals + this section ticked

### 5.12 — token_usage from gatekeeper (AW-T7) + keyless (AW-E3)

- [x] **P0** `PHASE5-088` agent: RED — test `token_usage` has one TokenRecord per LLM call (node/input/output) — DoD: test fails; ref AW-T7
- [x] **P0** `PHASE5-089` agent: GREEN — append TokenRecord per gatekeeper call — DoD: AW-T7 passes
- [x] **P0** `PHASE5-090` agent: RED — test keyless run (no key) uses mocked response; routing + token-structure assertions hold — DoD: test fails; ref AW-E3
- [x] **P0** `PHASE5-091` agent: GREEN — confirm keyless graph routes via mocked gatekeeper — DoD: AW-E3 passes
- [x] **P1** `PHASE5-092` agent: RED — test `token_usage` reconciles against gatekeeper JSONL log — DoD: test fails; ref TC-E5
- [x] **P1** `PHASE5-093` agent: GREEN — ensure state mirrors gatekeeper log — DoD: test passes

### 5.13 — prompts + wiring + quality gates

- [x] **P1** `PHASE5-094` agent: RED — test `prompts.py` templates load as text (no logic) — DoD: test fails
- [x] **P1** `PHASE5-095` agent: GREEN — implement prompt templates (plan/hypothesize/fix) — DoD: test passes
- [x] **P1** `PHASE5-096` agent: RED — test model id loaded from `config/agent.json` (not hardcoded) — DoD: test fails; ref D6
- [x] **P1** `PHASE5-097` agent: GREEN — config-driven model in agent calls — DoD: test passes
- [x] **P1** `PHASE5-098` agent: REFACTOR — keep `prompts.py` + `nodes.py` ≤150 lines each — DoD: file budget honored
- [x] **P0** `PHASE5-099` agent: RED — test `sdk.run_agent("graph_guided")` runs end-to-end keyless — DoD: test fails
- [x] **P0** `PHASE5-100` agent: GREEN — wire `run_agent` into `sdk.py` — DoD: test passes
- [x] **P0** `PHASE5-101` agent: RED — test `sdk.run_agent("naive")` runs end-to-end keyless — DoD: test fails
- [x] **P0** `PHASE5-102` agent: GREEN — naive run via sdk — DoD: test passes
- [x] **P1** `PHASE5-103` agent: RED — test `cli.py` `run` command delegates to sdk (zero logic) — DoD: test fails
- [x] **P1** `PHASE5-104` agent: GREEN — implement thin `ex04 run --type` CLI — DoD: test passes; ref SDK-first
- [x] **P1** `PHASE5-105` agent: RED — test every node/tool is documented (R6.2.2 explainability) — DoD: docstrings present
- [x] **P1** `PHASE5-106` agent: GREEN — add node docstrings — DoD: test passes
- [x] **P1** `PHASE5-107` agent: verify — mypy/ruff clean, coverage ≥90% on agent_workflow — DoD: gates green
- [x] **P1** `PHASE5-108` agent: verify — full keyless suite green (ADR-0005) — DoD: `uv run pytest` no key, 0 failures
- [x] **P1** `PHASE5-109` agent: commit — `feat: LangGraph agent both run types (AW-T1..8)` — DoD: tests with code

### 5.14 — node-level edge & integration coverage

- [x] **P1** `PHASE5-110` agent: RED — test graph-guided `validate` promotes INFERRED→EXTRACTED conclusion in narrative — DoD: test fails; ref R5.5.3
- [x] **P1** `PHASE5-111` agent: GREEN — implement promotion narrative — DoD: test passes
- [x] **P1** `PHASE5-112` agent: RED — test every node's input/output inspectable via AgentState (R5.5.2) — DoD: test fails
- [x] **P1** `PHASE5-113` agent: GREEN — ensure state observability — DoD: test passes
- [x] **P1** `PHASE5-114` agent: RED — test `messages` log records each LLM turn — DoD: test fails
- [x] **P1** `PHASE5-115` agent: GREEN — append to messages per turn — DoD: test passes
- [ ] **P2** `PHASE5-116` agent: RED — test graph-guided run reaches polygons root cause (integration, mocked fix) — DoD: test fails; ref R4.2
- [ ] **P2** `PHASE5-117` agent: GREEN — confirm root-cause localization in graph-guided — DoD: test passes
- [ ] **P2** `PHASE5-118` agent: RED — test naive run may mislocate (Lost in the Middle) handled gracefully — DoD: test fails; ref TC-E2
- [ ] **P2** `PHASE5-119` agent: GREEN — handle naive mislocation without crash — DoD: test passes
- [x] **P1** `PHASE5-120` agent: RED — test `fix` node writes POST-FIX polygons.py to a SCRATCH copy (not overwriting vendored baseline during tests) — DoD: test fails; ref brief §6
- [x] **P1** `PHASE5-121` agent: GREEN — implement scratch-write in test mode — DoD: test passes
- [x] **P1** `PHASE5-122` agent: RED — test graph compiles with LangGraph StateGraph API — DoD: test fails; ref R5.3.1
- [x] **P1** `PHASE5-123` agent: GREEN — confirm StateGraph compilation — DoD: test passes
- [x] **P2** `PHASE5-124` agent: RED — test workflow node order matches documented Plan→Retrieve→Hypothesize→Validate→Fix→Report — DoD: test fails; ref R5.3.3
- [x] **P2** `PHASE5-125` agent: GREEN — assert node order — DoD: test passes
- [x] **P1** `PHASE5-126` agent: REFACTOR — extract shared fix/report logic used by both routes — DoD: no duplication (AW-T8 spirit)
- [x] **P1** `PHASE5-127` agent: RED — test gatekeeper is the only LLM-provider seam used by agent (no direct provider-SDK calls) — DoD: test fails; ref ADR-0002
- [x] **P1** `PHASE5-128` agent: GREEN — confirm no direct SDK calls in nodes — DoD: test passes
- [x] **P2** `PHASE5-129` agent: RED — test `plan` records run_id for log correlation — DoD: test fails
- [x] **P2** `PHASE5-130` agent: GREEN — set run_id in plan — DoD: test passes
- [x] **P2** `PHASE5-131` agent: RED — test deterministic node sequencing under mocked client — DoD: test fails
- [x] **P2** `PHASE5-132` agent: GREEN — ensure deterministic sequencing — DoD: test passes
- [x] **P1** `PHASE5-133` agent: verify — agent_workflow files all ≤150 lines — DoD: budget audit passes
- [x] **P1** `PHASE5-134` agent: verify — no `NotImplementedError` in any node shipped to main — DoD: grep clean; ref CLAUDE.md §3
- [x] **P1** `PHASE5-135` agent: verify — no mock class shadows a real import — DoD: audit clean; ref CLAUDE.md §3
- [x] **P1** `PHASE5-136` agent: commit — `test: agent edge cases + integration (AW-E1..5)` — DoD: tests committed

---

## Phase 6 — token comparison + evidence

> `token_comparison.py` (keyless, fixture logs) + the manual real run (needs key, ADR-0005)
> + `reports/token_comparison.md` + `artifacts/graphify_post_fix/` + graph diff. TC-T1..8, TC-E1..5.

### 6.1 — RunMetrics / ComparisonResult interface

- [x] **P0** `PHASE6-001` token_comparison: RED — test `RunMetrics` dataclass (run_type/input/output/total/num_llm_calls/duration_s/correctness/per_node) — DoD: test fails; ref interface
- [x] **P0** `PHASE6-002` token_comparison: GREEN — implement `RunMetrics` — DoD: test passes
- [x] **P0** `PHASE6-003` token_comparison: RED — test `ComparisonResult` (graph_guided/naive/input_token_reduction_pct/correctness_delta) — DoD: test fails
- [x] **P0** `PHASE6-004` token_comparison: GREEN — implement `ComparisonResult` — DoD: test passes
- [x] **P0** `PHASE6-005` token_comparison: RED — test `TokenComparison(agent_config)` constructs from `config/agent.json` — DoD: test fails
- [x] **P0** `PHASE6-006` token_comparison: GREEN — implement constructor — DoD: test passes

### 6.2 — metrics_from_state + per-node (TC-T6)

- [x] **P0** `PHASE6-007` token_comparison: RED — test `metrics_from_state` sums input/output/total tokens from `token_usage` — DoD: test fails; ref TC-T1
- [x] **P0** `PHASE6-008` token_comparison: GREEN — implement `metrics_from_state` aggregation — DoD: test passes
- [x] **P0** `PHASE6-009` token_comparison: RED — test `per_node` lists each node's input/output (fix distinct from report) — DoD: test fails; ref TC-T6
- [x] **P0** `PHASE6-010` token_comparison: GREEN — implement per-node breakdown — DoD: TC-T6 passes
- [x] **P0** `PHASE6-011` token_comparison: RED — test `num_llm_calls` counts TokenRecords — DoD: test fails
- [x] **P0** `PHASE6-012` token_comparison: GREEN — implement call count — DoD: test passes
- [x] **P0** `PHASE6-013` token_comparison: RED — test token source is gatekeeper log; mismatch with state fails loud — DoD: test fails; ref TC-E5
- [x] **P0** `PHASE6-014` token_comparison: GREEN — implement log-authority + fail-on-disagreement — DoD: TC-E5 passes

### 6.3 — correctness check (TC-T4/T5)

- [x] **P0** `PHASE6-015` token_comparison: RED — test `check_correctness` true for pentagon 540/108 — DoD: test fails; ref TC-T4
- [x] **P0** `PHASE6-016` token_comparison: GREEN — implement calc_polygon_details(5) assertion — DoD: test passes
- [x] **P0** `PHASE6-017` token_comparison: RED — test `check_correctness` true for hexagon 720/120 — DoD: test fails; ref TC-T4
- [x] **P0** `PHASE6-018` token_comparison: GREEN — implement calc_polygon_details(6) assertion — DoD: test passes
- [x] **P0** `PHASE6-019` token_comparison: RED — test `check_correctness` verifies Polygon imports without NameError/SyntaxError — DoD: test fails; ref TC correctness §2
- [x] **P0** `PHASE6-020` token_comparison: GREEN — implement import/validity check (Object→object, new removed) — DoD: test passes
- [x] **P0** `PHASE6-021` token_comparison: RED — test correctness checks calc_polygon_details returns/consumes a Polygon (not bare dict) — DoD: test fails; ref TODO@L33
- [x] **P0** `PHASE6-022` token_comparison: GREEN — implement Polygon-usage assertion — DoD: test passes
- [x] **P0** `PHASE6-023` token_comparison: RED — test mocked-turtle draw_polygon(pentagon) issues 5 forward/right (not 6), each turn 360/sides — DoD: test fails; ref TC-T4 / TODO@L50
- [x] **P0** `PHASE6-024` token_comparison: GREEN — implement mocked-turtle call-count assertion — DoD: test passes
- [x] **P0** `PHASE6-025` token_comparison: RED — test `check_correctness` False for original broken polygons.py (else 1000/200, hardcoded 6) — DoD: test fails; ref TC-T5
- [x] **P0** `PHASE6-026` token_comparison: GREEN — confirm broken source fails all three — DoD: TC-T5 passes
- [x] **P1** `PHASE6-027` token_comparison: RED — test correctness is pass only when all three resolutions hold — DoD: test fails; ref correctness §
- [x] **P1** `PHASE6-028` token_comparison: GREEN — implement all-three-AND gate — DoD: test passes

### 6.4 — compare + reduction % (TC-T2/T3, TC-E4)

- [x] **P0** `PHASE6-029` token_comparison: RED — test `compare()` input_token_reduction_pct == 85.0 for 1200 vs 8000 — DoD: test fails; ref TC-T2
- [x] **P0** `PHASE6-030` token_comparison: GREEN — implement reduction % formula — DoD: TC-T2 passes
- [x] **P0** `PHASE6-031` token_comparison: RED — test narrative states "85% fewer input tokens" — DoD: test fails; ref TC-T2
- [x] **P0** `PHASE6-032` token_comparison: GREEN — implement R4.1 narrative — DoD: test passes
- [x] **P0** `PHASE6-033` token_comparison: RED — test `correctness_delta` notes "no accuracy cost" when both pass — DoD: test fails; ref TC-T3
- [x] **P0** `PHASE6-034` token_comparison: GREEN — implement R4.2 narrative — DoD: TC-T3 passes
- [x] **P0** `PHASE6-035` token_comparison: RED — test zero-division guard when naive input == 0 — DoD: test fails; ref TC-E4
- [x] **P0** `PHASE6-036` token_comparison: GREEN — implement zero-division guard — DoD: TC-E4 passes
- [x] **P1** `PHASE6-037` token_comparison: RED — test naive fail still renders report with correctness=fail narrative — DoD: test fails; ref TC-E2
- [x] **P1** `PHASE6-038` token_comparison: GREEN — implement fail-narrative path — DoD: TC-E2 passes

### 6.5 — render/write report (TC-T1)

- [x] **P0** `PHASE6-039` token_comparison: RED — test `render_report` markdown has table rows graph_guided + naive with correct sums — DoD: test fails; ref TC-T1
- [x] **P0** `PHASE6-040` token_comparison: GREEN — implement `render_report` table — DoD: TC-T1 passes
- [x] **P0** `PHASE6-041` token_comparison: RED — test table columns: Input/Output/Total/#LLM calls/Correctness/Notes — DoD: test fails; ref output artifact
- [x] **P0** `PHASE6-042` token_comparison: GREEN — implement full column set — DoD: test passes
- [x] **P0** `PHASE6-043` token_comparison: RED — test `write_report` writes `reports/token_comparison.md` — DoD: test fails
- [x] **P0** `PHASE6-044` token_comparison: GREEN — implement `write_report` — DoD: test passes
- [x] **P1** `PHASE6-045` token_comparison: RED — test report includes R4.1 + R4.2 narrative sections — DoD: test fails; ref output artifact
- [x] **P1** `PHASE6-046` token_comparison: GREEN — implement narrative sections — DoD: test passes
- [x] **P1** `PHASE6-047` token_comparison: REFACTOR — keep `report.py` + `runner.py` ≤150 lines each — DoD: file budget honored

### 6.6 — graph diff (TC-T7, TC-E3)

- [x] **P0** `PHASE6-048` token_comparison: RED — test `diff_graphs(pre, post)` reports `nodes: 23 → 20` for fixture post-fix — DoD: test fails; ref TC-T7
- [x] **P0** `PHASE6-049` token_comparison: GREEN — implement `diff_graphs` node/edge/community/confidence diff — DoD: TC-T7 passes
- [x] **P0** `PHASE6-050` token_comparison: RED — test diff lists `polygons_polygons_rationale_{18,33,50}` as removed — DoD: test fails; ref TC-T7 / R5.6.3 prediction
- [x] **P0** `PHASE6-051` token_comparison: GREEN — implement removed-node listing — DoD: test passes
- [x] **P0** `PHASE6-052` token_comparison: RED — test missing post-fix graph → fail loud / "pending re-run" (never fabricate) — DoD: test fails; ref TC-E3
- [x] **P0** `PHASE6-053` token_comparison: GREEN — implement TC-E3 handling — DoD: test passes
- [x] **P1** `PHASE6-054` token_comparison: RED — test `diff_graphs` writes `reports/graph_diff.md` (or section) — DoD: test fails; ref R5.6.3
- [x] **P1** `PHASE6-055` token_comparison: GREEN — implement graph_diff output — DoD: test passes
- [x] **P1** `PHASE6-056` token_comparison: RED — test diff notes Polygon now has a usage edge (used, not dead) prediction — DoD: test fails; ref R5.6.3 prediction
- [x] **P1** `PHASE6-057` token_comparison: GREEN — implement usage-edge note — DoD: test passes

### 6.7 — keyless test fixtures + real-run gating (TC-T8, TC-E1)

- [x] **P0** `PHASE6-058` token_comparison: RED — test suite runs on fixture gatekeeper logs (no key) — DoD: test fails; ref TC-E1
- [x] **P0** `PHASE6-059` token_comparison: GREEN — create fixture JSONL logs + wire tests keyless — DoD: TC-E1 passes
- [x] **P0** `PHASE6-060` token_comparison: RED — test real-run script exits "key required" when the configured provider key env var is absent — DoD: test fails; ref TC-T8
- [x] **P0** `PHASE6-061` token_comparison: GREEN — implement key-required gate in real-run script — DoD: TC-T8 passes
- [x] **P1** `PHASE6-062` token_comparison: verify — test suite never triggers the real-run path — DoD: pytest collects no keyed test; ref ADR-0005
- [x] **P1** `PHASE6-063` token_comparison: implement `scripts/run_comparison.py` (manual, keyed, not pytest-collected) — DoD: script runs both agent runs, dumps logs — DoD: gated by key
- [x] **P1** `PHASE6-064` token_comparison: implement `runner.run_both(sdk, cfg)` driving graph_guided + naive — DoD: returns ComparisonResult
- [x] **P1** `PHASE6-065` token_comparison: RED — test `run_both` calls agent for both run types — DoD: test fails (mocked)
- [x] **P1** `PHASE6-066` token_comparison: GREEN — implement run_both — DoD: test passes
- [x] **P1** `PHASE6-067` token_comparison: verify — mypy/ruff clean, coverage ≥90% on token_comparison — DoD: gates green
- [x] **P1** `PHASE6-068` token_comparison: wire `compare_tokens` into `sdk.py` + `ex04 compare` CLI — DoD: command resolves
- [x] **P1** `PHASE6-069` token_comparison: commit — `feat: token_comparison + graph diff (TC-T1..8)` — DoD: tests with code

### 6.8 — the actual manual real run (needs key)

- [x] **P0** `PHASE6-070` evidence: owner runs `scripts/run_comparison.py` once with the real provider key set (likely `GEMINI_API_KEY`) — DoD: both runs complete; gatekeeper JSONL logs produced; ref ADR-0005
- [x] **P0** `PHASE6-071` evidence: capture graph-guided run token log → `artifacts/runs/<run_id>.jsonl` — DoD: log committed
- [x] **P0** `PHASE6-072` evidence: capture naive run token log → `artifacts/runs/<run_id>.jsonl` — DoD: log committed
- [x] **P0** `PHASE6-073` evidence: generate real `reports/token_comparison.md` from the logs — DoD: real numbers, no placeholders, incl. `Files read` + `Iterations` columns (R5.6.5); ref R5.6.4/R7.8
- [x] **P0** `PHASE6-073a` evidence: commit the full graph-guided run **transcript** (per-node messages, hypothesis+tag, source-validation, the diff) → `docs/evidence/run_graph_guided.md` — the agent-debate committed-transcript signature, so the live run is inspectable without a key — DoD: transcript committed; ref R10.5, eval-harness behavioural evals
- [x] **P0** `PHASE6-073b` evidence: commit the full naive run transcript → `docs/evidence/run_naive.md` — DoD: transcript committed
- [x] **P1** `PHASE6-073c` evidence: add `docs/evidence/README.md` indexing the committed runs + stating model/provider/date used (D6) — DoD: index present; grader can trace each number to a transcript line
- [x] **P1** `PHASE6-073d` evidence: record `files_read` (graph-guided ≈3 vs naive ≈9) and `iterations` per run into the report from the transcripts — DoD: both mandated R5.6.5 columns populated with real values
- [x] **P0** `PHASE6-074` evidence: verify real graph-guided used fewer input tokens than naive — DoD: reduction % > 0; ref R4.1
- [x] **P0** `PHASE6-075` evidence: verify real correctness delta recorded (both/which passed) — DoD: correctness column populated; ref R4.2
- [x] **P0** `PHASE6-076` evidence: apply the real fix to `data/broken-python/polygons/polygons.py` (POST-FIX source) — DoD: three TODOs resolved; ref brief §2 fix scope
- [x] **P0** `PHASE6-077` evidence: owner re-runs Graphify on fixed repo → `artifacts/graphify_post_fix/graph.json` + GRAPH_REPORT — DoD: separate dir, PRE-FIX untouched; ref R5.6.3
- [x] **P0** `PHASE6-078` evidence: generate POST-FIX `hot.md` via obsidian_writer against post-fix graph — DoD: post-fix hot.md produced; ref PRD_graph_reader §4
- [x] **P0** `PHASE6-079` evidence: run `diff_graphs(pre, post)` on real graphs → `reports/graph_diff.md` — DoD: real diff committed; ref R5.6.3
- [x] **P0** `PHASE6-080` evidence: verify the three rationale_* nodes disappeared in POST-FIX graph — DoD: prediction confirmed or discrepancy documented; ref TC-T7
- [x] **P1** `PHASE6-081` evidence: commit all real artifacts (logs, reports, post-fix graph, post-fix hot.md) — DoD: `docs: commit real comparison artifacts (R5.6/R7.8)`
- [x] **P1** `PHASE6-082` evidence: note in KNOWN_LIMITATIONS that numbers reflect a specific model/run (D6) — DoD: disclosed; ref ADR-0005
- [x] **P1** `PHASE6-083` evidence: verify grader can read R5.6/R7.8 numbers without a key (static artifacts) — DoD: artifacts self-contained
- [x] **P2** `PHASE6-084` evidence: capture wall-clock duration per run into report — DoD: duration_s present
- [x] **P1** `PHASE6-085` evidence: cross-check report numbers trace to gatekeeper log entries — DoD: every number sourced; ref R10.5
- [x] **P1** `PHASE6-086` evidence: keep PRE-FIX `obsidian/hot.md` and POST-FIX hot.md both retained — DoD: both committed for diff story

---

## Phase 7 — reports

> Architecture diagrams, OOP-improvement summary, before/after diff writeup with root-cause
> narrative. Covers R5.2.4, R5.4.2, R7.6, R7.7, R7.9.

- [x] **P0** `PHASE7-001` reports: render the C4 context diagram (PLAN.md §1) to an image/markdown in `reports/` — DoD: diagram rendered; ref R5.4.2 — ✅ Phase 7
- [x] **P0** `PHASE7-002` reports: render the C4 container diagram (PLAN.md §2) — DoD: rendered — ✅ Phase 7
- [x] **P0** `PHASE7-003` reports: render the agent_workflow graph-guided state diagram (PLAN.md §3a) — DoD: rendered; ref R5.4.2/R7.3 — ✅ Phase 7
- [x] **P0** `PHASE7-004` reports: render the naive baseline state diagram (PLAN.md §3b) — DoD: rendered — ✅ Phase 7
- [x] **P1** `PHASE7-005` reports: verify rendered diagrams match the actual compiled LangGraph topology — DoD: node set matches build_graph — ✅ Phase 7
- [x] **P0** `PHASE7-006` reports: write before/after diff of `polygons.py` to `reports/` (unified diff) — DoD: diff present; ref R5.2.4/R7.6 — ✅ Phase 7
- [x] **P0** `PHASE7-007` reports: write root-cause narrative (single root cause: half-finished Polygon) — DoD: narrative present; ref R4.5/R5.2.2 — ✅ Phase 7
- [x] **P0** `PHASE7-008` reports: narrative covers Object→object fix (NameError) — DoD: documented; ref brief §2 — ✅ Phase 7
- [x] **P0** `PHASE7-009` reports: narrative covers `new` removed (SyntaxError) — DoD: documented — ✅ Phase 7
- [x] **P0** `PHASE7-010` reports: narrative covers calc_polygon_details generalization (TODO@L18, (sides-2)*180) — DoD: documented — ✅ Phase 7
- [x] **P0** `PHASE7-011` reports: narrative covers draw_polygon generalization (TODO@L50, 360/sides) — DoD: documented — ✅ Phase 7
- [x] **P0** `PHASE7-012` reports: narrative covers dict/class duplication removal (TODO@L33) — DoD: documented — ✅ Phase 7
- [x] **P0** `PHASE7-013` reports: write OOP-improvement summary — Polygon as single source of truth — DoD: present; ref R7.7/R3.4/R5.2.3 — ✅ Phase 7
- [x] **P0** `PHASE7-014` reports: OOP summary explains calc_polygon_details → constructor/classmethod refactor — DoD: documented — ✅ Phase 7
- [x] **P0** `PHASE7-015` reports: OOP summary explains removed dict duplication (signal 6) — DoD: documented; ref R4.4 — ✅ Phase 7
- [x] **P1** `PHASE7-016` reports: sides>=3 validation (signal 4) — IMPLEMENTED as a ValueError guard (post-review fix; closes the ZeroDivisionError on the live input path) + test; OOP summary documents it — DoD: noted — ✅ Phase 7
- [x] **P1** `PHASE7-017` reports: tie OOP improvements back to graph signals that suggested them — DoD: each improvement cites a signal; ref R4.4 — ✅ Phase 7
- [x] **P0** `PHASE7-018` reports: take Obsidian graph-view screenshot(s) — DoD: image(s) in `reports/`; ref R5.4.1/R7.9 — ✅ Phase 7
- [x] **P0** `PHASE7-019` reports: take screenshot of `hot.md` open in Obsidian — DoD: image present; ref R10.3 — ✅ Phase 7
- [x] **P0** `PHASE7-020` reports: take screenshot of `index.md` navigation — DoD: image present — ✅ Phase 7
- [x] **P0** `PHASE7-021` reports: take screenshot showing the Polygon god node in graph view — DoD: image present; ref R4.6 — ✅ Phase 7
- [x] **P1** `PHASE7-022` reports: write a short "how Obsidian helped" narrative (R4.6) — DoD: present — ✅ Phase 7
- [x] **P1** `PHASE7-023` reports: write the end-to-end pipeline diagram (repo→graph→vault→agent→fix) — DoD: rendered; ref R5.5.1 — ✅ Phase 7
- [x] **P1** `PHASE7-024` reports: pipeline doc shows each stage's inspectable artifact (R5.5.2) — DoD: artifacts listed per stage — ✅ Phase 7
- [x] **P1** `PHASE7-025` reports: pipeline doc shows how root cause found via graph (R5.5.3) — DoD: validate-step traced — ✅ Phase 7
- [x] **P1** `PHASE7-026` reports: write the six-signal → root-cause convergence summary — DoD: signals {1,5,6} table present; ref R4.5 — ✅ Phase 7
- [x] **P1** `PHASE7-027` reports: answer R4.3 (God Nodes reveal core abstraction/coupling) in a report section — DoD: present — ✅ Phase 7
- [x] **P1** `PHASE7-028` reports: answer R4.7 (AI usage + where agent diverged from human) — DoD: present; ref PROMPTS.md — ✅ Phase 7
- [x] **P1** `PHASE7-029` reports: ensure every quantitative claim links to a stored artifact (R10.5) — DoD: citations present — ✅ Phase 7
- [x] **P1** `PHASE7-030` reports: verify token-comparison numbers in narrative match `reports/token_comparison.md` — DoD: no drift — ✅ Phase 7
- [x] **P1** `PHASE7-031` reports: verify graph-diff numbers match `reports/graph_diff.md` — DoD: no drift — ✅ Phase 7
- [x] **P2** `PHASE7-032` reports: add a before/after metrics table (degrees, node counts) — DoD: table present — ✅ Phase 7
- [x] **P1** `PHASE7-033` reports: confirm all images are committed (not external links) — DoD: files in repo; ref R7.9 — ✅ Phase 7
- [x] **P1** `PHASE7-034` reports: verify diff narrative is reviewable/focused (4 documented items only) — DoD: scope matches ADR-0003 — ✅ Phase 7
- [x] **P1** `PHASE7-035` reports: cross-link reports from README (R8.5) — DoD: links present — ✅ Phase 7
- [x] **P2** `PHASE7-036` reports: add caption/alt-text to each screenshot for accessibility — DoD: captions present — ✅ Phase 7
- [x] **P1** `PHASE7-037` reports: verify reports reproducible by third party from repo (R1.5) — DoD: paths/instructions present — ✅ Phase 7
- [x] **P1** `PHASE7-038` reports: confirm reports live under `reports/` per R9 structure — DoD: location correct — ✅ Phase 7
- [x] **P2** `PHASE7-039` reports: add a "Lost in the Middle" explanation tying naive baseline to PART-B — DoD: cited; ref R1.4/ADR-0004 — ✅ Phase 7
- [x] **P1** `PHASE7-040` reports: verify OOP summary code samples compile against POST-FIX polygons.py — DoD: samples valid — ✅ Phase 7
- [x] **P1** `PHASE7-041` reports: spell/clarity pass on all reports — DoD: reviewed; ref R10.1 — ✅ Phase 7
- [x] **P2** `PHASE7-042` reports: add legend explaining EXTRACTED/INFERRED/AMBIGUOUS in the signal report — DoD: legend present — ✅ Phase 7
- [x] **P1** `PHASE7-043` reports: confirm before/after diff includes the resolved TODO comments removed — DoD: diff shows TODO removal — ✅ Phase 7
- [x] **P1** `PHASE7-044` reports: confirm root-cause narrative names it a single root cause (not multi-symptom) — DoD: framed per R5.2.2 — ✅ Phase 7
- [x] **P1** `PHASE7-045` reports: link agent workflow diagram from README R8.4 — DoD: link present — ✅ Phase 7
- [x] **P1** `PHASE7-046` reports: commit all Phase-7 reports + images — DoD: `docs: reports + diagrams (R5.4/R7.6/R7.7/R7.9)` — ✅ Phase 7
- [x] **P2** `PHASE7-047` reports: peer/self review of narrative for explainability (R10.4) — DoD: every claim defensible — ✅ Phase 7

---

## Phase 8 — README + self-grade

> Each README section R8.1–R8.9 as its own task, plus `scripts/self_grade.py`,
> KNOWN_LIMITATIONS final pass, screenshots verification, final commit/PR. Covers R8.x, R10.x.

### 8.1 — README sections (R8.1–R8.9)

- [x] **P0** `PHASE8-001` README: write §R8.1 — chosen repo (`martinpeck/broken-python`) + chosen bug (`polygons/polygons.py`) + rationale — DoD: section present; ref R8.1/R2.2/ADR-0003 — ✅ Phase 8
- [x] **P0** `PHASE8-002` README: write §R8.2 — setup + run (uv-based, keyless-by-default) — DoD: `uv sync` + `uv run pytest` documented; ref R8.2/ADR-0005 — ✅ Phase 8
- [x] **P0** `PHASE8-003` README: §R8.2 documents keyless test run explicitly (no key needed) — DoD: stated — ✅ Phase 8
- [x] **P0** `PHASE8-004` README: §R8.2 documents the manual keyed real-run path separately — DoD: stated; ref ADR-0005 — ✅ Phase 8 (in a `<details>` block)
- [x] **P0** `PHASE8-005` README: write §R8.3 — how Graphify + Obsidian were used (+ links/screenshots into `obsidian/`) — DoD: section + links; ref R8.3 — ✅ Phase 8
- [x] **P0** `PHASE8-006` README: §R8.3 links `obsidian/index.md` + `obsidian/hot.md` + screenshots — DoD: links present — ✅ Phase 8 (Figs 3/5 embedded)
- [x] **P0** `PHASE8-007` README: write §R8.4 — agent workflow (LangGraph diagram or description) — DoD: section + diagram link; ref R8.4/R5.4.2 — ✅ Phase 8 (both routes as inline Mermaid)
- [x] **P0** `PHASE8-008` README: §R8.4 documents nodes, tools, stop conditions — DoD: present; ref R5.3.3 — ✅ Phase 8 (validate→hypothesize bounded loop + budget-exhausted stop)
- [x] **P0** `PHASE8-009` README: write §R8.5 — root cause narrative + before/after diff (or link) — DoD: section + link; ref R8.5/R7.6 — ✅ Phase 8
- [x] **P0** `PHASE8-010` README: write §R8.6 — token-efficiency results (numbers: naive vs graph-guided) — DoD: numbers + link to report; ref R8.6/R7.8 — ✅ Phase 8 (406 vs 1743, 76.7%)
- [ ] **P0** `PHASE8-011` README: §R8.6 cites concrete input/output tokens + call counts — DoD: numbers present; ref R5.6.4 — ⏳ input tokens cited; output/call-counts await the keyed run (KNOWN_LIMITATIONS #5)
- [x] **P0** `PHASE8-012` README: write §R8.7 — OOP-improvement summary (or link) — DoD: section + link; ref R8.7/R7.7 — ✅ Phase 8
- [x] **P0** `PHASE8-013` README: write §R8.8 — AI-usage disclosure (AI-generated vs human-reviewed, per PROMPTS.md) — DoD: section + link; ref R8.8/R4.7 — ✅ Phase 8
- [x] **P0** `PHASE8-014` README: write §R8.9 — known limitations + honest self-grade — DoD: section + link to KNOWN_LIMITATIONS; ref R8.9 — ✅ Phase 8 (self-grade number computed at submission)
- [ ] **P1** `PHASE8-015` README: add research-questions section answering R4.1–R4.7 with evidence links — DoD: each RQ answered — (deferred; `reports/pipeline.md` covers RQs)
- [ ] **P1** `PHASE8-016` README: document the uv/pyproject deviation from §9 requirements.txt as intentional/disclosed — DoD: noted; ref R9.1
- [ ] **P1** `PHASE8-017` README: add repository-structure section matching R9 layout — DoD: tree present
- [x] **P1** `PHASE8-018` README: add reproduce-from-scratch quickstart (third party) — DoD: steps present; ref R1.5/R10.1 — ✅ Phase 8 (TL;DR + §2)
- [x] **P1** `PHASE8-019` README: link to the agent workflow diagram image — DoD: link resolves — ✅ Phase 8 (inline Mermaid + `reports/diagrams.md`)
- [x] **P1** `PHASE8-020` README: link to `reports/token_comparison.md` + `reports/graph_diff.md` — DoD: links resolve — ✅ Phase 8
- [x] **P1** `PHASE8-021` README: verify all README links resolve (no dead links) — DoD: link-check passes — ✅ Phase 8 (files verified; added missing `LICENSE`)
- [x] **P1** `PHASE8-022` README: clarity/grammar pass (R10.1) — DoD: reviewed — ✅ Phase 8
- [x] **P2** `PHASE8-023` README: add badges (CI status) if CI is set up — DoD: badge renders — ✅ Phase 8 (9 static badges: py/uv/ruff/mypy/tests/coverage/keyless/LangGraph/MIT)

### 8.2 — PROMPTS.md + AI disclosure

- [x] **P1** `PHASE8-024` disclosure: finalize `docs/PROMPTS.md` listing AI-generated vs human-reviewed artifacts — DoD: planning + code sessions disclosed; ref R8.8 — ✅ Phase 8 (Phase-8 entry appended; final read-through at submission)
- [x] **P1** `PHASE8-025` disclosure: note where the agent's workflow diverged from a human's (R4.7) — DoD: section present — ✅ Phase 8 (Antigravity-caught hardcoding shortcut documented in PROMPTS + README §8)
- [x] **P1** `PHASE8-026` disclosure: confirm AI is framed as collaborator, claims defensible (R10.4) — DoD: stated — ✅ Phase 8 (README §8 + honest TDD note)

### 8.3 — self_grade

- [ ] **P0** `PHASE8-027` self_grade: RED — test `scripts/self_grade.py` runs keyless and exits 0 — DoD: test fails; ref ADR-0005
- [ ] **P0** `PHASE8-028` self_grade: GREEN — implement `self_grade.py` (no API key, mocked) — DoD: test passes
- [ ] **P0** `PHASE8-029` self_grade: RED — test self_grade checks requirement coverage (R-id → artifact map) — DoD: test fails
- [ ] **P0** `PHASE8-030` self_grade: GREEN — implement requirement-coverage check — DoD: test passes
- [ ] **P1** `PHASE8-031` self_grade: check ruff 0 violations gate — DoD: reported
- [ ] **P1** `PHASE8-032` self_grade: check mypy --strict 0 errors gate — DoD: reported
- [ ] **P1** `PHASE8-033` self_grade: check coverage ≥90% gate — DoD: reported
- [ ] **P1** `PHASE8-034` self_grade: check all Python files ≤150 lines by invoking `scripts/check_file_sizes.py` (reuse, don't reimplement) — DoD: reported; ref CLAUDE.md / PHASE1-018
- [ ] **P1** `PHASE8-035` self_grade: check `obsidian/hot.md` exists + wikilink consistency — DoD: reported; ref Phase 4
- [ ] **P1** `PHASE8-036` self_grade: check `reports/token_comparison.md` numbers trace to gatekeeper logs — DoD: reported; ref R10.5
- [ ] **P1** `PHASE8-037` self_grade: check PRE-FIX baselines unmodified (hash) — DoD: reported; ref brief §6
- [ ] **P1** `PHASE8-038` self_grade: check no hardcoded secrets/values by invoking `scripts/check_no_hardcoded.py` (reuse) — DoD: reported; ref PHASE1-018b
- [ ] **P1** `PHASE8-039` self_grade: check no `NotImplementedError` on main / anti-patterns by invoking `scripts/check_anti_patterns.py` (reuse) — DoD: reported; ref PHASE1-018d
- [ ] **P1** `PHASE8-040` self_grade: emit a conservative, defensible numeric self-grade — DoD: number + justification; ref R8.9
- [ ] **P1** `PHASE8-041` self_grade: cross-reference self-grade against KNOWN_LIMITATIONS — DoD: consistent
- [ ] **P1** `PHASE8-042` self_grade: verify self_grade is NOT collected as a normal test but runnable via `uv run` — DoD: separate entry
- [ ] **P1** `PHASE8-043` self_grade: REFACTOR — keep self_grade modules ≤150 lines each — DoD: budget honored
- [ ] **P1** `PHASE8-044` self_grade: commit — `feat: self_grade keyless (R8.9)` — DoD: tests with code

### 8.4 — KNOWN_LIMITATIONS final pass

- [ ] **P0** `PHASE8-045` limits: confirm `pyproject.toml` authors placeholder item resolved or flagged — DoD: status accurate; ref brief §0
- [ ] **P1** `PHASE8-046` limits: document original `broken-python/` clone removal/gitignore status — DoD: noted; ref brief §3
- [ ] **P1** `PHASE8-047` limits: document keyless-run caveat (numbers from one model/run, D6) — DoD: noted; ref ADR-0005
- [ ] **P1** `PHASE8-048` limits: document turtle headless/mocked limitation (no visual verification) — DoD: noted; ref PRD.md §10
- [ ] **P1** `PHASE8-049` limits: document mathsquiz out-of-scope (secondary fixture only) — DoD: noted; ref ADR-0003
- [ ] **P1** `PHASE8-050` limits: document PDF Hebrew-extraction caveat for ASSIGNMENT.md — DoD: noted; ref ASSIGNMENT extraction note
- [ ] **P2** `PHASE8-051` limits: note VCR cassettes as future improvement (rejected baseline) — DoD: noted; ref ADR-0005
- [ ] **P1** `PHASE8-052` limits: ensure self-grade number is honest/conservative — DoD: defensible; ref R10.4

### 8.5 — screenshots + final verification

- [x] **P0** `PHASE8-053` final: verify Obsidian screenshots present + referenced (R5.4.1/R7.9) — DoD: images in reports/ + README — ✅ Phase 8 (Figs 3/5 in README §3; Figs 3–6 in reports/screenshots.md)
- [x] **P1** `PHASE8-054` final: verify agent workflow diagram present + referenced (R5.4.2/R7.3) — DoD: linked — ✅ Phase 8 (inline Mermaid in README §4 + reports/diagrams.md)
- [ ] **P0** `PHASE8-055` final: run full keyless suite `uv run pytest --cov` ≥90% green — DoD: pass; ref CLAUDE.md
- [ ] **P0** `PHASE8-056` final: run `uv run ruff check .` 0 violations — DoD: clean
- [ ] **P0** `PHASE8-057` final: run `uv run mypy --strict src/` 0 errors — DoD: clean
- [ ] **P0** `PHASE8-058` final: run `scripts/self_grade.py` keyless → green — DoD: pass
- [ ] **P1** `PHASE8-059` final: verify every R#.# (R1.1–R10.5) traces to ≥1 task/artifact — DoD: traceability matrix complete
- [ ] **P1** `PHASE8-060` final: verify all 8 modules have scaffold+impl+tests — DoD: module audit passes; ref brief §4
- [ ] **P1** `PHASE8-061` final: delete `docs/_internal_context_brief.md` before submission — DoD: removed; ref brief header
- [ ] **P1** `PHASE8-062` final: remove/gitignore original `broken-python/` clone — DoD: not in deliverable tree
- [ ] **P1** `PHASE8-063` final: verify commit history is continuous (no mass-commit), Conventional Commits — DoD: log audit passes; ref CLAUDE.md
- [ ] **P0** `PHASE8-064` final: confirm `pyproject.toml` authors = real names + IDs (no placeholder) — DoD: filled; ref brief §0
- [ ] **P1** `PHASE8-065` final: verify repo is public on GitHub (R7.1) — DoD: public
- [ ] **P1** `PHASE8-066` final: verify all deliverables R7.1–R7.9 present — DoD: checklist complete
- [ ] **P0** `PHASE8-067` final: create the submission PR / tag the release — DoD: PR open / release tagged
- [ ] **P1** `PHASE8-068` final: PR description summarizes deliverables + self-grade — DoD: present
- [ ] **P1** `PHASE8-069` final: final `docs: README + self-grade + cleanup` commit — DoD: committed
- [ ] **P2** `PHASE8-070` final: dry-run the README quickstart on a clean checkout — DoD: third-party reproduce works; ref R10.1
- [x] **P1** `PHASE8-071` final: confirm KNOWN_LIMITATIONS linked from README §R8.9 — DoD: link resolves — ✅ Phase 8

---

## Requirements not yet covered by a task (flag for verification)

*None.* Every numbered requirement R1.1–R10.5 is traceable to at least one task above:

- R1.1 → PHASE1-077 / PHASE8-001; R1.2 → PHASE8-001/005; R1.3 → PHASE5-016..019;
  R1.4 → PHASE5-084/085, PHASE7-039; R1.5 → PHASE4-037, PHASE7-037, PHASE8-018.
- R2.1/R2.2 → PHASE8-001 (ADR-0003). R3.1 → PHASE5 (graph-guided); R3.2 → PHASE5/ADR-0004;
  R3.3 → PHASE6; R3.4 → PHASE7-013; R3.5 → PHASE4/PHASE6 artifacts.
- R4.1 → PHASE6-029/074; R4.2 → PHASE6-033/075; R4.3 → PHASE3-012.., PHASE7-027;
  R4.4 → PHASE7-015/017; R4.5 → PHASE3-118, PHASE7-007/026; R4.6 → PHASE7-018..022;
  R4.7 → PHASE7-028, PHASE8-024/025.
- R5.1.1 → PHASE2-009/PHASE4-001; R5.1.2 → PHASE4-008/009; R5.1.3 → PHASE2-116, PHASE4-007;
  R5.1.4 → PHASE4-001..005; R5.2.1 → PHASE2-121, PHASE3; R5.2.2 → PHASE7-007/044;
  R5.2.3 → PHASE7-014; R5.2.4 → PHASE7-006; R5.3.1 → PHASE5-122; R5.3.2 → PHASE5-017;
  R5.3.3 → PHASE5-124, PHASE8-008; R5.4.1 → PHASE7-018, PHASE8-053; R5.4.2 → PHASE7-003,
  PHASE8-007; R5.5.1 → PHASE5-063, PHASE7-023; R5.5.2 → PHASE5-112, PHASE7-024;
  R5.5.3 → PHASE5-110, PHASE7-025; R5.6.1 → PHASE4-002/003; R5.6.2 → PHASE6-039;
  R5.6.3 → PHASE6-048..057/079; R5.6.4 → PHASE6-073, PHASE8-011.
- R6.1.1 → Phase 0; R6.1.2 → PHASE7-018..022; R6.1.3 → PHASE8-024; R6.1.4 → PHASE5-001/007;
  R6.1.5 → PHASE1-061 (model choice/D6); R6.1.6 → N/A (ADR-0003, documented);
  R6.2.1 → PHASE5-017; R6.2.2 → PHASE5-105; R6.2.3 → N/A; R6.2.4 → PHASE7-006;
  R6.2.5 → PHASE8-001..014; R6.2.6 → PHASE7-018.
- R7.1 → PHASE1-073/PHASE8-065; R7.2 → all src tasks; R7.3 → PHASE5-122/PHASE7-003;
  R7.4 → PHASE6-077; R7.5 → PHASE4; R7.6 → PHASE7-006; R7.7 → PHASE7-013; R7.8 → PHASE6-073;
  R7.9 → PHASE7-018/033.
- R8.1–R8.9 → PHASE8-001..014. R9.1 → PHASE1-001/PHASE8-016/017.
- R10.1 → PHASE7-041, PHASE8-022/070; R10.2 → PHASE7-013/040; R10.3 → PHASE4-033, PHASE7-019;
  R10.4 → PHASE7-047, PHASE8-026/052; R10.5 → PHASE6-085, PHASE7-029.
