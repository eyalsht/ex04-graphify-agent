"""Gate tests for ``scripts/check_vault_consistency.py``.

``test_dangling_link_in_a_node_note_is_caught`` is the regression the fork adds: the origin
gate scanned only ``index.md``/``hot.md``, so a per-node note linking to a ``community-N.md``
that nothing wrote passed clean.
"""

from __future__ import annotations

from pathlib import Path

import check_vault_consistency as gate


def _vault(tmp_path: Path, notes: dict[str, str]) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    for name, body in notes.items():
        (vault / name).write_text(body, encoding="utf-8")
    return vault


def test_resolving_links_pass(tmp_path: Path) -> None:
    vault = _vault(tmp_path, {"index.md": "[[mod_a|Module A]]\n", "mod_a.md": "# Module A\n"})
    assert gate.find_dangling_links(vault) == []


def test_dangling_link_in_index_is_caught(tmp_path: Path) -> None:
    vault = _vault(tmp_path, {"index.md": "[[missing]]\n"})
    assert gate.find_dangling_links(vault) == [("index.md", "missing")]


def test_dangling_link_in_a_node_note_is_caught(tmp_path: Path) -> None:
    vault = _vault(tmp_path, {"mod_a.md": "Community: [[community-3|Community 3]]\n"})
    assert gate.find_dangling_links(vault) == [("mod_a.md", "community-3")]


def test_aliased_links_resolve_on_the_id_not_the_label(tmp_path: Path) -> None:
    vault = _vault(tmp_path, {"hot.md": "[[mod_a|Anything At All]]\n", "mod_a.md": "x\n"})
    assert gate.find_dangling_links(vault) == []


def test_main_skips_a_missing_vault(tmp_path: Path) -> None:
    assert gate.main([str(tmp_path / "nope")]) == 0


def test_main_reports_exit_codes(tmp_path: Path) -> None:
    vault = _vault(tmp_path, {"index.md": "[[mod_a]]\n", "mod_a.md": "x\n"})
    assert gate.main([str(vault)]) == 0
    (vault / "index.md").write_text("[[gone]]\n", encoding="utf-8")
    assert gate.main([str(vault)]) == 1
