# Requirement Traceability Matrix (R1.1 → R10.5)

Every binding requirement in [`docs/ASSIGNMENT.md`](../docs/ASSIGNMENT.md) traced to ≥1
concrete, committed artifact (R8.9 / PHASE8-059). "Where" links to the file/section that
satisfies it; nothing is left unmapped.

## §1 Overview · §2 Repos · §3 Objectives
| Req | Where |
|---|---|
| R1.1 title | [`README.md`](../README.md) hero block |
| R1.2 Graphify→graph, Obsidian nav | [README §3](../README.md#-3-graphify--obsidian-the-navigation-layer-r83) · [`artifacts/graphify/`](../artifacts/graphify/) · [`obsidian/`](../obsidian/) |
| R1.3 graph-guided agent | [README §4](../README.md#-4-the-agent-workflow-r84) · [`src/.../agent_workflow/`](../src/ex04_graphify_agent/agent_workflow/) |
| R1.4 "Lost in the Middle" thesis | [README §6](../README.md#-6-token-efficiency--cost-results-r86) · [`token_comparison.md`](token_comparison.md) · [ADR-0004](../docs/adr/0004-graph-guided-retrieval-over-naive-dump.md) |
| R1.5 third-party reproducible | [README §2](../README.md#-2-setup--run-r82) · [`scripts/run_comparison.py`](../scripts/run_comparison.py) |
| R2.1 approved repo chosen | [ADR-0003](../docs/adr/0003-target-repo-and-bug.md) · [`data/broken-python/`](../data/broken-python/) |
| R2.2 README documents choice+why | [README §1](../README.md#-1-the-repo-the-bug-and-why-r81) · ADR-0003 |
| R3.1 graph-based RE | [README §3](../README.md#-3-graphify--obsidian-the-navigation-layer-r83) · [`graph_reader/`](../src/ex04_graphify_agent/graph_reader/) |
| R3.2 curated (not dumped) context | [README §4](../README.md#-4-the-agent-workflow-r84) · `agent_workflow/nodes.py` |
| R3.3 measurable token efficiency | [`token_comparison.md`](token_comparison.md) |
| R3.4 OOP improvements | [`oop_improvement.md`](oop_improvement.md) |
| R3.5 durable Graphify/Obsidian artifacts | [`artifacts/graphify/`](../artifacts/graphify/) · [`obsidian/`](../obsidian/) |

## §4 Research Questions
| Req | Where |
|---|---|
| R4.1 token reduction + by how much | [README §6](../README.md#-6-token-efficiency--cost-results-r86) (76.7% keyless) · [`tests/evals/test_agent_context_delta.py`](../tests/evals/) |
| R4.2 accuracy cost | [README §6](../README.md#-6-token-efficiency--cost-results-r86) · correctness gate `token_comparison/correctness.py` |
| R4.3 god nodes reveal coupling | [`root_cause.md`](root_cause.md) · `weakness_detector/signals_graph.py` (signal 1) |
| R4.4 OOP suggested + applied | [`oop_improvement.md`](oop_improvement.md) |
| R4.5 root cause via graph | [`root_cause.md`](root_cause.md) · [`pipeline.md`](pipeline.md) |
| R4.6 Obsidian concretely helped | [`screenshots.md`](screenshots.md) · [`reports/img/`](img/) |
| R4.7 AI-usage disclosure | [`docs/PROMPTS.md`](../docs/PROMPTS.md) · [README §8](../README.md#-8-ai-usage-disclosure-r88) |

## §5 Core Tasks
| Req | Where |
|---|---|
| R5.1.1 graph.json + report | [`artifacts/graphify/graph.json`](../artifacts/graphify/graph.json) · [`GRAPH_REPORT.md`](../artifacts/graphify/GRAPH_REPORT.md) |
| R5.1.2 per-node notes + wikilinks | [`obsidian/*.md`](../obsidian/) · `obsidian_writer/notes.py` |
| R5.1.3 index.md hub | [`obsidian/index.md`](../obsidian/index.md) · `obsidian_writer/index.py` |
| R5.1.4 hot.md prioritized map | [`obsidian/hot.md`](../obsidian/hot.md) · `obsidian_writer/hot.py` |
| R5.2.1 graph-first understanding | [README §3](../README.md#-3-graphify--obsidian-the-navigation-layer-r83) |
| R5.2.2 fix real bug + root cause | [`root_cause.md`](root_cause.md) · [`polygons.py`](../data/broken-python/polygons/polygons.py) |
| R5.2.3 OOP improvements | [`oop_improvement.md`](oop_improvement.md) |
| R5.2.4 before/after diff + narrative | [`diff_polygons.md`](diff_polygons.md) |
| R5.3.1 LangGraph agent | [ADR-0001](../docs/adr/0001-langgraph-over-crewai.md) · `agent_workflow/graph_def.py` |
| R5.3.2 consumes graph outputs | `agent_workflow/nodes.py` (`read_vault`) |
| R5.3.3 documented workflow | [README §4](../README.md#-4-the-agent-workflow-r84) · [`diagrams.md`](diagrams.md) |
| R5.4.1 Obsidian screenshots | [`screenshots.md`](screenshots.md) |
| R5.4.2 agent workflow diagram | [`diagrams.md`](diagrams.md) · [README §4](../README.md#-4-the-agent-workflow-r84) |
| R5.5.1 full pipeline defined | [`pipeline.md`](pipeline.md) |
| R5.5.2 inspectable stage artifacts | [`artifacts/`](../artifacts/) · [`obsidian/`](../obsidian/) · [`reports/`](.) |
| R5.5.3 root cause found via graph | [`pipeline.md`](pipeline.md) · [`root_cause.md`](root_cause.md) |
| R5.6.1 hot.md from a graph metric | `obsidian_writer/ranking.py` · [`config/weakness_thresholds.json`](../config/weakness_thresholds.json) |
| R5.6.2 token usage both runs | [`token_comparison.md`](token_comparison.md) · [`artifacts/runs/`](../artifacts/runs/) |
| R5.6.3 graph.json diff before/after | [`graph_diff.md`](graph_diff.md) · [`artifacts/graphify_post_fix/`](../artifacts/graphify_post_fix/) |
| R5.6.4 concrete numbers | [`token_comparison.md`](token_comparison.md) |
| R5.6.5 files_read + iterations columns | [`token_comparison.md`](token_comparison.md) (mandated columns) |

## §6 Planning & Efficiency
| Req | Where |
|---|---|
| R6.1.1 plan before Graphify | [`docs/PLAN.md`](../docs/PLAN.md) · [`docs/PRD.md`](../docs/PRD.md) |
| R6.1.2 Obsidian as real nav aid | [`screenshots.md`](screenshots.md) |
| R6.1.3 disclose AI usage | [`docs/PROMPTS.md`](../docs/PROMPTS.md) |
| R6.1.4 typed LangGraph state | `agent_workflow/state.py` |
| R6.1.5 justify model choice | [README §6](../README.md#-6-token-efficiency--cost-results-r86) · [`config/agent.json`](../config/agent.json) · [`run_journey.md`](run_journey.md) |
| R6.1.6 Docker/venv (N/A) | [ADR-0003](../docs/adr/0003-target-repo-and-bug.md) (broken-python needs none) |
| R6.2.1 not LLM-only | `agent_workflow/nodes.py` (`read_vault` graph backbone) |
| R6.2.2 explainable tools | [README §4](../README.md#-4-the-agent-workflow-r84) |
| R6.2.3 BugsInPy raw (N/A) | [ADR-0003](../docs/adr/0003-target-repo-and-bug.md) |
| R6.2.4 before/after evidence | [`diff_polygons.md`](diff_polygons.md) |
| R6.2.5 README has §8 sections | [README requirement-coverage map](../README.md#-requirement-coverage-pdf-8--where-it-lives) |
| R6.2.6 Obsidian screenshots | [`screenshots.md`](screenshots.md) |

## §7 Deliverables · §8 README · §9 Structure · §10 Expectations
| Req | Where |
|---|---|
| R7.1 public GitHub repo | repo public at `github.com/eyalsht/ex04-graphify-agent` (R7.1) |
| R7.2 Python source | [`src/`](../src/ex04_graphify_agent/) |
| R7.3 runnable agent workflow | [`agent_workflow/`](../src/ex04_graphify_agent/agent_workflow/) · `cli.py` |
| R7.4 Graphify outputs pre+post | [`artifacts/graphify/`](../artifacts/graphify/) · [`artifacts/graphify_post_fix/`](../artifacts/graphify_post_fix/) |
| R7.5 wikilinked vault | [`obsidian/`](../obsidian/) |
| R7.6 before/after diff + root cause | [`diff_polygons.md`](diff_polygons.md) · [`root_cause.md`](root_cause.md) |
| R7.7 OOP-improvement summary | [`oop_improvement.md`](oop_improvement.md) |
| R7.8 baseline-vs-graph comparison | [`token_comparison.md`](token_comparison.md) |
| R7.9 vault + workflow screenshots/diagrams | [`screenshots.md`](screenshots.md) · [`diagrams.md`](diagrams.md) |
| R8.1 repo+bug+rationale | [README §1](../README.md#-1-the-repo-the-bug-and-why-r81) |
| R8.2 setup & run | [README §2](../README.md#-2-setup--run-r82) |
| R8.3 Graphify+Obsidian usage | [README §3](../README.md#-3-graphify--obsidian-the-navigation-layer-r83) |
| R8.4 agent workflow | [README §4](../README.md#-4-the-agent-workflow-r84) |
| R8.5 root cause + before/after | [README §5](../README.md#-5-root-cause--beforeafter-r85) |
| R8.6 token-efficiency results | [README §6](../README.md#-6-token-efficiency--cost-results-r86) |
| R8.7 OOP-improvement summary | [README §7](../README.md#-7-oop-improvement-summary-r87) |
| R8.8 AI-usage disclosure | [README §8](../README.md#-8-ai-usage-disclosure-r88) |
| R8.9 known limits + self-grade | [README §9](../README.md#-9-known-limitations--honest-self-grade-r89) · [`KNOWN_LIMITATIONS.md`](../docs/KNOWN_LIMITATIONS.md) · `scripts/self_grade.py` |
| R9.1 repo structure | repo layout · [`docs/PLAN.md`](../docs/PLAN.md) §Module Structure |
| R10.1 clarity / reproducible | [README §2](../README.md#-2-setup--run-r82) |
| R10.2 OOP quality | [`oop_improvement.md`](oop_improvement.md) |
| R10.3 vault genuinely useful | [`screenshots.md`](screenshots.md) · [`obsidian/hot.md`](../obsidian/hot.md) |
| R10.4 explainable claims | [`docs/PROMPTS.md`](../docs/PROMPTS.md) · [`run_journey.md`](run_journey.md) |
| R10.5 evidence-based claims | [`artifacts/runs/`](../artifacts/runs/) · all of [`reports/`](.) |

**Coverage: 51/51 requirement IDs mapped** — no requirement is unsupported.
