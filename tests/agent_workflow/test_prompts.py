"""TDD for prompt templates — text only, no logic (PHASE5-094..095)."""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow import prompts


def test_system_prompts_are_non_empty_text() -> None:
    assert isinstance(prompts.PLAN_SYSTEM, str) and prompts.PLAN_SYSTEM
    assert isinstance(prompts.HYPOTHESIZE_SYSTEM, str) and prompts.HYPOTHESIZE_SYSTEM
    assert isinstance(prompts.FIX_SYSTEM, str) and prompts.FIX_SYSTEM


def test_fix_user_template_has_placeholders() -> None:
    template = prompts.FIX_USER_TEMPLATE
    assert "{context}" in template
    assert "{source}" in template
    assert "{hypothesis}" in template


def test_naive_fix_user_template_has_dump_placeholder() -> None:
    assert "{dump}" in prompts.NAIVE_FIX_USER_TEMPLATE


def test_templates_contain_no_ambiguous_unicode() -> None:
    # Guard against RUF001/002/003 ambiguous chars sneaking into prompt text.
    banned = (chr(0x00D7), chr(0x00B7))  # MULTIPLICATION SIGN, MIDDLE DOT
    for value in vars(prompts).values():
        if isinstance(value, str):
            assert all(ch not in value for ch in banned)
