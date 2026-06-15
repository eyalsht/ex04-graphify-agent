# ADR-0001: Use LangGraph (not CrewAI) for the reverse-engineering agent

## Status
Accepted

## Context
R5.3.1 explicitly permits building the agent with **either CrewAI or LangGraph**, so the
framework choice is ours to make and justify. The choice is not cosmetic: it is
constrained by three downstream requirements.

First, R5.6.2 / R5.6.4 require us to **measure and report token usage per run** (graph-guided
vs. naive baseline) with concrete numbers — input/output tokens and call counts — backed
by stored artifacts (R10.5). To produce an apples-to-apples comparison report
(`PRD_token_comparison.md`, R7.8) we need to attribute every LLM call to a specific
workflow step, which means the agent's state and its per-node LLM invocations must be
inspectable rather than hidden inside a framework's orchestration loop.

Second, R6.1.4 requires that, if LangGraph is used, **state is managed explicitly (typed
state, not ad-hoc dicts)**. R5.3.3 / R5.5.1 require the workflow's nodes, tools, and stop
conditions to be defined and documented as inspectable stages (R5.5.2), and R5.4.2 / R7.3 /
R7.9 require a workflow diagram of that graph. The agent's pipeline is itself a graph:
Plan → Retrieve(graph) → Hypothesize → Validate(source) → Fix → Report (see
`PRD_agent_workflow.md`, §4 of the internal brief).

Third, this is a cost-sensitive exercise — the comparison needs at least two full runs on
real API keys (D6 — provider/model config-driven, decided later; likely Gemini, no pinned
default), so tight control over the number of LLM
calls directly affects budget and the credibility of the token numbers.

## Decision
Build the agent with **LangGraph**. The workflow is modelled as an explicit
`StateGraph` with a typed state schema (`agent_workflow/`, per §4 of the brief), where each
node is a discrete, named step (Plan, Retrieve, Hypothesize, Validate, Fix, Report). Every
LLM-provider API call flows through `gatekeeper.py` (ADR-0002), which tags each call's token
counts with `{run_type, node}` — the typed state makes that tagging unambiguous.

## Consequences
- **Enables R5.6 token instrumentation:** typed state + node-by-node control gives a clean
  seam to attribute tokens to each step, which is the data source for
  `token_comparison.py` and the R7.8 report.
- **Enables R5.4.2 / R7.3 workflow diagram:** the `StateGraph` topology maps directly to
  the required architecture/flow diagram — the diagram is the graph, not a hand-drawn
  approximation.
- **Conceptual fit:** the agent's own control flow is a graph, mirroring Graphify's
  knowledge-graph output — the navigation metaphor ("read the graph first") is reflected in
  the agent's own structure.
- **Constrains us** to satisfy R6.1.4 (typed state, no ad-hoc dicts) — enforced as a design
  rule in `PRD_agent_workflow.md`.
- **Implies work:** Phase 5 (agent workflow build) must define the state schema, the six
  nodes, and stop conditions; Phase 6-7 (token comparison + reports) consumes the
  per-node token logs. See `docs/TODO.md` Phase 5-7.

## Alternatives Considered
- **CrewAI** (allowed by R5.3.1) — *Rejected.* CrewAI's crew/agent/task abstraction
  orchestrates LLM calls internally, which makes per-call token instrumentation and
  deterministic, node-by-node state harder to expose cleanly for the R5.6 comparison. The
  crew abstraction also gives looser control over the exact number of LLM calls (and thus
  cost), which weakens the credibility of an apples-to-apples token report. Its strengths
  (multi-agent role play) are not needed for a single graph-guided debugging agent.
- **Raw provider-SDK loop, no framework** — *Rejected.* A hand-rolled loop would give
  maximum control over calls but provides no resumability, no typed state object, and no
  graph structure to render — making the R5.4.2 / R7.3 workflow diagram a manual artifact
  divorced from the code, and risking ad-hoc dict state that R6.1.4 warns against. The
  gatekeeper would still be needed; LangGraph adds the missing structure and
  documentability for little cost.
