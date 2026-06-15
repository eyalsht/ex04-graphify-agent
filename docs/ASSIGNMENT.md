# EX04 Assignment — Binding Requirements

> **Source:** `lec/ex04-gaphify-obcidian-Reverse-engineering.pdf` (10 pages, Hebrew, v1.0, June 2026),
> cross-checked against `lec/L07-Lesson-Summary.pdf` and the project kickoff brief.
>
> **Extraction note:** The PDF embeds Hebrew body text using a custom font encoding that
> `pypdf`/standard text extractors cannot decode (output is replacement glyphs). All
> **English/technical terms embed cleanly** (LangGraph, CrewAI, BugsInPy, martinpeck/broken-python,
> andela/buggy-python, OOP, "Lost in the Middle", index.md, hot.md, graph.json, GRAPH_REPORT.md,
> Docker, GitHub, README, root cause, before/after). This document reconstructs the binding
> requirements from (a) those extracted terms and the page/section skeleton, and (b) the
> project owner's own kickoff brief, which already digests this PDF section-by-section.
> **TODO(owner): spot-check each numbered item below against the original PDF** (e.g. with
> Adobe/Hebrew-capable PDF reader) and correct any misreading — flag corrections as ADR
> amendments if they change scope.

---

## 1. Assignment Overview (PDF §1)

- **R1.1** — Title: "Reverse Engineering, Debugging and Token-Efficient Agentic AI with
  Graphify and Obsidian" (EX04, Lesson L07, June 2026, v1.0).
- **R1.2** — Take an unfamiliar, intentionally-broken Python repository. Use **Graphify**
  to reverse-engineer it into a knowledge graph, and **Obsidian** as the human/agent
  navigation layer over that graph.
- **R1.3** — Build an **AI agent** (CrewAI or LangGraph) that operates **graph-guided**:
  it reads `index.md` / `hot.md` first — not raw source files — to locate, explain, and
  fix a bug.
- **R1.4** — Core thesis to demonstrate: graph-guided navigation avoids the **"Lost in the
  Middle"** problem of dumping an entire unfamiliar codebase into an LLM context window;
  `index.md` + `hot.md` act as a compressed, prioritized map that reduces token usage
  while preserving (or improving) bug-localization accuracy.
- **R1.5** — The chosen repo, the chosen bug, and the agent's workflow must all be
  reproducible by a third party from the repo + README alone.

## 2. Base Repositories (PDF §2)

- **R2.1** — Approved source repos (pick one):
  - `soarsmu/BugsInPy` — curated dataset of real, reproducible Python bugs (heavier setup,
    Docker/virtualenv recommended).
  - `martinpeck/broken-python` — small, intentionally broken/incomplete Python scripts
    designed for debugging practice. **← CHOSEN (see ADR-0003).**
  - `andela/buggy-python` — alternative small buggy-Python practice repo.
- **R2.2** — The README **must document which repo was chosen and why**.

## 3. Objectives (PDF §3)

- **R3.1** — Practice structured reverse engineering of an unfamiliar codebase using a
  knowledge-graph representation rather than ad-hoc file reading.
- **R3.2** — Practice AI-agent-assisted debugging where the agent's context is curated
  (graph-guided) rather than dumped.
- **R3.3** — Produce measurable evidence of token efficiency gains from graph-guided vs.
  naive (dump-all-files) context.
- **R3.4** — Apply OOP improvements to the fixed code as part of the reverse-engineering
  exercise (not just a one-line patch).
- **R3.5** — Use Graphify + Obsidian as durable artifacts/deliverables, not throwaway
  exploration tools.

## 4. Research Questions (PDF §4)

The submission must explicitly answer (in the README/report), with evidence:

- **R4.1** — Does graph-guided agent navigation reduce token consumption vs. a naive
  "dump the whole repo into context" baseline, and by how much?
- **R4.2** — Does that reduction come at a cost to (or improve) bug-localization accuracy
  / correctness of the fix?
- **R4.3** — What do **God Nodes** (high-degree / high-centrality nodes) in the generated
  graph reveal about the codebase's core abstractions and coupling risk?
- **R4.4** — What OOP improvements does the graph-guided view suggest, and were they
  applied?
- **R4.5** — How did the graph help identify the **root cause** of the bug (not just a
  symptom)?
- **R4.6** — How did Obsidian (as a navigable vault) concretely help the agent / the
  student during the exercise — with screenshots/diagrams as evidence?
- **R4.7** — How was AI used throughout (disclosure), and where did the agent's workflow
  diverge from a human's?

## 5. Core Tasks (PDF §5)

### 5.1 — Run Graphify and generate the Obsidian vault (PDF §5.1)
- **R5.1.1** — Run Graphify against the chosen repo to produce `graph.json` and
  `GRAPH_REPORT.md` (or `.json`).
- **R5.1.2** — Generate an Obsidian vault from the graph: one Markdown note per
  node/concept/file/function, with wikilink (`[[...]]`) cross-references.
- **R5.1.3** — `index.md` — a navigation hub: communities, all nodes, entry points.
- **R5.1.4** — `hot.md` — a prioritized "where to look first" map (high centrality /
  high proximity to the bug / recently changed), distinct from the full `index.md`.

### 5.2 — Reverse-engineer and improve the code (PDF §5.2)
- **R5.2.1** — Use the graph (not blind file reading) to understand the unfamiliar
  codebase's structure before touching code.
- **R5.2.2** — Identify and fix at least one real bug, with a documented **root cause**
  (not just a symptom-level patch).
- **R5.2.3** — Apply OOP improvements (encapsulation, removing duplication, correct class
  design, etc.) as part of the fix — informed by what the graph revealed (e.g. unused
  classes, duplicate logic, god objects).
- **R5.2.4** — Document the change as a clear **before/after** (diff + narrative).

### 5.3 — Build the AI agent (PDF §5.3)
- **R5.3.1** — Build the agent with **CrewAI or LangGraph** (see ADR-0001).
- **R5.3.2** — The agent's workflow must consume the Graphify/Obsidian outputs
  (`index.md`/`hot.md`/`graph.json`) as its primary context — graph-guided, not raw-dump.
- **R5.3.3** — Define and document the agent's workflow (nodes/steps, tools, stop
  conditions).

### 5.4 — Documentation & communication artifacts (PDF §5.4)
- **R5.4.1** — Produce screenshots/diagrams of the Obsidian graph view and/or vault
  navigation as evidence the vault is real and usable.
- **R5.4.2** — Document the agent's workflow diagrammatically (architecture/flow
  diagram).

### 5.5 — End-to-end workflow definition (PDF §5.5)
- **R5.5.1** — Define the full pipeline workflow explicitly: repo → Graphify → `graph.json`
  / `GRAPH_REPORT.md` → Obsidian vault (`index.md`, `hot.md`, per-node notes) → agent
  → fix.
- **R5.5.2** — Each stage's input/output must be inspectable artifacts (not hidden
  intermediate state).
- **R5.5.3** — The workflow must show how the root cause was found via the graph.

### 5.6 — Token efficiency measurement (PDF §5.6)
- **R5.6.1** — `hot.md` must be derived using a graph metric (centrality and/or
  proximity to the bug location) — not arbitrary.
- **R5.6.2** — Measure and report token usage for: (a) the graph-guided agent run, and
  (b) a naive baseline run (dump-all-files / no graph).
- **R5.6.3** — Track `graph.json` changes (e.g. via diff) before/after the fix as
  evidence of the refactor's structural impact.
- **R5.6.4** — Report findings with concrete numbers (input/output tokens, call counts),
  not just qualitative claims.
- **R5.6.5** — The comparison report must include, **at minimum, as first-class columns**
  (per PDF §5.6, confirmed against the original): **(a) number of tokens**, **(b) number of
  files / textual units read**, **(c) number of iterations / investigation rounds**, and
  **(d) the quality and speed of reaching the root cause**. Items (b) `files_read` and (c)
  `iterations` are **mandated, not optional** — they must appear explicitly in the report
  table, not merely be implied by token counts.

## 6. Planning & Efficiency (PDF §6)

### 6.1 — Do's (PDF §6.1)
- **R6.1.1** — Plan before running Graphify; understand what `graph.json` / `index.md` /
  `hot.md` will be used for.
- **R6.1.2** — Use Obsidian as a real navigation aid (open it, link it, screenshot it) —
  not just generate it and ignore it.
- **R6.1.3** — Disclose AI usage throughout (this PRD/PLAN/TODO process counts).
- **R6.1.4** — If using LangGraph, manage state explicitly (typed state, not ad-hoc
  dicts) — see PRD_agent_workflow.md.
- **R6.1.5** — Justify the LLM/model choice (cost, capability, determinism for grading).
- **R6.1.6** — If using BugsInPy, use Docker/virtualenv for reproducibility (N/A for this
  project — see ADR-0003, broken-python needs no special env).

### 6.2 — Don'ts (PDF §6.2)
- **R6.2.1** — Don't run an LLM-only workflow without Graphify — the graph must be the
  navigation backbone.
- **R6.2.2** — Don't use agent workflows/tools you can't explain.
- **R6.2.3** — Don't use BugsInPy raw without environment setup (N/A here).
- **R6.2.4** — Don't skip before/after documentation — every claimed fix needs evidence.
- **R6.2.5** — Don't ship a README missing required sections (§8).
- **R6.2.6** — Don't skip Obsidian screenshots/diagrams.

## 7. Deliverables (PDF §7)

- **R7.1** — Public GitHub repository.
- **R7.2** — Python source code (this project's agent/graph-reading tooling — NOT a
  modified copy of Graphify itself).
- **R7.3** — The AI agent workflow implementation (LangGraph — ADR-0001), runnable.
- **R7.4** — Graphify outputs: `graph.json`, `GRAPH_REPORT.md` (pre- and post-fix).
- **R7.5** — Obsidian vault: `index.md`, `hot.md`, per-node Markdown notes, all
  wikilinked.
- **R7.6** — Before/after code diff with documented root cause.
- **R7.7** — OOP-improvement summary.
- **R7.8** — Baseline-vs-graph-guided comparison report with token-usage evidence.
- **R7.9** — Screenshots/diagrams of the Obsidian vault and agent workflow.

## 8. README Requirements (PDF §8)

The top-level `README.md` must include, at minimum:

- **R8.1** — Chosen repo + chosen bug + rationale for the choice.
- **R8.2** — How to set up and run the project (uv-based, keyless-by-default — see
  ADR-0005).
- **R8.3** — How Graphify + Obsidian were used (with links/screenshots into `obsidian/`).
- **R8.4** — The agent workflow (LangGraph graph diagram or description).
- **R8.5** — Root cause narrative + before/after diff (or link to it).
- **R8.6** — Token-efficiency results (numbers: naive vs. graph-guided).
- **R8.7** — OOP-improvement summary.
- **R8.8** — AI-usage disclosure (what was AI-generated vs. human-reviewed/written, per
  `docs/PROMPTS.md`).
- **R8.9** — Known limitations (`docs/KNOWN_LIMITATIONS.md`) and honest self-grade.

## 9. Recommended Repository Structure (PDF §9)

```
README.md
requirements.txt   (or pyproject.toml — this project uses uv/pyproject.toml, see ADR
                     and PLAN.md for the uv-only rationale)
pyproject.toml
/src
/tests
/obsidian
/reports
/artifacts
/data
```

- **R9.1** — This project follows this structure (mapped concretely in `docs/PLAN.md`
  §"Module Structure"), with `uv`/`pyproject.toml` replacing `requirements.txt` per the
  course's [TIGHTENED] CLAUDE.md conventions (documented as an intentional, disclosed
  deviation — not a violation, since `pyproject.toml` is explicitly listed as acceptable
  in §9).

## 10. Expectations (PDF §10)

- **R10.1** — Clarity: a third party should be able to follow the README and reproduce
  the result.
- **R10.2** — OOP quality: the fixed code should demonstrate good OOP, not just "make it
  run".
- **R10.3** — The Obsidian vault must be **genuinely useful** as a navigation aid — not a
  generated-and-ignored artifact.
- **R10.4** — AI is a collaborator/tool, not a replacement for understanding — the
  student must be able to explain every claim (root cause, token numbers, OOP choices).
- **R10.5** — Evidence-based claims throughout: every quantitative claim (token counts,
  graph metrics) must be backed by a stored artifact (graph diff, run log, report).

---

## Cross-reference index

| Requirement family | Primary PRD/PLAN coverage |
|---|---|
| R1.x, R3.x, R4.x (overview/objectives/research Qs) | `docs/PRD.md` |
| R2.x, R6.x (repo choice, planning discipline) | `docs/adr/0003-*.md`, `docs/PRD.md` |
| R5.1 (Graphify/Obsidian vault) | `docs/PRD_graph_reader.md`, `obsidian/` |
| R5.2 (reverse-engineer + fix + OOP) | `docs/PRD_weakness_detector.md`, `docs/adr/0003-*.md` |
| R5.3, R5.4, R5.5 (agent workflow) | `docs/PRD_agent_workflow.md`, `docs/adr/0001-*.md` |
| R5.6, R7.8 (token efficiency) | `docs/PRD_token_comparison.md`, `docs/adr/0004-*.md` |
| R7.x (deliverables) | `docs/PLAN.md` §"Data flow", `docs/TODO.md` Phase 6-8 |
| R8.x (README) | `docs/TODO.md` Phase 8 |
| R9.x, R10.x (structure/expectations) | `CLAUDE.md`, `docs/PLAN.md` |
