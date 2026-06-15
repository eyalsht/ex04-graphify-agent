# PROMPTS — AI Usage Log

This file is an **append-only log** of significant AI prompts used during the development
of EX04 (Graphify + Obsidian Reverse-Engineering Agent). It exists to satisfy **R8.8**
(AI-usage disclosure) and **R6.1.3** (disclose AI usage throughout).

## Format

Each entry records:

- **Date** — when the prompt was issued.
- **Phase** — which project phase it belongs to (Phase 0 = planning, Phase 1 = scaffold,
  ... Phase 8 = README/self-grade; see `docs/PLAN.md` / `docs/TODO.md` for the phase list).
- **Prompt summary** — what was asked, in 1-3 sentences (not the verbatim prompt unless
  short).
- **AI tool/model** — which tool and model(s) were used.
- **AI-generated vs. human-reviewed/edited** — what the AI produced unassisted, and what
  the human (project owner) checked, corrected, or rewrote afterward.

New entries are appended at the bottom in chronological order. Do not edit or delete past
entries except to fix factual errors (note the correction inline).

---

## Entries

### 2026-06-14 — Phase 0 (Planning)

- **Prompt summary:** Project kickoff prompt requested generation of the full planning
  layer for EX04: `CLAUDE.md`, `docs/ASSIGNMENT.md`, `docs/PRD.md`, `docs/PLAN.md`,
  `docs/adr/*` (ADR-0001 through ADR-0005), the four per-mechanism PRDs
  (`PRD_graph_reader.md`, `PRD_weakness_detector.md`, `PRD_agent_workflow.md`,
  `PRD_token_comparison.md`), `docs/TODO.md`, `docs/PROMPTS.md` (this file), and
  `docs/KNOWN_LIMITATIONS.md`. The kickoff prompt followed a `grill-me` interview session
  that resolved open questions about the project's repo layout (single repo containing
  both the agent tooling and the vendored target-repo data, vs. separate repos) — that
  interview's outcome is recorded as the "locked decisions" in
  `docs/_internal_context_brief.md` §1.
- **AI tool/model:** Claude Code — Claude Sonnet 4.6 acting as orchestrator, dispatching
  Claude Opus/Sonnet subagents to draft individual planning documents in parallel.
- **AI-generated vs. human-reviewed/edited:** All Phase 0 planning documents listed above
  are **fully AI-drafted** and have **not yet been reviewed line-by-line by the human**.
  They must be treated as a first draft requiring human review before being relied upon as
  final, in particular:
  - `docs/ASSIGNMENT.md` — reconstructed from partial PDF text extraction (Hebrew body
    text could not be machine-extracted); needs a spot-check against the source PDF.
  - `pyproject.toml`'s future `authors` field — currently specified only as a placeholder
    in the planning brief (`docs/_internal_context_brief.md` §0); real student names/IDs
    for the project owner and "Imri" must be filled in before any commit.
  - All "locked decisions" in `docs/_internal_context_brief.md` §1 (D1-D7) — presented as
    final by the planning subagents, but represent AI-proposed choices the human owner has
    not yet explicitly re-confirmed outside of the `grill-me` session.

---

### 2026-06-15 — Phases 3 & 4 (parallel subagent dispatch)

- **Prompt summary:** Project owner asked the orchestrator (this session) to drive Phases 3
  and 4 by dispatching subagents, deciding parallel-vs-serial and model per task, and
  PR-gating each. After a dependency check (Phase 2 `graph_reader` was already merged via
  PR #1; `obsidian_writer` was NOT), the orchestrator dispatched **two parallel subagents,
  each in its own git worktree off `main`**, since both depend only on `graph_reader` and
  touch disjoint modules:
  - **Phase 3 → Claude Opus** (analytical core): build `weakness_detector/` (six PART-C
    signals, EXTRACTED/INFERRED/AMBIGUOUS language↔tag invariant, Signal-6 disclosed
    source-peek, ranked `detect()` with `source_validation=None`) + `gatekeeper/`
    (provider-agnostic choke point, retry/queue, JSONL token log, keyless `MockClient`),
    strict TDD, keyless, ≤150-line files, → PR #2.
  - **Phase 4 → Claude Sonnet** (mechanical, well-specified): build the leftover Phase-2
    `obsidian_writer` ranking (OW-T1..5) then generate PRE-FIX `obsidian/hot.md`, a
    `check_vault_consistency.py` gate, and the `ex04 hot` CLI; baselines immutable;
    deterministic output, → PR #3.
  - Each subagent was given a self-contained brief (CLAUDE.md rules, the real `graph_reader`
    API, config contracts, target-bug facts, module boundaries to avoid collision, and
    "open a PR + return a summary"). `docs/TODO.md` / `docs/PROMPTS.md` were reserved for the
    orchestrator (this entry) to avoid cross-agent conflicts.
- **AI tool/model:** Claude Code — Claude Opus 4.8 orchestrator; Claude Opus (Phase 3
  subagent) + Claude Sonnet (Phase 4 subagent).
- **AI-generated vs. human-reviewed/edited:** Both PRs were **fully AI-drafted** under strict
  gates (PR #2: ruff 0 / mypy 0 / 92 tests @ 97.13%; PR #3: ruff 0 / mypy 0 / 68 tests @
  97.64%). The **human owner ran an "Antigravity" code review** on both PRs (3 performance
  findings each) and **chose Option B** for the `hot.md` ranking (centrality × proximity to
  the bug node, over the pure-degree metric the subagent first shipped). Revisions to address
  the review findings + the ranking change are applied on the existing PR branches before
  merge. The Phase-3 subagent self-disclosed a partial-TDD deviation (the six signal bodies
  were written alongside their tests rather than strict RED-first; scaffolding units did
  follow RED→GREEN) — recorded honestly rather than overstated.

---

## Template for future entries

```markdown
### YYYY-MM-DD — Phase N (<phase name>)

- **Prompt summary:** <1-3 sentences describing what was asked>
- **AI tool/model:** <e.g. Claude Code — Claude Sonnet 4.6>
- **AI-generated vs. human-reviewed/edited:** <what the AI produced; what the human
  reviewed, changed, or rejected; any follow-up corrections>
```
