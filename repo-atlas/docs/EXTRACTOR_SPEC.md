# Extractor spec — frozen contract

> Derived by cross-referencing the reference graph (`tests/fixtures/golden/reference_graph.json`,
> 23 nodes / 20 links) against the source it was built from. Every rule below is evidenced by that
> corpus unless marked **[EXTENSION]** — those are decisions we make because the corpus is silent.
>
> This file is the interface contract between the extractor modules. Change it by editing this
> file and saying so, never by quietly diverging in code.

## 0. Scope

The reference graph was produced by two pipelines: an AST pipeline (19 nodes, `_origin: "ast"`) and
a document pipeline (4 nodes, no `_origin`, carrying `source_url`/`author`/`captured_at`). **We
reproduce the AST pipeline only.** The document pipeline is out of scope (ADR-0001); its 4 nodes and
5 edges are the golden test's exclusion set.

The discriminator is `_origin`, **not** `file_type` — the 3 `rationale` nodes are `_origin: "ast"`
and in scope, while `mathsquiz_mathsquiz_final_py` is `file_type: "code"` and out of scope.

## 1. Data contract

```python
@dataclass(frozen=True)
class RawNode:
    id: str
    label: str
    norm_label: str  # always label.lower()
    file_type: str  # "code" | "rationale"
    source_file: str  # repo-relative POSIX path; "" for external symbols
    source_location: str | None  # "L<n>"; "" for external symbols
    origin: str  # "ast" | "scan"   (serialized as "_origin")


@dataclass(frozen=True)
class RawEdge:
    source: str
    target: str
    relation: str  # contains | method | inherits | calls | rationale_for
    confidence: str  # EXTRACTED | INFERRED | AMBIGUOUS
    confidence_score: float
    weight: float  # always 1.0
    source_file: str
    source_location: str | None
    context: str | None = None  # "call" on calls edges; omitted when None
```

## 2. Id derivation

`slug(s)` = `s.lower()` then `/` → `_`, `-` → `_`, `.` → `_`.

| Construct | Rule | Example |
|---|---|---|
| module | `slug(source_file minus a trailing `.py`)` | `mathsquiz/mathsquiz-step1.py` → `mathsquiz_mathsquiz_step1` |
| module-level function | `{module_id}_{name.lower()}` | `mathsquiz_mathsquiz_step2_welcome_message` |
| class | `{module_id}_{ClassName.lower()}` | `polygons_polygons_polygon` |
| method | `{class_id}_{name.strip('_').lower()}` | `Polygon.__init__` → `polygons_polygons_polygon_init` |
| rationale | `{module_id}_rationale_{1-based line}` | `polygons_polygons_rationale_18` |
| external symbol | `name.lower()` — bare, no prefix | `Object` → `object` |

Freeze these irregularities:

1. **Only a trailing `.py` is stripped, and it is stripped BEFORE slugging.** Strip after and you
   get `..._step1_py`, which is wrong.
2. **Dunder stripping is total on both sides**: `__init__` → `init`.
3. **Methods chain off the class id**, module-level functions off the module id. The class segment
   is what distinguishes them.
4. **External/unresolved symbols get a bare lowercase id, `source_file: ""`, `source_location: ""`**
   — empty strings, not `None`. This is the only place empty-string sentinels appear.
5. **Collisions are possible and are not disambiguated** by the reference (`__init__` vs `init`;
   `a-b.py` vs `a_b.py`; `Object` from two files). **[EXTENSION]** Detect a collision and raise a
   clear error naming both constructs rather than silently dropping one — a silently merged node is
   a wrong graph.
6. **[EXTENSION]** Nested functions/classes, dotted packages and decorators do not occur in the
   corpus. Decide: nested symbols chain off their parent's id exactly as methods chain off a class;
   `__init__.py` keeps its `__init__` segment via the module rule (no dunder stripping — that rule
   is for symbols, not paths); decorators are ignored for line numbers (see §4).

## 3. Labels and `norm_label`

`norm_label == label.lower()`, exactly and always. No trimming, no punctuation stripping.

| Node kind | `label` | Example |
|---|---|---|
| module | file basename **with** extension, case and hyphens preserved | `mathsquiz-step1.py` |
| module-level function | `{name}()` — empty parens | `calc_polygon_details()` |
| class | `{ClassName}` — **no parens** | `Polygon` |
| method | `.{name}()` — **leading dot**, class name not included | `.__init__()` |
| external symbol | name as written in source, case preserved | `Object` |
| rationale | full comment text, indentation stripped, `#` kept, trailing space stripped | `# TODO: find a better way to work this stuff out` |

The function/method label asymmetry (`welcome_message()` vs `.__init__()`) is real. Keep it.

## 4. `source_location`

Literal `"L"` + 1-based line. No padding, no ranges, no columns.

| Node kind | Value |
|---|---|
| module | **always `"L1"`**, regardless of where content starts |
| class / function / method | the `class`/`def` keyword line |
| rationale | the comment's own line |
| external symbol | `""` |

**[EXTENSION]** With decorators, use the `def`/`class` line, not the decorator line — this matches
CPython's `ast` `.lineno` on 3.8+.

## 5. Edges

Graph envelope is undirected (`"directed": false`), but `source`/`target` carry direction.

| Relation | Direction | `source_location` anchors to | Count in reference |
|---|---|---|---|
| `contains` | module → top-level symbol | the **target's** def/class line | 9 |
| `method` | class → method | the method's def line | 1 |
| `inherits` | subclass → base | the **class-header** line | 1 |
| `calls` | caller → callee | the **call-site** line | 1 |
| `rationale_for` | **rationale node → module node** (inverted vs `contains`) | the comment's line | 3 |

Rules with teeth:

- **`contains` is top-level only.** No `contains` edge to a method (methods are reached via
  `method`), and none to a rationale node.
- **`rationale_for` always targets the module node**, never the enclosing function — even though all
  three reference comments sit inside functions.
- **`calls` selection**: the call site must be lexically inside a `def`/`class`, AND the callee must
  be a bare `Name` resolving to a symbol defined in the same file. Module-level calls emit nothing.
  Builtins (`print`, `input`, `int`, `range`) and attribute calls (`turtle.Screen()`) are dropped.
  This is why the corpus yields exactly one `calls` edge despite 26 in-function call sites.
- **`calls` edges carry `context: "call"`.** No other relation has `context`.
- **No import edges at all**, despite `import turtle` / `import random` in the corpus. Negative
  constraint — assert it.
- **An unresolved base class still emits a node and an `inherits` edge** (`Object` is undefined in
  the source; the graph has it anyway).
- `weight` is `1.0` on every edge.

## 6. Confidence policy

| Situation | `origin` | `confidence` | `confidence_score` |
|---|---|---|---|
| Fact read from a successfully parsed AST | `ast` | `EXTRACTED` | `1.0` |
| Fact recovered by line scan after a `SyntaxError` | `scan` | `INFERRED` | `0.7` |
| Rationale comment (token stream, always available) | `ast` | `EXTRACTED` | `1.0` |

Every edge inherits the **weaker** confidence of its two endpoints: an edge between an `ast` node
and a `scan` node is `INFERRED`.

## 7. Unparseable files — the degraded path

Two of the five corpus files do not parse: `mathsquiz/mathsquiz.py` (Python-2 `print` statement) and
`polygons/polygons.py` (JavaScript `new` at L29). The reference graph nonetheless contains 9 nodes
and 9 edges from `polygons.py` — ~47% of the in-scope graph. A strict `ast.parse` extractor gets
none of it.

Required behaviour:

1. Try `ast.parse`. On success, everything from that file is `origin="ast"` / `EXTRACTED`.
2. On `SyntaxError`, **do not give up on the file.** Fall back to a line scan that recovers:
   - `class <Name>(<Base>, ...):` → class node + `inherits` edges to each base
   - `def <name>(` at column 0 → module-level function node
   - `def <name>(` indented directly under a class → method node of that class
   All of it tagged `origin="scan"` / `INFERRED` @ 0.7.
3. Call-site (`calls`) edges are **not** recovered from unparseable files. Documented gap: the
   reference's `polygons.py` L29 `calls` edge is unreachable for us. Record it in
   `docs/KNOWN_LIMITATIONS.md`.
4. Rationale extraction is unaffected — it runs off the raw line stream and never needs the AST.
5. Record every file that fell back, so `GRAPH_REPORT.md` can say so honestly.

## 8. Rationale (marker comment) nodes

- **Markers: `TODO`, `FIXME`, `XXX`, `HACK`** (word-boundary, case-sensitive as written). The corpus
  evidences `TODO` only; the other three are an **[EXTENSION]** — real repos use them the same way.
- Must run off the raw line/token stream, not the AST: comments are stripped by `ast`, and this path
  must survive `SyntaxError`.
- Only whole-line comments qualify **[EXTENSION]** — a trailing `x = 1  # TODO: fix` is not a
  rationale node, to keep the graph from filling with inline noise. Test this decision explicitly.
- `file_type: "rationale"`, `origin: "ast"`, one `rationale_for` edge to the module node.
- A configurable cap on rationale nodes per file **[EXTENSION]** — a repo with 400 TODOs should not
  drown its own graph. Default from config; document it.

## 9. Envelope

```json
{"directed": false, "multigraph": false, "graph": {}, "nodes": [...], "links": [...]}
```

`community` is assigned after the graph is built, by `communities.py`. **It is not comparable to the
reference** — the reference's partition was computed over the full graph including the 5
document-pipeline edges we do not produce. The golden test must not assert `community`.

## 10. What the golden test asserts

In scope: **19 nodes, 15 edges** (9 `contains`, 3 `rationale_for`, 1 `calls`, 1 `inherits`,
1 `method`).

1. Node ids and their `(label, file_type, source_file, source_location, norm_label)` tuples.
2. Edge tuples `(relation, source, target, weight, source_file, source_location)`, plus
   `context == "call"` on the single `calls` edge.
3. These 4 node ids are **absent**: `license_mit_license`, `readme_broken_python`,
   `mathsquiz_readme_maths_quiz`, `mathsquiz_mathsquiz_final_py`; and the 5 edges touching them.
4. Zero import edges; zero `calls` edges from module-level call sites.
5. **Not** `community`, and **not** `confidence` on nodes recovered via the degraded path — those
   are `INFERRED`/`scan` for us and `EXTRACTED`/`ast` in the reference. Assert our own policy there
   and record the divergence.
6. The one documented miss: the `polygons.py` L29 `calls` edge.
