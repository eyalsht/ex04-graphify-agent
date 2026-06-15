<!-- EX04 PR template. Fill every section; a thin description fails pr-discipline. -->

## Summary
<!-- What does this PR do, in user-facing terms? -->

## Linked planning items
- Implements PRD §...
- Closes TODO items: `PHASEx-yyy`, ...
- Requirement(s): R...

## Changes
-

## Checklists
- [ ] `uv run ruff check .` clean
- [ ] `uv run ruff format --check .` clean
- [ ] `uv run mypy --strict src/` — 0 errors
- [ ] `uv run pytest --cov=src --cov-fail-under=90` green (keyless)
- [ ] `uv run pytest -m eval --no-cov` green (structural evals, pass^k)
- [ ] `python scripts/check_file_sizes.py` / `check_no_hardcoded.py` / `check_anti_patterns.py` pass
- [ ] TODO items ticked in this PR; README updated if user-visible
- [ ] PRE-FIX baselines (`artifacts/graphify/*`, `obsidian/*` except `hot.md`) untouched
- [ ] No provider API key committed; no hardcoded model/secret
