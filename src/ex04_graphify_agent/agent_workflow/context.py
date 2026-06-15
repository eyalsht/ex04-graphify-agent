"""Context-assembly helpers — the heart of the context-minimization mechanism.

``read_vault_text`` builds the small graph-guided map (index.md + hot.md); ``dump_repo_text``
builds the deliberately larger naive context (every file under data/broken-python/**, sorted
for reproducibility — AW-E4). ``count_tokens`` is the provider-agnostic structural token proxy
used by the AW-T1 thesis assertion; ``make_diff`` renders the unified before/after diff. Each
reader returns the (text, files_read) pair so nodes can append to ``files_read`` (R5.6.5).
"""

from __future__ import annotations

import difflib
from pathlib import Path

_HOT_MISSING = "obsidian/hot.md not found ({path}) - run obsidian_writer first (generate_hot)"


def count_tokens(text: str) -> int:
    """Whitespace token proxy (provider-agnostic, deterministic, keyless)."""
    return len(text.split())


def read_vault_text(index_md: Path, hot_md: Path) -> tuple[str, list[str]]:
    """Read index.md + hot.md into the graph-guided map. Fail loud if hot.md is absent."""
    if not hot_md.is_file():
        raise FileNotFoundError(_HOT_MISSING.format(path=hot_md))
    index_text = index_md.read_text(encoding="utf-8")
    hot_text = hot_md.read_text(encoding="utf-8")
    text = f"{index_text}\n\n{hot_text}"
    return text, [str(index_md), str(hot_md)]


def dump_repo_text(repo_root: Path) -> tuple[str, list[str]]:
    """Concatenate every file under ``repo_root`` in sorted-path order (AW-E4)."""
    files = sorted(str(p) for p in repo_root.rglob("*") if p.is_file())
    chunks: list[str] = []
    for file in files:
        path = Path(file)
        rel = path.relative_to(repo_root).as_posix()
        chunks.append(f"# === {rel} ===\n{_read_text(path)}")
    return "\n\n".join(chunks), files


def make_diff(original: str, fixed: str, filename: str) -> str:
    """Unified diff of original vs fixed file contents."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        fixed.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    return "".join(diff)


def _read_text(path: Path) -> str:
    """Read text, tolerating non-UTF-8 bytes (e.g. LICENSE) without crashing."""
    return path.read_text(encoding="utf-8", errors="replace")
