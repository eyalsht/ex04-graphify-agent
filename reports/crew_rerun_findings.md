# Three-Agent Crew Re-Run — Findings

**Date:** 2026-06-17 · **Model:** `gemini-2.5-flash` (config-driven) · **Run by:** `uv run python scripts/run_comparison.py`

This note records a fresh keyed run of the token comparison **after** the graph-guided
route was rebuilt as the **three-agent crew** (Navigator → Analyst → Fixer subgraphs,
`cebcade` / PR #10, ADR-0006). The previously committed numbers in
[`token_comparison.md`](token_comparison.md) came from commit `0139ba5` (Phase 7) — i.e. the
**pre-crew monolithic** graph-guided agent. This is the first keyed run executed *through the
crew*, so it tells us whether the new orchestration changed the thesis. It is a decision
input only — README/other docs are **not** updated until we agree on the numbers.

## What I ran

| Check | Command | Result |
|---|---|---|
| Keyless eval (thesis) | `uv run pytest -m eval` | **4 passed** (76.7% input-context delta + known-answer localization) |
| Full keyless suite | `uv run pytest` | **244 passed, 98% coverage** (matches README badges) |
| Keyed live comparison | `uv run python scripts/run_comparison.py` | both routes ran on `gemini-2.5-flash`; rewrote the report + ledgers |

## Headline: the thesis is unchanged; the cost *gap* moved

| Metric | Pre-crew (committed) | Crew re-run (this run) | Change |
|---|---|---|---|
| **graph-guided input tok** | 1559 | **1559** | **identical** |
| **naive input tok** | 3670 | **3670** | **identical** |
| **Input-token reduction (R4.1)** | 57.5% | **57.5%** | **identical** |
| **Correctness — graph-guided** | ✅ pass | ✅ **pass** | **unchanged** |
| **Correctness — naive** | ❌ fail | ❌ **fail** | **unchanged** |
| graph-guided output tok | 1020 | 1891 | +85% (model-nondeterministic) |
| naive output tok | 2684 | 2180 | −19% (model-nondeterministic) |
| graph-guided cost (USD) | $0.0030 | $0.0052 | higher |
| naive cost (USD) | $0.0078 | $0.0066 | lower |
| **Total cost reduction** | **61.4%** | **20.7%** | **shrank** |
| graph-guided duration (s) | 29.11 | 29.67 | ~same |
| naive duration (s) | 35.64 | 34.09 | ~same |

## What the differences mean

1. **The core thesis survived the crew, deterministically.** Input-context tokens are a
   function of *what enters context* (the curated map + one validated file vs. the 8-file
   dump), not of model sampling — so they are **byte-for-byte identical** to the pre-crew
   run: 1559 vs 3670, a **57.5%** input reduction. This is exactly what ADR-0006 / README §4
   predicted: the crew is three subgraphs over the *same* shared `plan`/`fix` node objects, so
   it **adds no LLM calls of its own** (still 2 billed calls per route). The crew is a cleaner
   orchestration of the *same* context strategy, not a different one.

2. **Graph-guided still fixes the bug; naive still fails.** The "Lost in the Middle"
   result (R4.2) held on a second, independent live run — the most important outcome. The
   crew did not regress correctness.

3. **The cost *delta* dropped from 61.4% → 20.7% — and that is expected noise, not a
   regression.** Total cost is dominated by *output* tokens (priced 8.3× input:
   $2.50 vs $0.30 / 1M). Output length is **model-nondeterministic** even at
   `temperature=0` (Gemini does not guarantee deterministic decoding). This run, graph-guided
   happened to emit a longer report (1891 vs 1020) and naive a shorter one (2180 vs 2684), so
   the two costs converged. One keyed run is **one sample**; the cost-gap figure is the
   noisiest number we report and should be framed as such.

4. **Traceability gap found *and root-caused*.** The *old* committed ledgers
   (`artifacts/runs/*.jsonl`) recorded `output_tokens: 2` — a mock/keyless artifact that did
   **not** match the old report's 1020/2684 output figures (a latent CLAUDE.md §4
   traceability gap). The cause: a **keyless test** (`test_compare_tokens_writes_report`)
   called `compare_tokens(report_path=tmp)` but the ledger dump fell through to the *default*
   `artifacts/runs/`, so **every `uv run pytest` overwrote the tracked keyed ledgers with mock
   stubs**. Fixed by threading a `runs_dir` through `Ex04Sdk.compare_tokens` and pointing the
   test at its `tmp_path` (the manual keyed run still defaults to `artifacts/runs/`). After the
   fix, the real keyed ledgers **survive a full `pytest` run** and **reconcile exactly** with
   the report: graph-guided `41+1518 = 1559` in / `1415+476 = 1891` out; naive
   `39+3631 = 3670` in / `1182+998 = 2180` out. Every number in the rewritten report now
   traces to a stored gatekeeper log entry — permanently.

## Working-tree changes from this run (uncommitted)

The run rewrote three files; nothing is committed yet (per your "decide after seeing the
results"):

- `reports/token_comparison.md` — new output/cost numbers (input + correctness unchanged)
- `artifacts/runs/graph_guided.jsonl` — real keyed ledger (was a mock stub)
- `artifacts/runs/naive.jsonl` — real keyed ledger (was a mock stub)

The pre-crew values are preserved in git history (`0139ba5`) and were backed up before the run.

## Recommendation — accepted by the owner and applied (branch `docs/crew-rerun-evidence`)

The owner reviewed these findings and chose to keep the re-run and refresh the docs. The keyed
cost figures were updated across README §6, `token_comparison.md`, `run_journey.md`,
`reports/README.md`, `KNOWN_LIMITATIONS.md`, and ADR-0006; the rationale below is retained as
the decision record.


- **Keep the new run.** It is the first keyed run that genuinely exercises the crew, and it
  *strengthens* the submission: the deterministic thesis (57.5% input cut, graph-guided
  passes / naive fails) is reproduced, and the ledgers↔report traceability gap is closed.
- **Lead with the input-context numbers, not cost.** README §6 already does this; we should
  keep cost as the secondary, explicitly-noisy figure. If we commit this run, update the
  README §6 cost line **20.7%** (from 61.4%) and the `<table>` cost badge **~21%** (from
  61.4%), and add one sentence that the cost gap is output-token-bound and varies run-to-run.
- **The 76.7% keyless headline and the 57.5% keyed input figure both stand** — no change.
- Consider a short note in [`run_journey.md`](run_journey.md) recording this as the
  post-crew confirmation run.
