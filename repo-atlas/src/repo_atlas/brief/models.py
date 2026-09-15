"""Result types for a brief run."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Section:
    """One written section of the brief, with the confidence it is entitled to."""

    title: str
    body: str
    tag: str


@dataclass
class BriefResult:
    """Everything one run produced, including what it cost and what it opened."""

    repo_name: str
    run_type: str
    sections: list[Section] = field(default_factory=list)
    files_read: tuple[str, ...] = ()
    token_usage: list[dict[str, Any]] = field(default_factory=list)
    #: (node id, label) for the nodes this brief was built from, so a reader can follow
    #: any claim back to its note in the vault (PRD R4.4).
    vault_links: tuple[tuple[str, str], ...] = ()

    def render(self) -> str:
        """Render BRIEF.md. Every section states its own confidence (CLAUDE.md §4)."""
        lines = [
            f"# {self.repo_name} — architecture brief",
            "",
            "> Written from the repository's knowledge graph and a budgeted selection of its "
            "source. Each section is tagged with the confidence it is entitled to: "
            "`INFERRED` is synthesis grounded in graph facts, `AMBIGUOUS` means the context "
            "did not support the claim and a human should check.",
            "",
        ]
        for section in self.sections:
            lines += [f"## {section.title}", "", f"*{section.tag}*", "", section.body, ""]
        if self.vault_links:
            lines += ["## Follow these into the vault", ""]
            lines += [f"- [[{node_id}|{label}]]" for node_id, label in self.vault_links]
            lines.append("")
        if self.files_read:
            lines += ["## Sources read", ""]
            lines += [f"- `{name}`" for name in self.files_read]
            lines.append("")
        return "\n".join(lines)

    def write(self, path: str | Path) -> Path:
        """Write the rendered brief, creating parent directories as needed."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.render(), encoding="utf-8")
        return target
