# Provenance — the golden fixture

This directory is the golden regression oracle for `repo-atlas`'s extractor
(`docs/adr/0001-own-ast-extractor.md`, "Verification"): a known 5-file target repo plus
the reference graph the origin project's Graphify run produced over it. **Only the
extractor's golden-regression eval and `tests/fixtures/test_golden_provenance.py` may
read this directory** — every other test builds its own graph with
`tests/fixtures/graph_factory.py` (`CLAUDE.md` §7, `.claude/skills/eval-harness/SKILL.md`).

Nothing here is regenerated or hand-edited. If a file under this directory ever needs
to change, it means the pin below is being deliberately moved — update this document's
hashes and the "why the pin exists" evidence in the same commit, and expect
`test_golden_provenance.py` to fail until you do.

## Origin commit

All files are vendored from the origin project (`ex04-graphify-agent`) at:

- **Commit:** `23b8ee2196fb3681fb847e5de4b6739b8c81733e` (`23b8ee2`)
- **Subject:** `chore: vendor target repo + pre-fix Graphify artifacts + Obsidian vault`
- **Author:** Eyal Shtinmtez `<eyalshtinmetz@gmail.com>`, 2026-06-15
- HEAD of the origin project at the time this fixture was vendored was `543a9a1`, 88
  commits ahead of `23b8ee2` on the same line of history (`git merge-base --is-ancestor
  23b8ee2 HEAD` succeeds).

Every file below was extracted with the same command shape, substituting the path:

```bash
git show 23b8ee2:<repo-relative-path> > tests/fixtures/golden/<destination>
```

For example, the two files this fixture is built around:

```bash
git show 23b8ee2:artifacts/graphify/graph.json > tests/fixtures/golden/reference_graph.json
git show 23b8ee2:data/broken-python/polygons/polygons.py > tests/fixtures/golden/broken-python/polygons/polygons.py
```

All 8 source files are pinned to this one commit — not just `polygons.py` — so that
the whole fixture traces to a single, unambiguous point in history rather than "7 files
from wherever HEAD happened to be plus 1 from a blob."

## Why `polygons.py` must be pinned (the trap)

`data/broken-python/polygons/polygons.py` was rewritten **twice** after `23b8ee2` — the
working tree's current version is not the file the reference graph was built from, even
though every other vendored file happens to be untouched since that commit.

Verified directly (`diff` between `git show 23b8ee2:...` and the current working tree):

| File | Identical to `23b8ee2`? |
|---|---|
| `LICENSE.txt` | yes, byte-identical |
| `README.md` | yes, byte-identical |
| `mathsquiz/README.md` | yes, byte-identical |
| `mathsquiz/mathsquiz.py` | yes, byte-identical |
| `mathsquiz/mathsquiz-step1.py` | yes, byte-identical |
| `mathsquiz/mathsquiz-step2.py` | yes, byte-identical |
| `mathsquiz/mathsquiz-step3.py` | yes, byte-identical |
| `polygons/polygons.py` | **no** — rewritten twice, 75 → 53 lines |

`artifacts/graphify/graph.json` itself is also byte-identical between `23b8ee2` and the
current working tree (it is the immutable PRE-FIX baseline — outer `CLAUDE.md` §4).

Line-count evidence: `git show 23b8ee2:data/broken-python/polygons/polygons.py | wc -l`
→ **75**. The current working tree's `data/broken-python/polygons/polygons.py` is
**53** lines. The reference graph (`reference_graph.json`) encodes AST-origin nodes and
edges with `source_location` values taken from the 75-line version — `L3`, `L5`, `L13`,
`L18`, `L29`, `L33`, `L41`, `L50` for the class, `__init__`, `calc_polygon_details`, the
first `# TODO:`, the buggy `new Polygon(...)` call, the second `# TODO:`, `draw_polygon`,
and the third `# TODO:` respectively.

Against the *current* working tree, only the file-root reference (`L1`, trivially always
line 1) still lines up. Every other reference is wrong: the current file has already
been bug-fixed (`class Polygon(object):`, no `new`, a real `return poly`), so:

- `class Polygon` is now at line 4, not 3; `__init__` at line 6, not 5;
  `calc_polygon_details` at line 14, not 13; `draw_polygon` at line 28, not 41.
- The `new Polygon(...)` bug the `calc_polygon_details -> polygon` `calls` edge cites at
  `L29` no longer exists at all — line 22 now reads `poly = Polygon(sides,
  internal_angles_sum, internal_angle)`, with no `new` keyword.
- All three `# TODO:` comments (`L18`, `L33`, `L50`) — and the three `rationale`-typed
  nodes the reference graph derived from them — are gone from the current file entirely.

So of the 9 distinct `polygons/polygons.py` source-location references the reference
graph makes (8 node locations + the one edge-only `L29` reference), 8 no longer resolve
to anything meaningful in the working tree; only the trivial file-root `L1` still does.
Regenerating this fixture from the working tree instead of the pin would silently
desync the golden graph's line numbers from the source it claims to describe, and would
delete the three `rationale` nodes and their `rationale_for` edges outright — this is
exactly the failure mode `test_golden_provenance.py` exists to catch.

Content-addressed anchor (independent of any path or branch): the git blob SHA of the
pinned `polygons.py` is `224e921d21badad4ba89fca97b0051e431483290`
(`git rev-parse 23b8ee2:data/broken-python/polygons/polygons.py`).

## Known properties of the vendored source (informational, for later phases)

`ast.parse` (Python 3) rejects two of the five vendored `.py` files:

- `mathsquiz/mathsquiz.py` — Python 2 `print` statement (`SyntaxError` at line 3:
  "Missing parentheses in call to 'print'").
- `polygons/polygons.py` (this pinned blob) — the `new Polygon(...)` JavaScript-style
  bug at line 29 (`SyntaxError`: "invalid syntax").

`mathsquiz/mathsquiz-step1.py`, `mathsquiz-step2.py`, and `mathsquiz-step3.py` all parse
cleanly. The extractor (`docs/adr/0001-*`, Phase 1) must tolerate a per-file
`SyntaxError` without failing the whole run (`PHASE1-009`/`PHASE1-010`) — this fixture
is why that requirement exists.

## SHA-256 of every vendored file

Computed with `sha256sum`, paths relative to this directory. `test_golden_provenance.py`
recomputes and checks every row below on each run.

| Vendored path | SHA-256 |
|---|---|
| `reference_graph.json` | `910af6f0b0e92e87c6345cfede18d9451750cd8e30e526c39d5f38446713129e` |
| `broken-python/LICENSE.txt` | `aa5440d7a42d9344344de5af77ba54a13439b1cc2a982811d82078b47c17c3d5` |
| `broken-python/README.md` | `41d2da4d23394c1ce64702ac42d1f476decef3a8ef8b8f30edbaf77a2c743c4b` |
| `broken-python/mathsquiz/README.md` | `8f3d62f994db28766c0c1661ec241b336935264942186360db52f7eba25f57f8` |
| `broken-python/mathsquiz/mathsquiz.py` | `345d6d4ac36514739b9dee21329d13c5dcc20fdf57b4e6282fde4ffce7589b7e` |
| `broken-python/mathsquiz/mathsquiz-step1.py` | `447e9ce5c98387d30de8c1b2350ad5ef36b7a9b4eadaf2656b1f8a38ebed0d1c` |
| `broken-python/mathsquiz/mathsquiz-step2.py` | `ae77a5c4378cebef34436c016120dd847ab7469e878cd2275c6a9febd9afe045` |
| `broken-python/mathsquiz/mathsquiz-step3.py` | `2255ef444e9ebeaa18b97441a38a372392b48b9ba09693d8d4d479a5097140a6` |
| `broken-python/polygons/polygons.py` | `88ca435621890e06ce428b6688ee6ab9405fdddd71a5b3919a97509bb3054b5d` |

Reference graph shape: 23 nodes, 20 links (`reference_graph.json`, verified by
`json.load` + `len(...)` — no `networkx` needed just to count).
