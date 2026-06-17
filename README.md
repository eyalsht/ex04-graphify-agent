<div align="center">

# 🧭 Graphify + Obsidian Reverse-Engineering Agent

### A graph-guided LangGraph agent that fixes a real bug by *navigating a knowledge graph* — not by dumping source into the prompt.

**EX04 · University of Haifa · Dr. Yoram Segal's Agentic-AI course (L07)**
Authors: **Eyal Shtinmtez** (314884834) · **Imree Cohen** (312359284)

<br/>

![Python](https://img.shields.io/badge/python-%E2%89%A53.11-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/packaging-uv%20only-DE5FE9?logo=astral)
![LangGraph](https://img.shields.io/badge/agent-LangGraph-1C3C3C)
![ruff](https://img.shields.io/badge/ruff-0%20violations-success?logo=ruff)
![mypy](https://img.shields.io/badge/mypy-strict%20·%200%20errors-2A6DB2)
![tests](https://img.shields.io/badge/tests-221%20passing-success?logo=pytest&logoColor=white)
![coverage](https://img.shields.io/badge/coverage-97%25%20(gate%20%E2%89%A590%25)-success)
![keyless](https://img.shields.io/badge/test%20suite-keyless%20(no%20API%20key)-blue)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

<br/>

<table>
<tr>
<td align="center"><b>76.7%</b><br/>fewer input-context tokens<sup>†</sup></td>
<td align="center"><b>1 file</b><br/>read vs <b>8</b> for the naive dump</td>
<td align="center"><b>5 → 1</b><br/>symptoms traced to one root cause</td>
<td align="center"><b>6/6</b><br/>PART-C signals converge on the bug</td>
</tr>
</table>

<sub><sup>†</sup> keyless, reproducible <i>input-context</i> measurement (the thesis's independent variable). The full keyed run (output tokens / call count / latency) is one documented, owner-run step — see <a href="#-6-token-efficiency-results-r86">§6</a>.</sub>

</div>

---

## TL;DR

`martinpeck/broken-python`'s [`polygons/polygons.py`](data/broken-python/polygons/polygons.py) is a half-finished script with five visible defects. We pointed a **Graphify** knowledge graph + an **Obsidian** vault (`index.md` / `hot.md`) at it, then built a **LangGraph** agent that reads *the graph's map* — "where do I look first?" — instead of stuffing every file into the model's context. The agent localizes one root cause, fixes it, and we **prove** it does so on **76.7% less input context** than a naive "dump every file" baseline — with zero loss of correctness (verified by an executable 3-part gate, not a claim).

Everything in this README is backed by a committed artifact, a requirement ID, or a command you can re-run keylessly.

```bash
git clone <repo> && cd HW4
uv sync
uv run pytest                 # 221 tests, keyless (provider client mocked)
uv run pytest -m eval         # the thesis evals: 76.7% token delta, structural validity
uv run ruff check . && uv run mypy --strict src/   # 0 / 0
uv run ex04 hot               # regenerate obsidian/hot.md from the PRE-FIX graph (keyless)
```

---

## 📋 Requirement coverage (PDF §8 → where it lives)

This README satisfies every §8 requirement **inline** (deep-dives link out to `reports/`):

| Req | Section | Req | Section |
|---|---|---|---|
| **R8.1** repo + bug + rationale | [§1](#-1-the-repo-the-bug-and-why-r81) | **R8.6** token-efficiency numbers | [§6](#-6-token-efficiency-results-r86) |
| **R8.2** setup & run | [§2](#-2-setup--run-r82) | **R8.7** OOP-improvement summary | [§7](#-7-oop-improvement-summary-r87) |
| **R8.3** Graphify + Obsidian usage | [§3](#-3-graphify--obsidian-the-navigation-layer-r83) | **R8.8** AI-usage disclosure | [§8](#-8-ai-usage-disclosure-r88) |
| **R8.4** agent workflow | [§4](#-4-the-agent-workflow-r84) | **R8.9** known limits + self-grade | [§9](#-9-known-limitations--honest-self-grade-r89) |
| **R8.5** root cause + before/after | [§5](#-5-root-cause--beforeafter-r85) | | |

---

## 🎯 1. The repo, the bug, and why (R8.1)

**Chosen repo:** [`martinpeck/broken-python`](https://github.com/martinpeck/broken-python) · **Chosen bug:** [`polygons/polygons.py`](data/broken-python/polygons/polygons.py) (76 lines). Full rationale in [ADR-0003](docs/adr/0003-target-repo-and-bug.md).

We were offered three approved repos and picked this one deliberately: its compact, single-file `polygons.py` exhibits **all six PART-C weakness signals in one place**, and a pre-existing Graphify run already pointed *unusually cleanly* at it. The alternatives were rejected for concrete reasons — `BugsInPy` needs heavy Docker setup and a large graph that would *bury* the "Lost in the Middle" demo in noise; `andela/buggy-python` has no Graphify baseline; and `broken-python`'s own `mathsquiz.py` is parse-broken across its whole body (a rewrite, not a *localizable root cause*).

**The bug, in one sentence:** the author started a `Polygon` class as the program's central abstraction and **abandoned it half-finished**, so every downstream computation re-implements, by hand, the state `Polygon` was meant to own. Five symptoms (a `NameError`, a `SyntaxError`, a wrong-answer branch, a dead class, a hardcoded drawing loop) — **one** root cause. See [§5](#-5-root-cause--beforeafter-r85).

---

## ⚙️ 2. Setup & run (R8.2)

**Toolchain:** `uv` only (no `pip`/`venv`), `ruff`, `mypy --strict`, `pytest` ≥90% coverage. **Keyless by default** ([ADR-0005](docs/adr/0005-keyless-by-default-test-strategy.md)): the entire suite and self-grade pass with **no API key** — the LLM provider client is mocked at the gatekeeper boundary.

```bash
uv sync                       # create env + install from uv.lock
uv run pytest --cov=src --cov-report=term-missing   # 221 passed, 97% coverage
uv run pytest -m eval         # structural + token-delta evals (the thesis, keyless)
uv run ruff check .           # 0 violations
uv run mypy --strict src/     # 0 errors
uv run ex04 hot               # (re)generate obsidian/hot.md from the PRE-FIX graph
```

<details>
<summary><b>The one keyed run (optional — needs a provider API key)</b></summary>

The full R5.6/R7.8 keyed numbers (output tokens, LLM-call counts, latency) come from a **single manual run** and are committed as static artifacts, so **grading never needs a key**. Provider/model are config-driven in [`config/agent.json`](config/agent.json) (currently `gemini-3.5-flash`); the key is read from `os.environ` only.

```bash
cp .env.example .env          # then edit: GEMINI_API_KEY=...   (.env is gitignored, auto-loaded)
uv run python scripts/run_comparison.py
```
This overwrites Layer 2 of [`reports/token_comparison.md`](reports/token_comparison.md) with a machine-rendered table sourced straight from the gatekeeper's JSONL ledger.
</details>

---

## 🗺️ 3. Graphify + Obsidian: the navigation layer (R8.3)

Instead of feeding the agent raw files, we give it a **map**. Graphify extracted a 23-node / 20-edge knowledge graph from `data/broken-python/` ([`artifacts/graphify/graph.json`](artifacts/graphify/graph.json), read-only PRE-FIX baseline), and we surface it as an **Obsidian vault** the agent reads:

- **[`obsidian/index.md`](obsidian/index.md)** — all 23 nodes + 6 communities.
- **[`obsidian/hot.md`](obsidian/hot.md)** — *"where to look first."* Generated (not hand-curated) from a disclosed metric: **centrality × proximity-to-bug** — a `0.6·degree + 0.4·betweenness` blend (max-normalized) × `1/(1 + graph-distance to the bug node)` (R5.1.4 / R5.6.1, config in [`config/weakness_thresholds.json`](config/weakness_thresholds.json)). The #1 entry is **`Polygon`** (degree 4 — the god node *at* the bug location); every top-8 entry lives in `polygons/polygons.py`.

<div align="center">
<table>
<tr>
<td align="center"><img src="reports/img/obsidian_graph_view.png" width="380"/><br/><sub><b>Fig. 3</b> — Obsidian graph view</sub></td>
<td align="center"><img src="reports/img/obsidian_hot.png" width="380"/><br/><sub><b>Fig. 5</b> — <code>hot.md</code>: ranked entry points</sub></td>
</tr>
</table>
</div>

> Open `obsidian/` as a vault to explore it live. More renders (the `Polygon` node, `index.md`) in [`reports/screenshots.md`](reports/screenshots.md).

**Inference discipline.** Every graph-derived claim is tagged **EXTRACTED / INFERRED / AMBIGUOUS**, and any `INFERRED`/`AMBIGUOUS` fact must pass a source-validation step (open the file, confirm) before the agent acts on it — the PART-C *Observe → Relation → Confidence → Context → Source-validation* trail.

---

## 🤖 4. The agent workflow (R8.4)

A single parameterized **LangGraph** with two routes sharing identical `plan/fix/report` nodes (so the gatekeeper's token instrumentation is *identical* and the comparison is fair). Node names below are the **actual compiled names** from [`agent_workflow/graph_def.py`](src/ex04_graphify_agent/agent_workflow/), verified against `build_graph`.

**Graph-guided route** — reads the *map*, validates against source, fixes:

```mermaid
stateDiagram-v2
    [*] --> plan
    plan --> read_vault: read index.md / hot.md (NOT a raw dump)
    read_vault --> hypothesize: graph_reader + vault context
    hypothesize --> validate: weakness_detector → 6-signal hypothesis
    validate --> fix: source confirms hypothesis
    validate --> hypothesize: source contradicts AND budget left
    validate --> report: budget exhausted
    fix --> report: write POST-FIX polygons.py + diff
    report --> [*]
```

**Naive baseline route** — the "Lost in the Middle" control (R1.4 / [ADR-0004](docs/adr/0004-graph-guided-retrieval-over-naive-dump.md)):

```mermaid
stateDiagram-v2
    [*] --> plan
    plan --> dump_repo: read ALL of data/broken-python/** into context
    dump_repo --> fix: LLM localizes + patches from the raw dump
    fix --> report
    report --> [*]
```

**SDK-first architecture:** all business logic lives behind [`sdk.py`](src/ex04_graphify_agent/sdk.py); [`cli.py`](src/ex04_graphify_agent/cli.py) is a thin wrapper with zero logic. Every external LLM call goes through a provider-agnostic **`gatekeeper`** (rate-limit, retry, queue, token counters, JSONL logging) — the provider can be swapped without touching anything else. Full C4 + pipeline diagrams in [`reports/diagrams.md`](reports/diagrams.md).

---

## 🔬 5. Root cause & before/after (R8.5)

> **One root cause:** `Polygon` was started as the central abstraction and abandoned half-finished, so every computation re-implements the state it should own. The author even left the confession in a comment: `# TODO: perhaps I should use the class Polygon instead!` (L33). **The graph found the same thing without reading the comments** — signals 1 (god node), 5 (isolated `rationale` TODO nodes), and 6 (the dict duplicates the class fields) all converge on `Polygon`. Full narrative: [`reports/root_cause.md`](reports/root_cause.md).

| # | Symptom | Type | Fix |
|---|---|---|---|
| 1 | `class Polygon(Object)` → `NameError` | blocking | `class Polygon(object)` |
| 2 | `poly = new Polygon(...)` → `SyntaxError` | blocking | `poly = Polygon(...)` |
| 3 | angle table returns `1000°/200°` for any non-tri/quad | latent | `(sides-2)·180`, `sum/sides` |
| 4 | a `dict` shadows the class (**the root cause**) | latent | return the `Polygon`; drop the dict |
| 5 | `draw_polygon` hardcodes a hexagon | latent | drive the loop from `polygon.sides` |

**This isn't asserted — it's gated.** `token_comparison.correctness.check_correctness` runs three independent properties against an *executed* copy of the fixed module: the angle formula (`5→540,108`; `6→720,120`), that `Polygon` is actually returned, and that `draw_polygon(pentagon)` issues exactly 5 turtle moves of `360/5`. PRE-FIX fails (`SyntaxError`); POST-FIX returns `True`. Literal diff: [`reports/diff_polygons.md`](reports/diff_polygons.md).

The fix even shows up in the graph — re-running Graphify on the fixed file (keylessly, AST-only) removes the three `rationale` TODO nodes and gives `Polygon` a new inbound `calls` edge ([`reports/graph_diff.md`](reports/graph_diff.md)):

<div align="center">
<table>
<tr>
<td align="center"><img src="reports/img/graph_pre_fix.png" width="380"/><br/><sub><b>Fig. 1</b> — PRE-FIX graph</sub></td>
<td align="center"><img src="reports/img/graph_post_fix.png" width="380"/><br/><sub><b>Fig. 2</b> — POST-FIX graph</sub></td>
</tr>
</table>
</div>

---

## 📉 6. Token-efficiency results (R8.6)

The thesis: graph-guided navigation costs **far less context** than dumping files, **without losing accuracy**. Measured two ways.

**Layer 1 — input context (keyless, reproducible, available now).** Both routes are billed the same way by the gatekeeper; the *only* variable is context strategy:

| Route | Input-context tokens | Files read | What entered context |
|---|---|---|---|
| **graph-guided** | **406** | **1** source (+ `index.md` + `hot.md`) | curated map + one validated file |
| **naive** | **1743** | **8** | all of `data/broken-python/**` |

> ### → **76.7% fewer input tokens** `(1743 − 406) / 1743` — comfortably clears the R4.1 ≥50% bar.

```bash
uv run pytest -m eval tests/evals/test_agent_context_delta.py   # asserts the ≥50% reduction
```

**Accuracy is not sacrificed (R4.2):** the graph-guided route reaches the same single root cause and its fix passes the 3-part correctness gate. The naive route gets the same facts *plus* noise.

> ⚠️ **Scope, stated honestly.** The 76.7% is the keyless *input-context* delta — the thesis's independent variable. The **full keyed table** (output tokens, # LLM calls, iterations, latency, end-to-end correctness from a live provider) is **one documented, owner-run step** (`scripts/run_comparison.py`, ADR-0005); it's the only remaining open item and is tracked in [`reports/token_comparison.md`](reports/token_comparison.md) §"Layer 2" and [§9](#-9-known-limitations--honest-self-grade-r89). Per CLAUDE.md §4, nothing here is an estimate — every number traces to a re-runnable command.

---

## 🧱 7. OOP-improvement summary (R8.7)

The graph said *"the most connected thing is a class that nothing uses, shadowed by a dict that everything uses."* The OOP-correct response isn't to delete the class — it's to **promote `Polygon` to the role it was designed for and retire the duplicate**. Full write-up: [`reports/oop_improvement.md`](reports/oop_improvement.md).

| Improvement | PRE-FIX | POST-FIX | Driving graph signal |
|---|---|---|---|
| **Single source of truth** | class + parallel dict | `Polygon` only | Signal 6 (semantic duplication) |
| **Encapsulated construction** | returns a dict | returns a `Polygon` | Signal 1 (god node *is* the abstraction) + `TODO@L33` |
| **Behavior near data** | hardcoded table; draw ignores `sides` | formula computes state; draw reads `polygon.sides` | Signal 5 (`rationale` nodes) |
| **Valid type hierarchy** | `Polygon(Object)` (`NameError`) | `Polygon(object)` | Signal 1 |
| **Invariant guard** | none | `ValueError` for `sides < 3` before any math | Signal 4 (critical-path break) |

One decision — *return `Polygon`, drop the dict* — turns five scattered symptoms into one coherent fix.

---

## 🧾 8. AI-usage disclosure (R8.8)

This project was built **with heavy AI assistance, disclosed in full** — the append-only log is [`docs/PROMPTS.md`](docs/PROMPTS.md) (R6.1.3). Summary:

- **Tooling:** Claude Code, with **Claude Opus 4.8** as orchestrator dispatching Opus/Sonnet **subagents** (each in its own git worktree) to build modules in parallel under strict TDD.
- **AI-generated:** all planning docs, the eight source modules, tests, the eight Phase-7 reports, and this README are **AI-drafted**.
- **Human-reviewed / directed:** the project owner ran **"Antigravity" code reviews** that caught real architectural shortcuts (e.g. the graph-guided route once **hardcoded** the fix target, faking the context-minimization thesis — torn out and replaced with a dynamic `source_file` resolver), chose the `hot.md` ranking (centrality × proximity over pure degree), made repo/bug decisions, and approved every PR + merge.
- **Honest TDD note:** some signal bodies and orchestrator-finished code were written tests-and-code-together rather than strict RED-first; this is disclosed in `PROMPTS.md` rather than overstated. Report prose is AI-drafted and merits a final human read-through (R10.1).

---

## ⚠️ 9. Known limitations & honest self-grade (R8.9)

Full, defensible list in [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md). The headline items:

- **Keyed token run is the one open deliverable.** Layer-1 (input-context, 76.7%) is committed and keyless; the keyed Layer-2 table awaits a single owner-run command. Not fabricated — deferred per ADR-0005.
- **Obsidian screenshots** were captured from a local scratch vault populated with copies of the committed notes (Figures 3–6).
- **POST-FIX graph** re-run split the READMEs into section nodes on the *document* side; the **code-graph** diff (the part that matters) is clean.
- **`turtle`** needs a GUI, so `draw_polygon` is verified by a mocked call-count assertion, not a rendered image.
- **Branch protection** can't be server-enforced on a free-tier private repo; mitigated by CI on every push/PR + local hooks.

**Self-grade:** computed at submission against the rubric, *after* the gates are green (they are: ruff 0, mypy 0, 221 tests @ 97%) — conservative and cross-referenced against the limitations above, never inflated. See [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md).

---

## 📚 Reports & evidence

Start at **[`reports/README.md`](reports/README.md)**. Each report ties every quantitative claim to a committed artifact or a re-runnable command:

| Report | Covers |
|---|---|
| [`root_cause.md`](reports/root_cause.md) | One root cause, 5 symptoms, how the graph localized it |
| [`diff_polygons.md`](reports/diff_polygons.md) | Literal before/after unified diff |
| [`oop_improvement.md`](reports/oop_improvement.md) | `Polygon` as single source of truth |
| [`graph_diff.md`](reports/graph_diff.md) | PRE vs POST graph structure |
| [`token_comparison.md`](reports/token_comparison.md) | 76.7% input-context reduction + pending keyed table |
| [`diagrams.md`](reports/diagrams.md) | C4 + both agent routes + pipeline (Mermaid) |
| [`pipeline.md`](reports/pipeline.md) | End-to-end pipeline, six-signal convergence |
| [`screenshots.md`](reports/screenshots.md) | Graph renders + Obsidian captures |

**Planning layer:** [`CLAUDE.md`](CLAUDE.md) (project constitution) · [`docs/PRD.md`](docs/PRD.md) · [`docs/PLAN.md`](docs/PLAN.md) · [`docs/ASSIGNMENT.md`](docs/ASSIGNMENT.md) (requirement IDs) · [`docs/adr/`](docs/adr/).

---

<div align="center">

**License:** MIT — see [`LICENSE`](LICENSE). · Built for EX04, University of Haifa.

</div>
