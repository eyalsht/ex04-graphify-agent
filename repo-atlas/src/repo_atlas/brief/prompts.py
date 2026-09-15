"""Prompts for the brief. One per section, all sharing the same assembled context.

Deliberately identical across the graph-guided and naive routes: the only thing that
differs between them is *what context they were given*, which is the whole point of the
comparison in PRD R5. Change a prompt here and both routes change together.
"""

from __future__ import annotations

SYSTEM = (
    "You are explaining an unfamiliar Python repository to a new contributor. "
    "Ground every statement in the supplied graph and source context. "
    "Where the context does not support a claim, say what is unknown rather than "
    "guessing. Prefer concrete names — modules, classes, functions — over generalities. "
    "Be concise: a few short paragraphs or a tight list."
)

#: Section title -> the question that section answers.
SECTIONS: dict[str, str] = {
    "What this repository does": (
        "From the context, what is this repository for? What problem does it solve, and "
        "what are its main capabilities?"
    ),
    "Entry points": (
        "What are the entry points — CLI commands, public APIs, or main modules? Name them."
    ),
    "Module map": ("Describe the main modules or packages and what each is responsible for."),
    "Hot spots": (
        "Which parts of the codebase are most central or most connected, and why do they "
        "matter to someone reading this code for the first time?"
    ),
    "How data flows": (
        "Trace the main flow through the system: what calls what, and in what order?"
    ),
    "Where to start reading": (
        "Give an ordered short list of the files or symbols to read first, and say why each."
    ),
}


def section_prompt(title: str, question: str, context: str) -> str:
    """The user message for one section: its question, then the shared context."""
    return f"## {title}\n\n{question}\n\n---\nCONTEXT\n---\n{context}\n"
