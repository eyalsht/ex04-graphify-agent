---
name: pr-discipline
description: |
  Use this skill when ready to open a pull request or merge to main. Triggers include:
  "open a PR", "create pull request", "ready to merge", "let's review",
  "ship this", "let's open the PR", "time to merge", "submit for review",
  "let's get this into main".
  Always apply before invoking gh pr create or merging in the GitHub UI.
---

# PR Discipline

Enforces a clean PR workflow: up-to-date branch, all checks green, full PR description, README/TODO sync.

## Pre-PR checks (run before opening)

### 1. Branch is up to date with main

```bash
git checkout main
git pull
git checkout <your-branch>
git rebase main
```

If conflicts arise, resolve them before continuing. After rebasing, force-push:
```bash
git push --force-with-lease
```

### 2. All quality checks green

```bash
make grade
```

This runs the entire quality stack — EX04's actual gates (CLAUDE.md §2/§3):
- `uv run ruff check .` (0 violations required)
- `uv run mypy --strict src/` (0 errors)
- `uv run pytest --cov=src --cov-fail-under=90` (keyless — no provider API key set, ADR-0005)
- file-size check — every Python file (tests too) ≤150 lines
- no-hardcoded-values check — config from JSON/env only, secrets via `os.environ`

If any fails → STOP. Fix locally, commit, push. Don't open the PR yet.

> If `make grade` / a `scripts/` checker isn't wired yet, run the underlying commands above
> directly. Don't claim a gate passed that the project hasn't set up.

### 3. README is current

Verify that any user-visible behavior change is reflected in `README.md`:
- New `sdk.py` methods → mention in "What Is Currently Implemented"
- New `cli.py` commands → document in "Quickstart"
- New reports/artifacts (`reports/token_comparison.md`, `obsidian/hot.md`) → reference them

### 4. TODO is current

Open `docs/TODO.md`. For every item completed by this branch, tick the checkbox in the same commit (don't create a separate "update TODO" commit per item — bundle the ticks into the relevant feature commit).

### 5. Self-review

Open the GitHub compare view in your browser:
```
https://github.com/<owner>/<repo>/compare/main...<your-branch>
```

Read your own diff as if reviewing someone else's work. Check:
- [ ] Every file you intended to change is in the diff
- [ ] No accidental file inclusions (e.g., `.DS_Store`, IDE configs, the pristine `broken-python/` clone)
- [ ] No PRE-FIX baseline overwritten (`artifacts/graphify/*`, `obsidian/*` except `hot.md`)
- [ ] No commented-out code without `# TODO:` justification
- [ ] No `print()` debug statements left in production code
- [ ] No hardcoded values that should be config; no committed secrets
- [ ] Imports are clean (no unused, sorted)
- [ ] Tests cover all new logic, including edge cases, and run keyless

## Opening the PR

```bash
gh pr create --base main --head <your-branch>
```

The PR template (`.github/PULL_REQUEST_TEMPLATE.md`) loads automatically. Fill in **every** section:

### Summary

One paragraph: what does this PR do, in user-facing terms? Not "added function X" but "the agent now ranks `polygons_polygons_polygon` (the Polygon god node) at the top of `hot.md`."

### Linked planning items

Reference the PRD section, requirement IDs, TODO items, and any related issues:
```
- Implements PRD_graph_reader.md §metrics (degree/centrality)
- Satisfies R5.1.4 / R5.6.1 (hot.md derived metric)
- Closes TODO items: graph_reader §1.1, §1.2
- Related issue: #7
```

### Changes

Bulleted list of concrete changes:
```
- Added src/ex04_graphify_agent/graph_reader/metrics.py with degree/betweenness/centrality
- Added tests/unit/test_graph_reader/test_metrics.py with 12 keyless tests
- Updated docs/TODO.md to tick completed items
- Updated README.md "What Is Currently Implemented"
```

### Checklists

Tick every box in both author checklists (correctness + self-review). If something can't be ticked, explain why — `docs/KNOWN_LIMITATIONS.md` may need an entry.

## After opening the PR

### Wait for CI

CI runs automatically (ruff, mypy --strict, keyless pytest ≥90%). If it fails:
1. Read the failure output (click "Details" on the failing check).
2. Fix locally, commit, push (the PR auto-updates).
3. CI re-runs.

Don't merge with a red CI. Branch protection blocks it anyway.

### Independent review before merge

Green CI is necessary but not sufficient — a second pair of eyes should review every PR. Use
whichever of the following is set up for this course instance, and **document which path was
used in `docs/PROMPTS.md`**:

- **If the `antigravity-reviewer` skill is initialized for this repo** (same Antigravity /
  Gemini tooling as prior projects — see that skill), let its background reviewer post its
  findings, then address every accepted finding with follow-up commits on the same branch
  (fix-or-disclose; a rejected finding gets a brief reason in the PR thread, an unfixable one
  an entry in `docs/KNOWN_LIMITATIONS.md`).
- **If it is NOT set up for this course instance**, substitute a self-review pass using a
  **fresh Claude Code session with no prior context** (re-read `CLAUDE.md` + the relevant
  `docs/PRD*.md` cold) — plus, if available, **human partner (Imri) review**. Address findings
  on the same branch the same way.

Don't claim the Antigravity gate ran if this project never initialized it — be honest about
which review path was used.

### Human partner review (encouraged)

In this 2-person sprint, **human partner (Imri)** approval is encouraged. If the partner is
available, ping them; they leave comments; address them on the same branch. The human gate may
be relaxed when waiting blocks progress.

## Merging

**Precondition:** CI green **and** the independent review path above has run and its accepted
findings are addressed.

In the GitHub UI:
- **"Rebase and merge"** for atomic-commit PRs (preserves the individual commits)
- **"Squash and merge"** only if the PR has trivial WIP commits ("typo", "fixup")

Branch is auto-deleted on merge (configure in repo settings). Locally:
```bash
git checkout main
git pull
git branch -d <your-branch>
```

## Post-merge

Update `docs/PROMPTS.md` with a brief entry for this phase:
```markdown
## Phase 2 — graph_reader (PR #5)
**Driver:** Imri (Claude Code session)
**Reviewer:** self-review (fresh cold session) — antigravity-reviewer not initialized this instance
**Context loaded:** CLAUDE.md, PRD_graph_reader.md, PLAN.md §4.1
**Outcome:** graph_reader package with 12 keyless unit tests, all passing. 92% coverage.
```

## Anti-patterns to refuse

If asked to:
- **Open a PR without rebasing on main** → run rebase first
- **Skip `make grade` / the quality gates** → require the full check
- **Merge with a vague PR description** → require summary, linked items, changes list
- **Self-merge before CI is green** → refuse, branch protection blocks anyway
- **Merge with no independent review at all** → refuse; run one of the two review paths above
- **Force-push to `main`** → refuse, never. Branch protection blocks.
- **Open multiple PRs from the same branch** → suggest closing extras first
- **Leave a PR open with merge conflicts** → require rebase or close

## Verification

After merging, verify:
- `git log main --oneline -5` shows the PR commits
- The branch is deleted (or in a closed state)
- CI on `main` is still green
- `docs/PROMPTS.md` was updated (including which review path was used)
