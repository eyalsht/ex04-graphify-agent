"""Fail if any ``[[id|Label]]`` wikilink in a generated vault is dangling.

Scans **every** ``*.md`` in the vault directory, not only the navigation entry points. The
origin project scanned just ``index.md``/``hot.md``, which is why its vault writer could emit
per-node notes linking to ``community-N.md`` files nothing ever wrote — a whole class of
dangling link the gate could not see. Exit 1 (and print offenders) on a dangling link, else 0.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")


def find_dangling_links(vault_dir: Path) -> list[tuple[str, str]]:
    """Return ``(filename, node_id)`` for every wikilink without a matching note file."""
    # Snapshot existing note stems once; O(1) membership beats a stat() per wikilink.
    notes = sorted(vault_dir.glob("*.md"))
    note_ids = {path.stem for path in notes}
    offenders: list[tuple[str, str]] = []
    for path in notes:
        for node_id in _WIKILINK.findall(path.read_text(encoding="utf-8")):
            if node_id not in note_ids:
                offenders.append((path.name, node_id))
    return offenders


def main(argv: list[str] | None = None) -> int:
    vault_dir = Path(argv[0]) if argv else Path.cwd() / "vault"
    if not vault_dir.is_dir():
        print(f"Vault consistency check skipped — no vault at {vault_dir}.")
        return 0
    offenders = find_dangling_links(vault_dir)
    if offenders:
        print(f"Vault consistency check FAILED — {len(offenders)} dangling link(s):")
        for filename, node_id in offenders:
            print(f"  {filename}: [[{node_id}]] -> missing {node_id}.md")
        return 1
    print(f"Vault consistency check passed — all wikilinks in {vault_dir} resolve.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
