"""A minimal, from-scratch ``.gitignore`` matcher (PRD R1.3) — no third-party dependency.

Only the repo-root ``.gitignore`` is read; nested ``.gitignore`` files are out of scope (see
:mod:`repo_atlas.extractor.discovery` for how this is combined with the exclude-dirs config).

Supported syntax: blank lines and ``#`` comments (skipped), a trailing ``/`` marking a
directory-only rule, a leading (or any interior) ``/`` anchoring a pattern to the repo root
instead of matching at any depth, ``*``/``?``/``[seq]`` wildcards (delegated to
:mod:`fnmatch`), and ``!`` negation with last-match-wins precedence — the same precedence
git itself uses.

Out of scope, deliberately, and each covered by a test asserting the actual behaviour rather
than left to guesswork (``tests/extractor/test_gitignore.py``):

- ``**`` has no special recursive meaning. It is matched the same as a single ``*``, which
  already crosses path separators here because :func:`fnmatch.fnmatch` matches whole
  strings, not path segments.
- Backslash-escaping (of a leading ``#``/``!``, or of trailing whitespace) is not supported.
- Git's rule that a negated pattern cannot resurrect a file whose ancestor directory was
  itself excluded by a different pattern is moot in practice: this module only answers
  "does this one path match", and :mod:`repo_atlas.extractor.discovery` prunes an ignored
  directory before ever visiting anything beneath it, so that case cannot arise.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path

_GITIGNORE_NAME = ".gitignore"


@dataclass(frozen=True)
class _Rule:
    pattern: str
    negate: bool
    dir_only: bool
    anchored: bool


class GitIgnore:
    """Rules parsed from one repo-root ``.gitignore``; empty when there is none."""

    def __init__(self, rules: tuple[_Rule, ...]) -> None:
        self._rules = rules

    @classmethod
    def load(cls, repo_root: Path) -> GitIgnore:
        """Parse ``<repo_root>/.gitignore``. An absent file yields a no-op matcher."""
        gitignore_path = repo_root / _GITIGNORE_NAME
        if not gitignore_path.is_file():
            return cls(())
        lines = gitignore_path.read_text(encoding="utf-8", errors="replace").splitlines()
        rules = tuple(rule for line in lines if (rule := _parse_line(line)) is not None)
        return cls(rules)

    def matches(self, rel_path: str, *, is_dir: bool) -> bool:
        """Whether ``rel_path`` (repo-relative, POSIX, no leading ``/``) is ignored.

        Later rules override earlier ones, exactly like git's own last-match-wins rule.
        """
        basename = rel_path.rsplit("/", 1)[-1]
        ignored = False
        for rule in self._rules:
            if rule.dir_only and not is_dir:
                continue
            candidate = rel_path if rule.anchored else basename
            if fnmatch.fnmatch(candidate, rule.pattern):
                ignored = not rule.negate
        return ignored


def _parse_line(raw: str) -> _Rule | None:
    line = raw.rstrip("\r\n")
    if not line.strip() or line.startswith("#"):
        return None
    negate = line.startswith("!")
    if negate:
        line = line[1:]
    dir_only = line.endswith("/")
    if dir_only:
        line = line[:-1]
    if not line:
        return None
    anchored = line.startswith("/")
    if anchored:
        line = line[1:]
    elif "/" in line:
        anchored = True
    if not line:
        return None
    return _Rule(pattern=line, negate=negate, dir_only=dir_only, anchored=anchored)
