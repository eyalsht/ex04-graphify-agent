"""Fail if any ``[[id|Label]]`` wikilink in ``index.md``/``hot.md`` is dangling.

Phase 4 (CLAUDE.md §3 "obsidian/index.md and obsidian/hot.md must stay consistent with
graph.json"). Scans only ``index.md`` and ``hot.md`` (the navigation entry points) and
checks every ``[[id]]`` / ``[[id|Label]]`` wikilink resolves to an existing
``obsidian/<id>.md`` note. Exit 1 (and print offenders) on a dangling link, else 0.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
_SCANNED_FILES = ("index.md", "hot.md")


def find_dangling_links(vault_dir: Path) -> list[tuple[str, str]]:
    """Return ``(filename, node_id)`` for every wikilink without a matching note file."""
    # Snapshot existing note stems once; O(1) membership beats a stat() per wikilink.
    note_ids = {path.stem for path in vault_dir.glob("*.md")}
    offenders: list[tuple[str, str]] = []
    for filename in _SCANNED_FILES:
        path = vault_dir / filename
        if not path.is_file():
            continue
        for node_id in _WIKILINK.findall(path.read_text(encoding="utf-8")):
            if node_id not in note_ids:
                offenders.append((filename, node_id))
    return offenders


def main(argv: list[str] | None = None) -> int:
    vault_dir = Path(argv[0]) if argv else Path.cwd() / "obsidian"
    offenders = find_dangling_links(vault_dir)
    if offenders:
        print(f"Vault consistency check FAILED — {len(offenders)} dangling link(s):")
        for filename, node_id in offenders:
            print(f"  {filename}: [[{node_id}]] -> missing {node_id}.md")
        return 1
    print(f"Vault consistency check passed — {', '.join(_SCANNED_FILES)} wikilinks resolve.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
