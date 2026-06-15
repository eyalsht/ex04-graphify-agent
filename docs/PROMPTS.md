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

## Template for future entries

```markdown
### YYYY-MM-DD — Phase N (<phase name>)

- **Prompt summary:** <1-3 sentences describing what was asked>
- **AI tool/model:** <e.g. Claude Code — Claude Sonnet 4.6>
- **AI-generated vs. human-reviewed/edited:** <what the AI produced; what the human
  reviewed, changed, or rejected; any follow-up corrections>
```
