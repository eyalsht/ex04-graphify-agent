# PRD: graph_reader.py (+ obsidian_writer.py)

> Covers two modules. `graph_reader.py` is the query layer over the Graphify
> `graph.json`; `obsidian_writer.py` consumes those queries to emit the Obsidian
> vault's `hot.md`. Per brief §4, the Obsidian vault is treated as *graph_reader's
> output*, so both live in one PRD. Module names and the `graph.json` schema match
> brief §4 and `artifacts/graphify/graph.json` verbatim.

---

## Purpose

- **graph_reader.py** — Parse the pre-generated, read-only baseline graph
  `artifacts/graphify/graph.json` (23 nodes · 20 edges · 6 communities, per
  `GRAPH_REPORT.md`) into an in-memory graph and expose typed queries used by
  `weakness_detector.py` and `obsidian_writer.py`: per-node degree, per-node
  betweenness centrality, community grouping, and confidence filtering over edges
  (`EXTRACTED` / `INFERRED` / `AMBIGUOUS`). It is the single read path to the graph —
  no other module parses `graph.json` directly (R5.2.1).
- **obsidian_writer.py** — Generate `obsidian/hot.md`, the prioritized "where to look
  first" note (R5.1.4, R5.6.1). It ranks nodes by a graph metric (not arbitrary) and
  emits a Markdown list of `[[node_id|Label]]` wikilinks that resolve against the
  existing vault's note files.

## Inputs

### graph_reader.py
- `artifacts/graphify/graph.json` — NetworkX node-link JSON. Top-level keys:
  `directed: false`, `multigraph: false`, `graph: {}`, `nodes: [...]`, `links: [...]`,
  `hyperedges: []`.
  - Node fields used: `id` (e.g. `polygons_polygons_polygon`), `label` (e.g. `Polygon`),
    `file_type` (`code` | `document` | `rationale`), `source_file`, `source_location`,
    `community` (int 0–5), `norm_label`.
  - Edge (`links`) fields used: `source`, `target`, `relation`, `confidence`
    (`EXTRACTED` | `INFERRED`; `AMBIGUOUS` is a valid value but absent in this graph —
    0% AMBIGUOUS per `GRAPH_REPORT.md`), `confidence_score` (float, e.g. `0.8`, `0.9`,
    `1.0`), `weight`.
- Path is config-driven, not hardcoded (CLAUDE.md non-negotiable): default
  `artifacts/graphify/graph.json`, overridable via constructor arg.

### obsidian_writer.py
- A constructed `GraphReader` instance (dependency-injected, not re-parsed).
- The vault directory `obsidian/` (to confirm the note-naming convention; default
  config-driven path).
- `top_k` for `hot.md` (default config value, e.g. `5`).

## Outputs

### graph_reader.py
- Pure return values (no file writes). Typed dataclasses / NamedTuples:
  `NodeView(id, label, file_type, source_file, source_location, community, degree,
  betweenness)` and `EdgeView(source, target, relation, confidence, confidence_score,
  weight)`.

### obsidian_writer.py
- Writes `obsidian/hot.md` (Markdown). **It must NOT touch the read-only baselines**
  (`graph.json`, `GRAPH_REPORT.md`, `index.md`, per-node notes) — `hot.md` is the only
  file this module creates/overwrites (brief §2 "do not overwrite baselines"; brief §6
  EX04 additions).

## Public interface (sketch — signatures only, no implementation)

```python
# graph_reader.py
from dataclasses import dataclass

@dataclass(frozen=True)
class NodeView:
    id: str
    label: str
    file_type: str
    source_file: str
    source_location: str | None
    community: int
    degree: int
    betweenness: float

@dataclass(frozen=True)
class EdgeView:
    source: str
    target: str
    relation: str
    confidence: str           # "EXTRACTED" | "INFERRED" | "AMBIGUOUS"
    confidence_score: float
    weight: float

class GraphReader:
    def __init__(self, graph_path: str = "artifacts/graphify/graph.json") -> None: ...

    def node(self, node_id: str) -> NodeView: ...
    def all_nodes(self) -> list[NodeView]: ...
    def degree(self, node_id: str) -> int: ...
    def betweenness(self, node_id: str) -> float: ...
    def top_n_by_degree(self, n: int) -> list[NodeView]: ...          # tie-break: betweenness DESC, then id ASC
    def top_n_by_betweenness(self, n: int) -> list[NodeView]: ...
    def nodes_in_community(self, community: int) -> list[NodeView]: ...
    def communities(self) -> dict[int, list[NodeView]]: ...
    def edges_with_confidence(self, confidence: str) -> list[EdgeView]: ...
    def inferred_edges_below(self, threshold: float) -> list[EdgeView]: ...   # confidence == INFERRED and score < threshold
    def edges_of(self, node_id: str) -> list[EdgeView]: ...
    def node_exists(self, node_id: str) -> bool: ...

# obsidian_writer.py
class ObsidianWriter:
    def __init__(self, reader: GraphReader, vault_dir: str = "obsidian") -> None: ...

    def rank_hot_nodes(self, top_k: int = 5) -> list[NodeView]: ...   # (degree DESC, betweenness DESC, id ASC)
    def wikilink(self, node: NodeView) -> str: ...                    # "[[<id>|<Label>]]"
    def render_hot_md(self, top_k: int = 5) -> str: ...               # returns markdown text
    def write_hot_md(self, top_k: int = 5) -> str: ...                # writes obsidian/hot.md, returns path
```

## Behavior / algorithm

### graph_reader.py
1. **Load.** Read JSON; reconstruct a graph with `networkx.node_link_graph(data,
   edges="links")`. **networkx dependency is assumed and reasonable** for this course
   project: it is the canonical reader for this exact `node_link` schema (the file was
   produced by it — note `"links"` key), it provides correct betweenness, and it is a
   standard, pure-Python, well-maintained dep installable via `uv add networkx`. This is
   recorded as a minor dependency decision (no separate ADR needed; cite here).
2. **Degree.** `G.degree(node_id)`. For this baseline graph the expected degrees include
   `polygons_polygons_polygon` (Polygon) = **4** — the god node (GRAPH_REPORT "God
   Nodes" #1) — `mathsquiz_readme_maths_quiz` = 3,
   `polygons_polygons_calc_polygon_details` = 2, `readme_broken_python` = 2, and the
   three `polygons_polygons_rationale_{18,33,50}` = 1 each.
3. **Betweenness.** `networkx.betweenness_centrality(G)`. `polygons_polygons_polygon` is
   the highest cross-community bridge (GRAPH_REPORT cites betweenness ≈ 0.056 for it).
4. **Community grouping.** Bucket nodes by their `community` int → `dict[int,
   list[NodeView]]` (communities present: 0,1,2,3,4,5).
5. **Confidence filtering.** `edges_with_confidence("INFERRED")` returns the 2 inferred
   edges; `inferred_edges_below(threshold)` returns INFERRED edges with
   `confidence_score < threshold` (e.g. threshold `0.85` returns the
   `semantically_similar_to` edge at 0.8 but not the `conceptually_related_to` edge at
   0.9).

### obsidian_writer.py
1. **Rank.** `rank_hot_nodes(top_k)` sorts all nodes by **(degree DESC, then betweenness
   DESC, then id ASC)** and takes the first `top_k`. This is the EXACT `hot.md` metric
   (satisfies R5.6.1 "derived using a graph metric — not arbitrary": primary = degree
   centrality, secondary = betweenness as proximity-to-bridge proxy).
2. **Wikilink convention.** Derived from the real vault: each note file is named
   `<node_id>.md` and `index.md` links as `[[<node_id>|<Label>]]` (e.g.
   `obsidian/polygons_polygons_polygon.md` → `[[polygons_polygons_polygon|Polygon]]`).
   `wikilink(node)` returns exactly `f"[[{node.id}|{node.label}]]"`.
3. **Render.** Emit a `# Hot — Where to look first` heading, a one-line metric
   disclosure, and an ordered list. Each item: the wikilink, plus `degree=D · bw=B ·
   community=C · source_file:source_location`. Top item for the PRE-FIX graph is
   `[[polygons_polygons_polygon|Polygon]]` (degree 4).
4. **Regeneration / POST-FIX.** `hot.md` **MUST be regenerated whenever `graph.json`
   changes** — i.e. `obsidian_writer` is re-run against
   `artifacts/graphify_post_fix/graph.json` after the fix to produce the POST-FIX
   `hot.md`. This is required so the R5.6.3 before/after diff story has a hot.md on both
   sides. (The PRE-FIX `obsidian/hot.md` baseline, once committed, is itself a graded
   artifact and is not silently overwritten; the POST-FIX render targets the post-fix
   vault path — exact path decided in PLAN.md.)

## Edge cases

- **Isolated node.** `license_mit_license` (MIT License) has degree 1 and is the lone
  "isolated" node per GRAPH_REPORT "Knowledge Gaps"; `top_n_by_*` must still return it
  deterministically via the id tie-break, never crash.
- **`AMBIGUOUS` confidence absent.** `edges_with_confidence("AMBIGUOUS")` must return
  `[]` (not raise) — the value is valid in the schema though unused in this graph.
- **`source_location` is `null`.** Document nodes (e.g. `license_mit_license`,
  `readme_broken_python`) and several edges have `source_location: null`; `NodeView`/
  `EdgeView` must accept `None` and `hot.md` must render it gracefully (omit `:Lxx`).
- **`Object` node has empty `source_file`.** Node `object` (label `Object`) has
  `source_file: ""`; must not be mistaken for a real file path.
- **Duplicate labels across communities.** `welcome_message()`, `ask_question()`,
  `print_final_scores()` each appear twice (step2 & step3) with different `id`s —
  wikilinks must key on `id`, never `label`, to stay unique.
- **Unknown node id.** `node()` / `degree()` on a missing id raises `KeyError`;
  `node_exists()` is the safe probe.
- **`top_n` with `n` > node count.** Returns all nodes, no padding.

## Test cases (for TDD — Given/When/Then; become docs/TODO.md tasks)

- **GR-T1 (load).** Given `artifacts/graphify/graph.json`, When `GraphReader` is
  constructed, Then `len(all_nodes()) == 23` and total edges == 20.
- **GR-T2 (degree god node).** Given the baseline graph, When `degree("polygons_polygons_polygon")`,
  Then it returns `4`.
- **GR-T3 (top-N by degree).** Given the graph, When `top_n_by_degree(1)`, Then the
  single result has `id == "polygons_polygons_polygon"` and `label == "Polygon"`.
- **GR-T4 (community grouping).** Given the graph, When `nodes_in_community(1)`, Then the
  result ids == `{polygons_polygons, polygons_polygons_draw_polygon,
  polygons_polygons_rationale_18, polygons_polygons_rationale_33,
  polygons_polygons_rationale_50}` (the polygons.py + draw_polygon + 3 rationale nodes).
- **GR-T5 (inferred filter).** Given the graph, When `edges_with_confidence("INFERRED")`,
  Then exactly 2 edges return: `mathsquiz_mathsquiz_final_py→mathsquiz_mathsquiz`
  (score 0.8) and `mathsquiz_readme_maths_quiz→readme_broken_python` (score 0.9).
- **GR-T6 (inferred below threshold).** Given the graph, When `inferred_edges_below(0.85)`,
  Then exactly 1 edge returns (the 0.8 `semantically_similar_to` edge).
- **GR-T7 (ambiguous empty).** Given the graph, When `edges_with_confidence("AMBIGUOUS")`,
  Then returns `[]`.
- **OW-T1 (hot ranks Polygon first — PRE-FIX).** Given the baseline graph, When
  `rank_hot_nodes(5)`, Then `result[0].id == "polygons_polygons_polygon"` (Polygon, the
  degree-4 god node ranks at the top).
- **OW-T2 (wikilink format).** Given the `Polygon` NodeView, When `wikilink(node)`, Then
  returns exactly `"[[polygons_polygons_polygon|Polygon]]"`.
- **OW-T3 (render contains links + metric).** Given the graph, When `render_hot_md(5)`,
  Then output contains `[[polygons_polygons_polygon|Polygon]]` and a line disclosing the
  ranking metric (degree DESC, betweenness DESC).
- **OW-T4 (write + idempotent regenerate).** Given a temp vault dir, When `write_hot_md()`
  runs twice, Then `obsidian/hot.md` exists and the second write byte-equals the first
  (deterministic — supports the R5.6.3 diff being attributable to graph change, not
  render noise).
- **OW-T5 (baseline untouched).** Given the vault, When `write_hot_md()`, Then
  `index.md` and `polygons_polygons_polygon.md` are unmodified (mtime/hash unchanged).

## Requirement traceability (ASSIGNMENT.md)

- **R5.1.1** — consumes the Graphify `graph.json` output (read path).
- **R5.1.2** — wikilink convention matches the per-node vault notes (`[[id|Label]]`).
- **R5.1.3** — complements `index.md` (graph_reader queries back the same nodes/communities).
- **R5.1.4 / R5.6.1** — `hot.md` produced via a graph metric (degree + betweenness),
  distinct from `index.md`.
- **R4.3** — `top_n_by_degree` / `top_n_by_betweenness` surface the God Nodes that
  reveal core abstractions and coupling risk (Polygon).
- **R5.6.3** — deterministic regeneration of `hot.md` against the POST-FIX graph enables
  the before/after diff.

## Dependencies on other modules

- **Depends on:** `networkx` (external; betweenness + node_link parsing). No dependency
  on other `ex04_graphify_agent` modules (it is the lowest layer).
- **Depended on by:** `weakness_detector.py` (all six signals query through
  `GraphReader`), `obsidian_writer.py` (injected `GraphReader`), and indirectly
  `agent_workflow/` (via `read_vault` reading the generated `hot.md`).
