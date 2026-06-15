# Phase 0 Verification Pass — Coverage & Gap Report

> Generated at the end of the planning session (2026-06-14). Confirms every PRD
> requirement maps to ≥1 TODO task, every PLAN module has a per-mechanism PRD, and every
> open assignment decision has an ADR. Mechanical checks were run with `grep` over the
> docs (see commands inline).

## 1. Requirement → TODO coverage (ASSIGNMENT.md R#.# → docs/TODO.md)

- **ASSIGNMENT leaf requirements:** all of R1.1–R1.5, R2.1–R2.2, R3.1–R3.5, R4.1–R4.7,
  R5.1.1–R5.6.4, R6.1.1–R6.2.6, R7.1–R7.9, R8.1–R8.9, R9.1, R10.1–R10.5 are referenced by
  ≥1 task in `docs/TODO.md`. **No leaf requirement is uncovered.**
- The only ASSIGNMENT IDs *not* literally appearing in TODO are the bare section headers
  **R5.1, R5.2, R5.3, R5.5** (and R5.4/R5.6 appear only incidentally). These are parent
  headers whose every child (R5.1.1–4, R5.2.1–4, R5.3.1–3, R5.5.1–3) IS covered — so
  coverage is complete at the actionable (leaf) level. **Not a gap.**

## 2. PRD test-case → TODO coverage

Every Given/When/Then test-case ID defined in the per-mechanism PRDs maps to ≥1 TODO task
(RED+GREEN). Mechanical check (`grep -oE '<PREFIX>[0-9]+'`):

| PRD | Test-case IDs | In TODO? |
|---|---|---|
| `PRD_graph_reader.md` (graph_reader) | GR-T1 … GR-T7 | ✅ all 7 |
| `PRD_graph_reader.md` (obsidian_writer) | OW-T1 … OW-T5 | ✅ all 5 |
| `PRD_weakness_detector.md` | WD-T1 … WD-T8 | ✅ all 8 |
| `PRD_agent_workflow.md` | AW-T1 … AW-T8 | ✅ all 8 |
| `PRD_token_comparison.md` | TC-T1 … TC-T8 | ✅ all 8 |

**36/36 test cases covered. No gap.**

## 3. PLAN module → per-mechanism PRD coverage

| Module (brief §4 / PLAN.md) | Primary PRD | Covered? |
|---|---|---|
| `graph_reader.py` | `PRD_graph_reader.md` | ✅ |
| `obsidian_writer.py` | `PRD_graph_reader.md` (folded in, by design) | ✅ |
| `weakness_detector.py` | `PRD_weakness_detector.md` | ✅ |
| `agent_workflow/` | `PRD_agent_workflow.md` | ✅ |
| `gatekeeper.py` | ADR-0002 + `PRD_token_comparison.md` + `PRD_agent_workflow.md` | ✅ |
| `token_comparison.py` | `PRD_token_comparison.md` | ✅ |
| `sdk.py` | `PLAN.md` only (façade — no separate PRD, by design per brief §7) | ✅ (intentional) |
| `cli.py` | `PLAN.md` only (thin CLI — no logic, by design) | ✅ (intentional) |

**All 8 modules covered.** `sdk.py`/`cli.py` intentionally have no standalone PRD (they
hold no business logic per the SDK-first rule); this is documented, not a gap.

## 4. Locked decision → ADR coverage

| Decision (brief §1) | ADR | Present? |
|---|---|---|
| D1 LangGraph over CrewAI | `0001-langgraph-over-crewai.md` | ✅ |
| D2 Gatekeeper present | `0002-gatekeeper-present-or-omitted.md` | ✅ |
| D3 Target repo + bug | `0003-target-repo-and-bug.md` | ✅ |
| D4 Graph-guided over naive dump | `0004-graph-guided-retrieval-over-naive-dump.md` | ✅ |
| D5 Keyless-by-default tests | `0005-keyless-by-default-test-strategy.md` | ✅ |
| D6 LLM provider/model config-driven, decided later (no default; NOT Haiku; likely Gemini) | CLAUDE.md + `config/agent.json` (not a standalone ADR) | ✅ (intentional) |
| D7 uv-only / pyproject | CLAUDE.md + ASSIGNMENT.md §9 note | ✅ (intentional) |

**All 5 architecturally-significant decisions have ADRs.** D6/D7 are recorded in
CLAUDE.md/config rather than standalone ADRs (the kickoff specified exactly 5 ADR files);
documented, not a gap.

## 5. Cross-doc consistency (mechanical)

- **POST-FIX graph directory name:** `artifacts/graphify_post_fix/` used uniformly (18
  occurrences; 0 competing spellings). ✅
- **Module names:** all 8 canonical names (`graph_reader`, `weakness_detector`,
  `obsidian_writer`, `agent_workflow`, `gatekeeper`, `token_comparison`, `sdk`, `cli`)
  used consistently across PLAN/PRD/CLAUDE. ✅
- **Package name:** `ex04_graphify_agent` (import name) / `ex04-graphify-agent`
  (`[project] name`) — the standard underscore-vs-hyphen pairing, consistent. ✅
- **Graph facts:** 23 nodes / 20 edges / 6 communities / 90% EXTRACTED-10% INFERRED-0%
  AMBIGUOUS / `Polygon` degree 4 / 2 INFERRED edges (0.8, 0.9) — used identically in
  PRD.md, PLAN.md, ADR-0003, PRD_graph_reader.md, PRD_weakness_detector.md. ✅
- **Falsifiable graph-diff prediction:** "nodes 23 → 20, the three `rationale_*` nodes
  disappear after the fix" — stated consistently in PRD_token_comparison.md and TODO
  (PHASE6-048, PHASE6-080, TC-T7). ✅

## 6. Task count

`docs/TODO.md` = **751 atomic tasks** (within the required 500–1000 band):

| Phase | Tasks |
|---|---|
| 0 Planning | 32 |
| 1 Scaffold | 86 |
| 2 graph_reader (TDD) | 121 |
| 3 weakness_detector (TDD) | 118 |
| 4 Obsidian vault | 41 |
| 5 LangGraph agent (TDD) + structural evals | 145 |
| 6 token comparison + evidence | 90 |
| 7 reports | 47 |
| 8 README + self-grade | 71 |
| **Total** | **751** |

## 7. Open items carried forward (NOT planning gaps — owner/execution actions)

These are tracked in `docs/TODO.md` Phase 0 and `docs/KNOWN_LIMITATIONS.md`; they require
the **owner**, not more planning:

1. **`pyproject.toml` authors** — real student IDs for Eyal Shtinmetz + Imri (full
   name/email/ID) are placeholders (PHASE0-015). Blocks the first commit.
2. **ASSIGNMENT.md PDF spot-check** — the Hebrew body text could not be machine-extracted
   (custom font encoding); ASSIGNMENT.md was reconstructed from embedded English terms +
   the owner's kickoff digest and needs a manual spot-check against the original PDF
   (PHASE0-016). *Highest-confidence risk in the planning layer.*
3. **Graphify CLI availability** — needed for the POST-FIX graph re-run (PHASE0-017 /
   R5.6.3); unverified.
4. **Obsidian install** — needed for the screenshot deliverables (PHASE0-018 / R5.4.1,
   R7.9).
5. **Provider API key** (config-driven, likely `GEMINI_API_KEY`) — needed once, for the manual real-run that produces the actual
   token-comparison numbers (PHASE0-019 / ADR-0005).
6. **Original `broken-python/` clone** — pristine copy with its own `.git` sits beside the
   vendored `data/broken-python/`; `.gitignore` or remove before submission (PHASE0-027).
7. **`docs/_internal_context_brief.md`** — a session-internal coordination file; delete
   before submission (PHASE0-031).

## 8. Judgment calls flagged by subagents (for owner awareness)

- **PLAN.md:** modules projected into directories (e.g. `agent_workflow/`,
  `graph_reader/`) to respect the ≤150-line file rule, while keeping brief §4's exact
  module names as package names. If single-file modules were intended, several would
  exceed 150 lines.
- **PRD_weakness_detector.md:** Signal 6 (semantic duplicate) tagged AMBIGUOUS pre-source
  -read, upgraded after — because no backing graph edge exists; it requires a source-read
  even to hypothesize (a noted edge case). `god_node_min_degree` default = 4 (makes
  `Polygon` the sole trigger on the current graph).
- **PRD_agent_workflow.md:** one parameterized LangGraph (`run_type` in state) chosen over
  two named graphs; `max_validation_attempts` default = 1.
- **PRD_token_comparison.md:** the 23→20 graph-diff prediction assumes the fix *deletes*
  the TODO comments. If the fix leaves resolved-TODO comments in place, the rationale
  nodes may persist and the count prediction would change — the most assumption-heavy
  claim; worth confirming at Phase 6.

## 9. Review-driven tightenings (post first review, applied)

Four issues raised in review (by a reader who read the original PDF) were applied:

1. **R5.6.5 added — mandated comparison columns.** The PDF §5.6 requires the report to
   show, as first-class columns, not just tokens: **`files_read`** (files/textual units
   read) and **`iterations`** (investigation rounds), plus quality+speed to root cause.
   Added `R5.6.5` to ASSIGNMENT.md; propagated to `PRD_token_comparison.md` (the
   `RunMetrics` dataclass now has `files_read`/`iterations`/`files_read_list`; the report
   table gained `Files read` + `Iterations` + `Duration` columns; new test cases TC-T9/
   TC-T10), to `PRD_agent_workflow.md` (`AgentState.files_read`, with `iterations` sourced
   from `findings_tried`), and to TODO (PHASE6-073/073d).
2. **Naive-baseline modeling stated as deliberate in ADR-0004.** Added a paragraph making
   explicit that modeling the naive run as a single dump→fix pass (no validation loop) is a
   faithful operationalization of the PDF's framing, not an under-built baseline — both
   runs share the identical task, full code view, and correctness check.
3. **Standalone CI gate scripts added (agent-debate parity).** TODO now creates
   `scripts/check_file_sizes.py`, `scripts/check_no_hardcoded.py`,
   `scripts/check_anti_patterns.py` as committed, TDD'd, CI-wired scripts (PHASE1-018…018f),
   wired into `.pre-commit-config.yaml` (PHASE1-019) and `ci.yml` by name (PHASE1-071), and
   reused by `self_grade` (PHASE8-034/038/039) — matching the standard the project claims to
   follow.
4. **Thesis promoted to `tests/evals/` + committed run transcripts (the agent-debate
   signature).** The AW-T1 context-delta is no longer a buried unit test: a keyless
   structural-eval suite (`tests/evals/`, `pass^k=100%`, run via `-m eval`) was added
   (PHASE1-058a/b, PHASE5-E01…E09) covering the token-delta thesis, the known-answer
   weakness detection (signals 1 & 5), hot.md ranking, graph-schema, fixed-polygons
   correctness, and report well-formedness; the one real keyed run's full transcripts are
   committed under `docs/evidence/` (PHASE6-073a/b/c).

## Verdict

**No blocking planning-layer gaps.** Every requirement (incl. the new R5.6.5), test case,
module, and decision is covered. All remaining items are owner/execution actions already
tracked in TODO Phase 0 + KNOWN_LIMITATIONS. The plan layer is ready for review and (on
approval) Phase 1 scaffold.
