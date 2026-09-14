# ADR-0003 — Paths are parameters; no upward config discovery

- **Status:** Accepted
- **Date:** 2026-09-14

## Context

Every layer of the origin project found its data by walking up the filesystem from `__file__` until
it hit a directory containing its own config file — `graph_reader/loader.py` looked for
`config/paths.json`, `gatekeeper/config.py` for `config/agent.json`, `weakness_detector/config.py`
for `config/weakness_thresholds.json`, and `self_grade/config.py` simply took `parents[3]`. Three
near-identical cached loaders, plus two modules that bypassed all of them and read `paths.json`
inline.

The consequence: the package could only operate on the checkout it lived in. Every input path
(`data_repo_root`, `graph_json`, `obsidian_dir`) was a repo-relative string in a committed JSON file,
and no SDK method accepted a target-repo argument. Pointing it at another repository meant editing
config, and pointing it at two repositories in one process was impossible.

## Decision

One immutable `RunPaths` value object, constructed from CLI arguments, carries every path:

```python
@dataclass(frozen=True)
class RunPaths:
    repo_root: Path  # the repository being explained
    out_dir: Path  # where graph/vault/brief are written (default: <repo>/.atlas)
    config_path: Path  # the atlas config in use
```

It is threaded explicitly through the SDK into every layer. No module reads a global, walks up a
tree, or caches a root. `config/atlas.json` holds behaviour (provider, model, thresholds, budgets) —
never locations.

## Consequences

**Good.** `atlas map ~/some/other/repo` works with no edit to anything. Multiple targets can be
processed in one process. Tests build paths under `tmp_path` with no monkeypatching of module-level
caches. The three duplicated loaders collapse into one.

**Cost.** Every public function grows a parameter, and the convenience of `GraphReader()` with no
arguments is gone — construction now requires saying which graph. That explicitness is the point.
