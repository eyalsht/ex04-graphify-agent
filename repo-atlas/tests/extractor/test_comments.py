"""Marker-comment extraction (EXTRACTOR_SPEC §8).

This runs off the raw line stream, never the AST — comments are discarded by ``ast``,
and this path has to keep working on files that do not parse at all.
"""

from __future__ import annotations

from repo_atlas.extractor import comments

_BROKEN = 'print "python 2"\n# TODO: port this\n'


def _texts(source: str, **kwargs: object) -> list[str]:
    return [marker.text for marker in comments.find_markers(source, **kwargs)]  # type: ignore[arg-type]


def test_finds_a_todo_and_keeps_the_hash_while_stripping_indentation() -> None:
    found = comments.find_markers("def f():\n    # TODO: find a better way\n")
    assert [(m.text, m.lineno) for m in found] == [("# TODO: find a better way", 2)]


def test_recognises_every_marker_word() -> None:
    source = "# TODO: a\n# FIXME: b\n# XXX: c\n# HACK: d\n"
    assert len(comments.find_markers(source)) == 4


def test_ignores_a_comment_without_a_marker() -> None:
    assert comments.find_markers("# just a note about the code\n") == ()


def test_requires_a_word_boundary() -> None:
    """``TODOS`` and ``mastodon`` are not markers."""
    assert comments.find_markers("# TODOS are tracked elsewhere\n# mastodon\n") == ()


def test_ignores_a_trailing_inline_comment() -> None:
    """§8: whole-line comments only, so the graph does not fill with inline noise."""
    assert comments.find_markers("x = 1  # TODO: fix this\n") == ()


def test_strips_trailing_whitespace_from_the_text() -> None:
    assert _texts("# TODO: trailing   \n") == ["# TODO: trailing"]


def test_survives_a_file_that_does_not_parse() -> None:
    """The whole point of scanning lines instead of the AST."""
    assert _texts(_BROKEN) == ["# TODO: port this"]


def test_line_numbers_are_one_based() -> None:
    found = comments.find_markers("\n\n# FIXME: third line\n")
    assert found[0].lineno == 3


def test_respects_a_per_file_cap() -> None:
    """A repo with hundreds of TODOs must not drown its own graph."""
    source = "".join(f"# TODO: {index}\n" for index in range(10))
    assert len(comments.find_markers(source, limit=3)) == 3


def test_a_cap_of_zero_disables_marker_nodes() -> None:
    assert comments.find_markers("# TODO: x\n", limit=0) == ()


def test_does_not_match_a_marker_inside_a_string_literal_line() -> None:
    assert comments.find_markers('message = "TODO: not a comment"\n') == ()
