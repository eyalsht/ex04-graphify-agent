---
name: commit-discipline
description: |
  Use this skill before creating any git commit. Triggers include:
  "ready to commit", "let me commit", "git commit", "stage the changes",
  "what should I include in this commit", "let's commit this", "time to commit".
  Always apply before staging files or running git commit.
---

# Commit Discipline

Enforces atomic commits, Conventional Commits format, and pre-commit verification per
CLAUDE.md §3 / §7 (continuous history, ≤~300 lines/commit, no mass-commits).

## Pre-flight checks (run before staging)

1. **Verify you're not on `main`:**
   ```bash
   git branch --show-current
   ```
   If output is `main` → STOP. Create a feature branch first:
   ```bash
   git checkout -b <yourname>/<phase>-<short-name>
   ```

2. **Check the diff size:**
   ```bash
   git diff --stat
   ```
   - Target: ≤ ~300 changed lines per commit (CLAUDE.md §3).
   - If > 300: split into multiple atomic commits, one per concern.

3. **Verify TODO items:** if this commit completes any TODO checkbox in `docs/TODO.md`, tick it as part of this commit.

4. **Verify docstrings:** if any new public function/class was added, confirm it has a docstring with params, returns, raises, and example.

## Commit message format (Conventional Commits)

```
<type>(<scope>): <subject>

<optional body explaining WHY>

<optional footer (Co-Authored-By, Closes #N, etc.)>
```

### Types

| Type | When |
|------|------|
| `feat` | New feature visible to users |
| `fix` | Bug fix |
| `docs` | Documentation only — no code change |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or fixing tests (but not the impl) |
| `chore` | Tooling, config, dependencies |
| `perf` | Performance improvement |
| `style` | Formatting, no logic change |
| `ci` | CI/CD configuration |

### Scope

The package or module touched: `graph_reader`, `weakness_detector`, `obsidian_writer`,
`agent_workflow`, `gatekeeper`, `token_comparison`, `sdk`, `cli`, `docs`, `config`,
`scripts`.

### Subject

- ≤ 72 characters
- Imperative mood ("add" not "added", "fix" not "fixed")
- No period at end
- Lowercase except for proper nouns

### Examples (good)

```
feat(weakness_detector): detect god-node signal for Polygon (degree=4)

The god-node detector flags polygons_polygons_polygon — the highest-degree
node in artifacts/graphify/graph.json — as PART-C signal #1 (coupling /
dead-class bug). The hypothesis carries an INFERRED tag until Validate opens
data/broken-python/polygons/polygons.py and confirms the dead Polygon class.
```

```
test(token_comparison): failing tests TC-T1 through TC-T8 per PRD_token_comparison.md
```

```
fix(gatekeeper): read provider API key (GEMINI_API_KEY) from os.environ only, never config

Hardcoding/reading the key from config/agent.json violated the no-secrets
non-negotiable (CLAUDE.md §3). Keyless-by-default selects the mock client
when the env var is absent.

Closes #14
```

### Examples (bad)

```
update files                                 # no type, no scope, vague
feat: stuff                                  # vague
feat(graph_reader): added the degree fn      # past tense ("added" is wrong)
WIP                                          # never commit WIP to main; if needed for backup, use a branch
```

## Co-authoring

If pairing or carrying over someone else's work:

```bash
git commit -m "feat(agent_workflow): LangGraph state schema per Imri's PRD_agent_workflow.md

Co-Authored-By: Imri <SURNAME> <imri@example.com>"
```

GitHub renders this with both avatars on the commit page. (Note: `pyproject.toml` authors are
still placeholders — see `docs/KNOWN_LIMITATIONS.md` item 1; fill real IDs before submission.)

## Pre-commit hooks

The repo has hooks installed via `.pre-commit-config.yaml`. They run automatically on `git commit`:
- `ruff check --fix`
- `ruff-format`
- `mypy --strict src/`
- `python scripts/check_file_sizes.py`  (≤150 lines)
- `python scripts/check_no_hardcoded.py`
- `python scripts/check_anti_patterns.py`

If any fail, commit is aborted. Read the output, fix, re-stage, re-commit.

## Anti-patterns to refuse

If the user asks to:
- **Commit "WIP" or unfinished work to main** → refuse; suggest a feature branch instead
- **Skip pre-commit hooks (`git commit --no-verify`)** → refuse unless there's a documented emergency reason in `docs/PROMPTS.md`
- **Commit with vague messages like "fixes" or "update"** → push back and request a Conventional Commit message
- **Bundle a refactor with a feature in one commit** → suggest splitting into two commits
- **Commit secrets, `.env` files, any provider API key (e.g. `GEMINI_API_KEY`), or absolute/`AI Agent` author strings** → refuse and explain
- **Overwrite a PRE-FIX baseline artifact** (`artifacts/graphify/*`, `obsidian/*` except `hot.md`) → refuse; POST-FIX graph output goes in a separate dir (CLAUDE.md §4)

## Verification before signaling success

After running `git commit`, verify:
```bash
git log -1 --format=fuller
```

Confirm:
- Author and committer are correct (real student names, not placeholders)
- Subject matches Conventional Commits format
- File list matches what was intended
