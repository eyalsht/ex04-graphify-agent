"""``manifest.json`` — content-hash tracking for incremental re-runs (PRD R1.7).

A file's entry is ``{"mtime": float, "ast_hash": str}``. ``mtime`` is a cheap first
check a caller can use to skip re-reading a file whose modification time has not
moved; ``ast_hash`` is the authoritative signal this module actually compares on,
because ``mtime`` changes on a touch that leaves the content (and the AST) identical,
and a build tool that skipped re-extraction on hash equality alone would still be
correct after such a touch.

``ast_hash`` prefers structure over bytes: it hashes ``ast.dump`` of the parsed tree,
so whitespace-only edits do not look like a change. When a file does not parse — the
same degraded case ``docs/EXTRACTOR_SPEC.md`` §7 handles for node/edge extraction — it
falls back to hashing the raw text, so an unparseable file still gets a real content
signature instead of a crash or a placeholder.
"""

from __future__ import annotations

import ast
import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ManifestEntry = dict[str, Any]
Manifest = dict[str, ManifestEntry]


def ast_hash(source: str) -> str:
    """SHA-256 hex digest of the parsed AST, or of the raw text if it will not parse."""
    try:
        payload = ast.dump(ast.parse(source))
    except SyntaxError:
        payload = source
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_manifest(files: Mapping[str, Path]) -> Manifest:
    """Build a manifest from repo-relative path -> on-disk file path.

    Reads each file's modification time and text, and computes ``ast_hash`` for it.
    Callers own discovery (which files, under what ignore rules) — this only measures
    the files it is handed.
    """
    return {
        rel_path: {
            "mtime": abs_path.stat().st_mtime,
            "ast_hash": ast_hash(abs_path.read_text(encoding="utf-8")),
        }
        for rel_path, abs_path in files.items()
    }


def load_manifest(path: Path) -> Manifest:
    """Load a previously written manifest, or ``{}`` if it does not exist yet."""
    if not path.exists():
        return {}
    data: Manifest = json.loads(path.read_text(encoding="utf-8"))
    return data


def write_manifest(path: Path, data: Manifest) -> None:
    """Write ``data`` as UTF-8 JSON to ``path``, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = dict(sorted(data.items()))
    path.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class ManifestDiff:
    """Which repo-relative paths are new, gone, changed, or untouched since ``old``."""

    unchanged: set[str]
    changed: set[str]
    added: set[str]
    removed: set[str]


def diff_manifest(old: Manifest, new: Manifest) -> ManifestDiff:
    """Compare two manifests by ``ast_hash`` (not ``mtime`` — see module docstring)."""
    old_paths, new_paths = set(old), set(new)
    shared = old_paths & new_paths
    changed = {path for path in shared if old[path]["ast_hash"] != new[path]["ast_hash"]}
    return ManifestDiff(
        unchanged=shared - changed,
        changed=changed,
        added=new_paths - old_paths,
        removed=old_paths - new_paths,
    )
