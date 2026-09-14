"""Walk a repo and yield the files eligible for extraction (PRD R1.3).

Eligibility, cheapest check first so a file is skipped before an expensive step ever runs on
it: suffix is ``.py`` (kind ``"python"``) or in ``config.document_extensions`` (kind
``"document"``); its basename does not match ``config.exclude_globs``; the repo-root
``.gitignore`` (:mod:`repo_atlas.extractor.gitignore`) does not match it; a symlink resolves
inside ``repo_root``; ``Path.stat`` (never a read) puts it at or under ``max_file_bytes``;
and a single in-memory decode (:func:`_is_utf8_text`) proves it is valid UTF-8. A directory
named in ``config.exclude_dirs``, or gitignore-matched, is pruned at any depth before it is
ever descended into. The result is a sorted tuple of :class:`DiscoveredFile`, so two runs
over an unchanged tree always agree and nothing downstream has to sort it again.

Scope decisions, each covered by a test asserting the documented behaviour rather than left
implicit (``tests/extractor/test_discovery.py``, ``test_discovery_symlinks.py``):

- **A symlinked directory is never traversed**, even one whose target lies inside
  ``repo_root`` (free from ``os.walk(..., followlinks=False)``) — a strictly safer superset
  of the PRD's "don't follow an *escaping* symlink", at the cost of not indexing anything
  reached only through one.
- **A symlinked file** is included only when its resolved target lies inside ``repo_root``;
  its ``abs_path`` is then that resolved target, so a later ``open()`` never leaves the tree.
- **``exclude_globs`` matches the basename**, not the repo-relative path — consistent with
  the shipped config's own patterns (``"*.lock"``, ``"*.min.js"``).
- **Extension matching is case-insensitive** (``.PY`` counts as ``"python"``).
"""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path

from repo_atlas.extractor.gitignore import GitIgnore
from repo_atlas.paths import ExtractorConfig

_KIND_PYTHON = "python"
_KIND_DOCUMENT = "document"


@dataclass(frozen=True)
class DiscoveredFile:
    """One file selected for extraction."""

    rel_path: str  # repo-relative, POSIX, no leading "/"
    abs_path: Path  # absolute; a symlink's *resolved* target, never the link itself
    kind: str  # "python" | "document"


def discover_files(repo_root: Path, config: ExtractorConfig) -> tuple[DiscoveredFile, ...]:
    """Walk ``repo_root`` and return the eligible files, sorted by ``rel_path``."""
    repo_root = repo_root.resolve()
    ignore = GitIgnore.load(repo_root)
    exclude_dirs = set(config.exclude_dirs)
    found: list[DiscoveredFile] = []

    for dirpath, dirnames, filenames in os.walk(repo_root, followlinks=False):
        current = Path(dirpath)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in exclude_dirs
            and not ignore.matches(_rel(current / name, repo_root), is_dir=True)
        ]
        for name in filenames:
            discovered = _consider(current / name, repo_root, config, ignore)
            if discovered is not None:
                found.append(discovered)

    return tuple(sorted(found, key=lambda f: f.rel_path))


def _consider(
    path: Path, repo_root: Path, config: ExtractorConfig, ignore: GitIgnore
) -> DiscoveredFile | None:
    kind = _classify(path, config)
    if kind is None:
        return None
    if any(fnmatch.fnmatch(path.name, pattern) for pattern in config.exclude_globs):
        return None
    rel_path = _rel(path, repo_root)
    if ignore.matches(rel_path, is_dir=False):
        return None
    abs_path = _resolve_within_root(path, repo_root)
    if abs_path is None:
        return None
    try:
        size = abs_path.stat().st_size
    except OSError:
        return None
    if size > config.max_file_bytes:
        return None
    if not _is_utf8_text(abs_path):
        return None
    return DiscoveredFile(rel_path=rel_path, abs_path=abs_path, kind=kind)


def _classify(path: Path, config: ExtractorConfig) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return _KIND_PYTHON
    if suffix in {ext.lower() for ext in config.document_extensions}:
        return _KIND_DOCUMENT
    return None


def _rel(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _resolve_within_root(path: Path, repo_root: Path) -> Path | None:
    """The real path for ``path``, or ``None`` if a symlink escapes ``repo_root``."""
    if not path.is_symlink():
        return path
    resolved = path.resolve()
    if resolved == repo_root or repo_root in resolved.parents:
        return resolved
    return None


def _is_utf8_text(path: Path) -> bool:
    """Read ``path`` once and attempt a strict UTF-8 decode; never read it a second time."""
    try:
        path.read_bytes().decode("utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    return True


def read_discovered_text(discovered: DiscoveredFile) -> str:
    """Read a discovered file's text (reused by the naive-dump baseline, PHASE4-012).

    Decode-error policy: ``discover_files`` already proved ``abs_path`` decodes as strict
    UTF-8, so a strict decode here is expected to always succeed on the same bytes. If the
    file changed on disk between discovery and this call (a TOCTOU race) and a strict decode
    now fails, this falls back to ``errors="replace"`` rather than raising — a single
    corrupted file should never abort a caller reading many of them. Any other I/O error
    (the file having been deleted, say) is not caught and propagates as ``OSError``.
    """
    try:
        return discovered.abs_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return discovered.abs_path.read_text(encoding="utf-8", errors="replace")
