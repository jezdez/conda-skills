from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..links import BACKENDS, destination
from ..skills import _validate_metadata
from .init import execute as init
from .install import execute as install
from .output import escape_terminal_controls

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..skills import Skill


@dataclass(frozen=True)
class SkillSelection:
    """An installed skill and the backend chosen for its link."""

    skill: Skill
    backend: str

    def destination(self, root: Path) -> Path:
        """Return the proposed link path after checking client directories."""
        return destination(root, self.backend) / self.skill.name


def execute(load_skills: Callable[[], list[Skill]], *, global_scope: bool) -> None:
    """Guide terminal users through review and confirmation before a single write."""
    if context.json:
        raise ValueError(
            "quickstart does not support JSON; use init, list, or install instead"
        )
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError(
            "quickstart requires an interactive terminal on stdin and stdout; "
            "use conda skill init, list, or install instead"
        )
    console = Console(markup=False, highlight=False)
    console.print(
        "Start a new skill or link an installed one. "
        "This guide creates starter files or a link. "
        "It does not use AI, install packages, or create environments."
    )
    try:
        action = Prompt.ask(
            "Choose an action",
            choices=["link", "new", "cancel"],
            default="cancel",
            console=console,
        )
        if action == "cancel":
            console.print("Cancelled. No changes made.")
            return
        selection: SkillSelection | tuple[str, str]
        if action == "link":
            skills = load_skills()
            if not skills:
                console.print(
                    "No package-owned skills found. Use conda skill init to author one."
                )
                return
            for index, skill in enumerate(skills, 1):
                console.print(f"{index}. {escape_terminal_controls(skill.name)}")
            choice = Prompt.ask(
                "Choose a skill number",
                choices=[str(i) for i in range(1, len(skills) + 1)],
                console=console,
            )
            selected = skills[int(choice) - 1]
            console.print(f"Review source: {escape_terminal_controls(selected.path)}")
            console.print(
                f"Description: {escape_terminal_controls(selected.description)}"
            )
            console.print(
                "A skill is not automatically trustworthy because it comes "
                "from a package. "
                "Review SKILL.md and its supporting files before making them available "
                "to an agent."
            )
            backend = Prompt.ask(
                "Backend", choices=list(BACKENDS), default="agents", console=console
            )
            selection = SkillSelection(selected, backend)
        else:
            name = Prompt.ask("Skill name", console=console)
            description = Prompt.ask(
                "Description (when to use this skill)", console=console
            )
            _validate_metadata(name, description)
            selection = (name, description)
        console.print(
            "Home-directory changes require starting quickstart with --global."
        )
        scope = Prompt.ask(
            "Scope", choices=["project", "home"], default="project", console=console
        )
        root = Path.home() if scope == "home" else Path.cwd()
        if not global_scope and (
            scope == "home" or root.resolve() == Path.home().resolve()
        ):
            raise ValueError(
                "Use --global explicitly when changing skills in your home directory"
            )
        if isinstance(selection, SkillSelection):
            target = selection.destination(root)
            console.print(f"Link destination: {escape_terminal_controls(target)}")
        else:
            name, description = selection
            console.print(f"Create skeleton: {escape_terminal_controls(root / name)}")
            console.print(f"Description: {escape_terminal_controls(description)}")
        confirmed = Confirm.ask(
            "Proceed with this change?", default=False, console=console
        )
    except (EOFError, KeyboardInterrupt):
        console.print("Cancelled. No changes made.")
        return
    if not confirmed:
        console.print("Cancelled. No changes made.")
    elif isinstance(selection, SkillSelection):
        install(selection.skill, root, selection.backend)
    else:
        init(*selection, root)
