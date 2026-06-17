# Live-Run Engineering Log — getting a real, passing keyed run (R4.2 / R8.8 / R10.4)

> An honest, blow-by-blow log of producing the **keyed** token/cost numbers in
> [`token_comparison.md`](token_comparison.md). It is kept deliberately, for two reasons:
> (1) honesty — the headline result took real debugging, not one clean shot; (2) it is the
> best *live* proof of the system's **modularity** — every model swap and retry tweak below
> was **one field in `config/agent.json`**; the gatekeeper, the LangGraph agent, and every
> caller stayed byte-for-byte unchanged.

## Timeline

| # | Model (config) | What happened | Root cause | Response |
|---|---|---|---|---|
| 1 | `gemini-3.5-flash` | Transient **503** on the `fix` node (retries exhausted); succeeded on a re-run, but **both routes failed correctness** | The model returned a `function_call` part; the SDK's `.text` accessor warned and dropped the patch text | Added `join_text_parts` + disabled automatic function-calling in `GeminiClient` (TDD) |
| 2 | `gemini-3.5-flash` | Re-ran with the text fix → **still both failed** | `fix_target.fixed_content` returned the **raw** LLM reply — including ```` ```python ```` fences / "Here is the fix:" prose — so the "fixed" file would not execute | Added `_strip_code_fence` to `fix_target` (TDD) |
| 3 | `gemini-3.1-pro` | **404 NOT_FOUND** | Wrong model id | Listed the account's models → correct id is `gemini-3.1-pro-preview` |
| 4 | `gemini-3.1-pro-preview` | **429 RESOURCE_EXHAUSTED**, `limit: 0` | Pro tier is **not available on the free key** (zero quota) | Abandoned the Pro path (would need paid billing) |
| 5 | `gemini-3.5-flash` | Repeated **503 "high demand"** storms; then **429 daily-quota** (free tier = 20 req/day per model — the 503-retries burned through it) | `gemini-3.5-flash` was both flaky and rate-capped for the day | Bumped gatekeeper retries (`3→6`, backoff `2→3 s`); still capped |
| 6 | **`gemini-2.5-flash`** | ✅ **Completed.** graph-guided **PASS**, naive **FAIL** | Stable GA model, separate per-model quota, no 503s | **Kept as the configured model** |

## The result (run #6 — first keyed pass, pre-crew monolithic agent)

| Run | Input tok | Output tok | # calls | Cost (USD) | Correctness |
|---|---|---|---|---|---|
| **graph_guided** | 1559 | 1020 | 2 | **$0.0030** | ✅ **pass** |
| naive | 3670 | 2684 | 2 | $0.0078 | ❌ fail |

**57.5% fewer input tokens · 61.4% lower total cost · and graph-guided reached the correct
fix while the full-repo dump did not** — the "Lost in the Middle" prediction (ADR-0004),
realized on a live model: the curated `hot.md` + one validated file let `gemini-2.5-flash`
fix the bug; the 8-file dump derailed it.

## Confirmation run (post-crew — the current committed ledgers)

After the graph-guided route was rebuilt as the three-agent crew (Navigator / Analyst /
Fixer, ADR-0006), the comparison was re-run keyed on the same model. This is the run whose
ledgers are now committed under [`../artifacts/runs/`](../artifacts/runs/), and it is the
source of the [`token_comparison.md`](token_comparison.md) numbers:

| Run | Input tok | Output tok | # calls | Cost (USD) | Correctness |
|---|---|---|---|---|---|
| **graph_guided** | 1559 | 1891 | 2 | **$0.0052** | ✅ **pass** |
| naive | 3670 | 2180 | 2 | $0.0066 | ❌ fail |

The **input tokens (1559 / 3670) and the pass/fail correctness are identical** to run #6 —
the crew adds no LLM calls, so the deterministic 57.5% input cut and the "Lost in the
Middle" result reproduce exactly. The **output tokens and cost moved** (cost gap 61.4% →
20.7%) because output length is model-nondeterministic even at `temperature=0`, and total
cost is output-bound (output priced 8.3× input). One keyed run is one sample; the input cut
is the load-bearing number. Full before/after analysis:
[`crew_rerun_findings.md`](crew_rerun_findings.md).

## Why this is a modularity proof, not just a war story

- **Three model swaps + one retry re-tune = six edits, all in `config/agent.json`.** No
  change to `gatekeeper/`, `agent_workflow/`, `token_comparison/`, or `sdk.py`. The provider
  is hidden behind the `LLMClient` protocol (ADR-0002), so the model id, pricing, and retry
  policy are pure configuration (D6 / CLAUDE.md §3).
- **The two code fixes landed exactly where provider quirks belong** — the `GeminiClient`
  adapter (the *only* module that imports the SDK) absorbed the `function_call` behaviour,
  and the agent's output seam (`fix_target`) absorbed the markdown-fence formatting. Neither
  fix touched routing, state, or the comparison logic. Both are covered by keyless unit tests
  (`tests/gatekeeper/test_provider.py`, `tests/agent_workflow/test_fix_target.py`).
- **Cost followed the model for free.** Because `pricing` is config-driven too, swapping
  `gemini-3.5-flash` ($1.50/$9.00) → `gemini-2.5-flash` ($0.30/$2.50) re-priced the report
  with no code change; cost is always `logged tokens x configured rate`.

## Reproduce

The keyless evidence needs no key: `uv run pytest -m eval` (the 76.7% input-context delta).
The keyed run above is one manual command (ADR-0005), and re-pricing/model selection is a
config edit only:

```bash
# config/agent.json: set "model" + matching "pricing"; key in .env (gitignored)
uv run python scripts/run_comparison.py   # rewrites token_comparison.md + artifacts/runs/*.jsonl
```
