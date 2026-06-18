"""In-process structural self-grade checks (cheap, deterministic, keyless)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import sha256_of
from .models import CheckResult


def requirement_coverage(root: Path, cfg: dict[str, Any]) -> CheckResult:
    """Every mapped R-id must point at an artifact that exists on disk (R8.* coverage)."""
    artifacts: dict[str, str] = cfg["requirement_artifacts"]
    missing = [f"{rid}:{rel}" for rid, rel in artifacts.items() if not (root / rel).exists()]
    detail = (
        f"{len(artifacts)} R-ids mapped to existing artifacts"
        if not missing
        else f"missing: {', '.join(missing)}"
    )
    return CheckResult("requirement-coverage", not missing, detail)


def hot_md_consistent(root: Path, cfg: dict[str, Any]) -> CheckResult:
    """``obsidian/hot.md`` must exist and carry wikilinks (Phase-4 deliverable)."""
    rel = cfg.get("hot_md", "obsidian/hot.md")
    path = root / rel
    if not path.is_file():
        return CheckResult("hot.md-consistent", False, f"{rel} absent")
    has_links = "[[" in path.read_text(encoding="utf-8")
    detail = "exists with wikilinks" if has_links else "present but no wikilinks"
    return CheckResult("hot.md-consistent", has_links, detail)


def baselines_unmodified(root: Path, cfg: dict[str, Any]) -> CheckResult:
    """PRE-FIX baselines must match their recorded SHA-256 (CLAUDE.md §4 immutability)."""
    drift: list[str] = []
    for rel, expected in cfg["baseline_hashes"].items():
        path = root / rel
        actual = sha256_of(path) if path.is_file() else "<absent>"
        if actual != expected:
            drift.append(rel)
    detail = "all baseline hashes match" if not drift else f"drift: {', '.join(drift)}"
    return CheckResult("prefix-baselines-unmodified", not drift, detail)


def grade_documented(root: Path, grade: float) -> CheckResult:
    """The computed grade must be the same number documented in KNOWN_LIMITATIONS (R8.9)."""
    rel = "docs/KNOWN_LIMITATIONS.md"
    path = root / rel
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    needles = (f"{grade:g} / 100", f"{grade:g}/100")
    found = any(needle in text for needle in needles)
    detail = f"{needles[0]} present in KNOWN_LIMITATIONS" if found else f"{needles[0]} not found"
    return CheckResult("self-grade-documented", found, detail)
