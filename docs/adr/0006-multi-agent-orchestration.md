# ADR-0006: Realize the graph-guided route as a three-agent crew

## Status
Accepted (supersedes the "multi-agent role play … not needed" line in ADR-0001)

## Context
The L07 assignment (PDF §11.1.4 and the **ריבוי סוכנים / "multiple agents"** box) is explicit
that one agent is not enough: it asks, as the preferred design, for **several specialist agents,
each an expert in its domain** — naming three roles:

1. a **GitHub / clone agent** — download/update the target code, trigger Graphify;
2. a **graph-analysis agent** — read `graph.json`, find hubs/communities/architectural smells;
3. a **refactor agent** — propose and apply the fix.

The lecturer framed this multi-agent split as *the* signal that separates students who understood
the assignment from those who did not, and tied it to the agent-orchestration material from the
previous lesson. The course itself is **Orchestration of AI Agents**, so this is the conceptual
centre of gravity, not an optional flourish.

ADR-0001 chose **LangGraph over CrewAI** for clean per-node token instrumentation (needed by the
R5.6 token comparison) and, in doing so, asserted that "multi-agent role play is not needed for a
single graph-guided debugging agent." That reasoning was sound **for the framework choice** but
under-served the assignment's explicit multi-agent expectation: it optimized the token-comparison
axis at the cost of the orchestration axis, and only reconciled the former. This ADR closes that
gap **without** giving up the token-parity property ADR-0001 was protecting.

## Decision
Structure the **graph-guided** route as a **three-agent crew** — three compiled LangGraph
subgraphs over the shared typed `AgentState`, composed by an **orchestrator** graph
(`agent_workflow/agents.py` + `graph_def._wire_graph_guided`):

| Lecturer's role | Crew agent (subgraph) | Nodes it owns | Specialist module |
|---|---|---|---|
| GitHub / clone | **Navigator** | `plan` → `read_vault` | (loads + navigates the committed target + Graphify map) |
| graph-analysis | **Analyst** | `hypothesize` → `validate` (bounded retry loop) | `graph_reader`, `weakness_detector` |
| refactor | **Fixer** | `fix` | `agent_workflow.fix_target` |

The orchestrator wires `Navigator → Analyst → (Fixer | report)`: a deterministic post-Analyst
gate runs the Fixer agent only when the Analyst validated a finding, otherwise it skips straight
to an honest `report`. The bounded `validate → hypothesize` loop (`max_findings_tried`,
config-driven) lives **inside** the Analyst agent.

The **naive** baseline stays a single flat pipeline (`plan → dump_repo → fix → report`). Keeping
it monolithic is deliberate: the contrast *orchestrated specialist crew* vs *one undifferentiated
blob* is itself part of the "Lost in the Middle" story (ADR-0004).

### Two honest scoping decisions
- **"Navigator" (acquisition), not a live "GitHub agent".** We cannot clone from GitHub or run
  Graphify at agent runtime: the target repo is **vendored** under `data/broken-python/` and the
  Graphify artifacts (`artifacts/graphify/*`, the Obsidian vault) are **committed**, immutable
  PRE-FIX baselines (CLAUDE.md §4). The Navigator agent therefore *loads and navigates* that
  committed target and map rather than performing a network clone. We name it **Navigator** (not
  "GitHub agent") so the deliverable does not over-claim a capability it does not exercise (R10.1
  honesty) — and the name reinforces the project thesis: *navigate the map, don't dump the files*.
- **Deterministic supervisor.** The orchestrator's routing is rule-based, not an LLM "supervisor"
  call. This preserves token parity with the naive route (no crew-introduced LLM calls), keeps the
  R5.6 numbers an apples-to-apples measurement of *context strategy alone*, and keeps the routing
  deterministically testable (keyless, ADR-0005).

## Consequences
- **Token instrumentation unchanged.** Only `plan` and `fix` call the gatekeeper; both are the
  shared node objects (AW-T8), now owned by the Navigator and Fixer agents respectively. The
  crew adds **zero** LLM calls, so the committed keyless numbers (76.7% / 406 vs 1743 tokens,
  3 vs 8 files) hold unchanged. A later **keyed re-run through the crew** confirmed this on a
  live model: input tokens (1559 / 3670) and pass/fail correctness are **byte-for-byte
  identical** to the pre-crew run; only the model-nondeterministic output tokens/cost moved
  (cost gap 61.4% → 20.7%, `$0.0052` vs `$0.0066`). Evidence: `reports/crew_rerun_findings.md`.
- **Behaviour-preserving.** The flat node execution order is identical
  (`plan → read_vault → hypothesize → validate → fix → report`); `node_names("graph_guided")` is
  now *derived* from `agents.CREW` so the diagram and the code cannot drift. Every pre-existing
  end-to-end test (`test_run.py`) passes unchanged.
- **Inspectable crew.** Each agent is independently buildable and testable
  (`build_navigator_agent` / `build_analyst_agent` / `build_fixer_agent`,
  `tests/agent_workflow/test_agents.py`); `agents.CREW` is the single source of truth mapping each
  of the lecturer's three roles to its nodes.
- **Diagram is now nested.** The R5.4.2/R7.3 workflow diagram renders as an orchestrator over three
  agent subgraphs (README §4, `reports/diagrams.md`).
- **Constrains us** to keep the supervisor deterministic; introducing an LLM supervisor later would
  reopen the token-parity question and must be re-justified.

## Alternatives Considered
- **Keep the single flat StateGraph (status quo before this ADR).** *Rejected.* It satisfied the
  token thesis but left the assignment's headline multi-agent expectation only implicitly met and
  unreconciled — exactly the gap this ADR exists to close.
- **CrewAI for genuine role-play agents.** *Rejected*, per ADR-0001: CrewAI hides per-call token
  accounting inside its crew loop, which would compromise the R5.6 comparison's credibility. A
  LangGraph subgraph-per-agent gives the same three-specialist structure **and** keeps every LLM
  call attributable.
- **An LLM "supervisor" agent routing the crew.** *Rejected.* It would add LLM calls the naive
  baseline has no counterpart for, breaking the apples-to-apples token comparison, and make routing
  non-deterministic (harder to test keylessly) — for no localization benefit on a single-bug target.
