"""Prompt templates (text only, no logic) for the LangGraph nodes.

System prompts are tiny and provider-agnostic; the user templates are filled by the nodes
with the assembled context. The graph-guided FIX template receives the small vault map plus
exactly one source file; the naive template receives the whole repo dump (the deliberately
larger "Lost in the Middle" baseline). Only ASCII punctuation is used (ruff RUF001/2/3).
"""

from __future__ import annotations

PLAN_SYSTEM = (
    "You are a graph-guided debugging agent. Plan a minimal route to localize and fix one "
    "bug in a small Python repo, preferring a knowledge-graph map over reading raw files."
)

HYPOTHESIZE_SYSTEM = (
    "You rank graph-weakness signals into a single primary bug hypothesis. State the "
    "confidence tag (EXTRACTED, INFERRED, or AMBIGUOUS) and do not treat an unvalidated "
    "INFERRED/AMBIGUOUS claim as fact."
)

FIX_SYSTEM = (
    "You are a senior Python engineer. Given a localized bug, return the corrected full "
    "contents of the single target file. Keep changes minimal and behaviour-correct."
)

FIX_USER_TEMPLATE = (
    "Graph map (where to look first):\n{context}\n\n"
    "Hypothesis:\n{hypothesis}\n\n"
    "Source file to fix ({filename}):\n{source}\n\n"
    "Return the corrected full file contents."
)

NAIVE_FIX_USER_TEMPLATE = (
    "Here is the entire repository. Find the bug and fix it.\n\n{dump}\n\n"
    "Begin your answer with a line `FILE: <relative path>` naming the file you fixed, then "
    "return that file's corrected full contents."
)
