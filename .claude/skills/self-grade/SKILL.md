---
name: self-grade
description: |
  Use this skill when ready to compute the final self-assessed grade for submission. Triggers include:
  "self grade", "final grade", "ready to submit", "compute the grade",
  "self-assess", "what's our score", "how are we scored", "grade ourselves",
  "submission check", "before we submit".
  Apply only at the end of the project, after all other work is complete.
---

# Self-Grade

Computes a defensible self-assessed grade for EX04, with strict honesty
(`CLAUDE.md` §3: "Honest self-grade … conservative, defensible number"; R8.9).

## When to run

Self-grade is the final step before submission. Run it only when:
- All planned commits are merged to main
- CI on main is green (ruff, mypy --strict, pytest ≥90% coverage, file-size, no-hardcoded)
- The full keyless test suite passes with **no provider API key set** (e.g. no `GEMINI_API_KEY`) (ADR-0005)
- README is complete and the deliverables in `docs/ASSIGNMENT.md` §7 (R7.x) exist as artifacts
- `docs/KNOWN_LIMITATIONS.md` is current

## How to compute

The repo has `scripts/self_grade.py` that produces a numeric score automatically (keyless):

```bash
uv run python scripts/self_grade.py
```

> **No official numeric rubric weights were extractable from the PDF** — see
> `docs/KNOWN_LIMITATIONS.md` item 2 (the assignment PDF's Hebrew body uses a custom font
> encoding that standard extractors can't decode, so `docs/ASSIGNMENT.md` was reconstructed
> from the cleanly-extractable English/technical terms plus the owner's digest). **The
> weights below are this project's own best-guess allocation for self-tracking purposes; do
> not over-index on the exact numbers — the qualitative checklist matters more.** The
> categories are derived from `docs/ASSIGNMENT.md` §10 (Expectations) and the §7 deliverables
> (R7.x).

Output (illustrative — categories from §10/§7, weights are this project's own allocation):
```
=== Self-Grade Report (best-guess weights — not an official rubric) ===

Graph/Obsidian artifacts:          18 / 20
  - graph.json parsed correctly:    5 / 5
  - hot.md derived (centrality×prox):4 / 5  (proximity weight tuning is a judgment call)
  - vault consistent with graph:    5 / 5
  - PRE-FIX baseline untouched:     4 / 5  (one regen run targeted a scratch dir — verify)

Agent workflow + token evidence:   22 / 25
  - graph-guided vs naive runs:    10 / 10
  - token numbers traced to logs:   8 / 10  (one per-node row needs a log cross-check)
  - fix correctness (pentagon/hex): 4 / 5

Code quality (ruff/mypy/coverage): 23 / 25
  - Ruff:                           5 / 5
  - Mypy --strict:                  5 / 5
  - File sizes (≤150):              5 / 5
  - Coverage (92%):                 5 / 5
  - Anti-patterns:                  3 / 5  (one TODO comment left in signals.py)

Documentation (PRD/PLAN/ADR/...):  14 / 15
  - PRD/PLAN/ADR/TODO complete:     8 / 8
  - PROMPTS.md (reviewer trail):    3 / 4
  - KNOWN_LIMITATIONS honesty:      3 / 3

Root-cause + OOP narrative:        13 / 15
  - root-cause writeup:             7 / 8
  - before/after OOP improvement:   6 / 7  (could tie Polygon refactor to PART-C signal 6)

=== Total: 90 / 100 ===
```

## Honesty rules

1. **Never report > 95 without explicit override.** A score of 95+ implies near-perfection. If the script outputs 96+, the prompt should:
   - Re-run with `--strict` flag to apply harsher penalties
   - Audit each "5/5" rubric item with skepticism
   - Lower at least one rubric item by 1 if any judgment call was made

2. **The grader's number is the ground truth.** Dr. Segal's grading agent will produce its own number. If your self-grade differs by too much you lose accuracy credit. Therefore: target slightly below your honest assessment. If you think the work is 92, report 90.

3. **Justification > number.** The submission PDF must include a written justification of the score, broken down by category. The number is meaningless without the explanation — and doubly so here, since the weights are unofficial best-guesses (see the extraction caveat above).

## What gets graded (categories derived from `docs/ASSIGNMENT.md` §10 + §7 — weights unofficial)

| Category | Best-guess weight | What's measured |
|----------|-------------------|-----------------|
| Graph/Obsidian artifacts | 20 | graph.json read correctly, `hot.md` derived from a documented centrality×proximity metric, vault consistent with the graph, PRE-FIX baseline untouched |
| Agent workflow + token-efficiency evidence | 25 | graph-guided vs naive runs, token numbers traced to gatekeeper logs (not estimates), fix correctness (pentagon 540/108, hexagon 720/120, mocked-turtle sides) |
| Code quality (ruff/mypy/coverage) | 25 | Ruff 0, mypy --strict 0 on src/, files ≤150 lines, coverage ≥90%, no hardcoded values |
| Documentation (PRD/PLAN/ADR/TODO/PROMPTS/KNOWN_LIMITATIONS) | 15 | completeness + honesty of the planning/process docs |
| Root-cause + OOP improvement narrative | 15 | root-cause writeup for `polygons.py` and the before/after OOP refactor of the `Polygon` class |

> **Reminder:** these weights are *this project's own* allocation, not extracted from the
> official rubric (none was machine-readable — `KNOWN_LIMITATIONS.md` item 2). Treat the
> qualitative checklist as the real signal; the numbers are scaffolding for self-tracking.

## Generating the submission PDF

```bash
uv run python scripts/generate_submission_pdf.py
```

This produces `submission.pdf` containing:
- Cover page: both names, both student IDs, repo URL
- Self-grade with full justification (the report above, expanded into prose, including the
  "weights are unofficial" caveat)
- Brief summary of the root-cause + token-comparison findings
- Link to the live README on GitHub

The PDF is uploaded to Moodle. Verify before uploading:
- **Both student IDs are correct and not placeholders.** `pyproject.toml` `[project] authors`
  is currently a placeholder (Eyal Shtinmetz + Imri, IDs TODO — `docs/KNOWN_LIMITATIONS.md`
  item 1). Do not submit while this is unresolved.
- Repo URL is the public GitHub URL, not a private fork
- Date is current

## Anti-patterns to refuse

If asked to:
- **Report a grade > 95** → require override + audit
- **Submit while `pyproject.toml` authors are still placeholders** → refuse (KNOWN_LIMITATIONS item 1)
- **Submit without `KNOWN_LIMITATIONS.md` entries** → refuse, hidden imperfections cost more than documented ones
- **Submit with CI red on main** → refuse, fix first
- **Skip the justification text** → require it; the number alone won't survive grading
- **Present the best-guess weights as an official rubric** → refuse; always carry the extraction caveat
- **Backdate the submission** → refuse, never falsify timestamps

## Verification before submission

Final pre-submission checklist:
- [ ] Quality gates green on main (ruff, mypy --strict, pytest ≥90% cov, file-size, no-hardcoded)
- [ ] Full test suite passes **keyless** (no provider API key set, e.g. no `GEMINI_API_KEY`)
- [ ] `scripts/self_grade.py` reports a defensible number with breakdown + caveat
- [ ] `submission.pdf` has correct (non-placeholder) student IDs and current date
- [ ] Repo is public (not private)
- [ ] `docs/PROMPTS.md` is truthful and complete
- [ ] `docs/KNOWN_LIMITATIONS.md` lists every documented imperfection
- [ ] README renders correctly on github.com
- [ ] Both partners reviewed the final state

Only when all are checked → upload PDF to Moodle.
