# ADR-0002 — Comprehension is the product; the bug-fix loop is dropped

- **Status:** Accepted
- **Date:** 2026-09-14

## Context

The origin project's pipeline ended in a repair: detect a weakness, hypothesise a bug, validate it
against source, rewrite the file, and prove the fix with an oracle. Three of its layers existed only
to serve that ending, and all three were welded to one target:

- `weakness_detector/` — six "signals", of which signal 4 performed no analysis at all (it checked
  that two literal node ids existed and emitted a canned sentence) and signal 6 hardcoded a node-id
  pair plus `self.X =` / `"key":` regexes.
- `token_comparison/correctness.py` — an oracle asserting three specific known fixes.
- `token_comparison/graph_diff.py` — a before/after graph diff pinned to one node id.

A generic bug-finder is a different and much harder product than a generic repo explainer, and the
success criterion ("is the fix correct?") has no repo-agnostic answer short of running the target's
own test suite.

## Decision

Scope this fork to comprehension. `atlas` explains a repository; it never modifies one.

The bug-fix loop, the weakness detector, the correctness oracle and the graph diff are not carried
over. The LangGraph flow is replaced by a linear
`load_graph -> select_context -> summarize -> write_brief` pipeline, and `AgentState` loses its
scalar `current_hypothesis` / `target_file` / `fix_diff` fields.

## Consequences

**Good.** Everything that remains is repo-agnostic by construction. The output is judged on whether
a reader understands the repo afterwards, not on a pass/fail oracle that cannot generalise. The
LangGraph flow becomes simple enough to reason about and cheap enough to run per-section.

**Cost.** The origin project's headline result — "graph-guided retrieval found and fixed the bug
using ~77% fewer input tokens" — is not reproducible here, because there is no fix. The token
comparison keeps the input-token reduction but replaces the `correctness` column with a **coverage**
measure (what fraction of hot nodes and modules the brief actually cites), so that "cheaper" cannot
be won by saying less.

**Reopening.** If repair is wanted later it returns as a separate consumer of this library, with the
target repo's own test suite as its oracle — not as a hardcoded checker.
