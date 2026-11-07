from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..links import BACKENDS, destination
from ..skills import _validate_metadata, discover
from .init import execute as init
from .link import execute as link
from .output import escape_terminal_controls

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..skills import Skill


@dataclass(frozen=True)
class SkillSelection:
    """Installed skills and the backend chosen for their links."""

    skills: tuple[Skill, ...]
    backend: str

    def destinations(self, root: Path) -> tuple[Path, ...]:
        """Return link paths, rejecting redirects and conflicts without writes."""
        directory = destination(root, self.backend)
        targets = tuple(directory / skill.name for skill in self.skills)
        for skill, target in zip(self.skills, targets):
            if not os.path.lexists(target):
                continue
            if target.is_symlink():
                try:
                    if target.resolve(strict=True) == skill.path.resolve():
                        continue
                except (OSError, RuntimeError):
                    pass
            raise ValueError(f"Refusing to replace existing destination: {target}")
        return targets


def execute(source_prefix: Callable[[], Path], *, global_scope: bool) -> None:
    """Guide terminal users through review and confirmation before writes."""
    if context.json:
        raise ValueError(
            "quickstart does not support JSON. Use init, list, or link instead."
        )
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError(
            "quickstart requires an interactive terminal on stdin and stdout. "
            "use conda skill init, list, or link instead"
        )
    console = Console(markup=False, highlight=False)
    console.print("Skill quickstart", style="bold green")
    console.print(
        "Create starter files or link installed skills.\n"
        "No AI is used. This guide does not install packages or create environments."
    )
    console.print()
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
        console.print()
        if action == "link":
            console.print("Installed skills", style="bold")
            prefix = source_prefix()
            console.print(f"Source environment: {escape_terminal_controls(prefix)}")
            skills = discover(prefix)
            if not skills:
                console.print(
                    "No package-owned skills found in this environment.\n"
                    "Check the source with -n NAME or -p PATH. "
                    "Install a skill package with conda before linking it."
                )
                return
            for index, skill in enumerate(skills, 1):
                console.print(
                    f"{index}. {escape_terminal_controls(skill.name)}: "
                    f"{escape_terminal_controls(skill.description)}"
                )
            numbered = {str(i): skill for i, skill in enumerate(skills, 1)}
            while True:
                choice = Prompt.ask(
                    "Choose skill numbers (space/comma separated), all, or cancel",
                    console=console,
                ).strip()
                if choice == "cancel":
                    console.print("Cancelled. No changes made.")
                    return
                if choice == "all":
                    selected = tuple(skills)
                    break
                numbers = dict.fromkeys(choice.replace(",", " ").split())
                if numbers and all(number in numbered for number in numbers):
                    selected = tuple(numbered[number] for number in numbers)
                    break
                console.print(
                    "Invalid selection. Enter listed numbers, all, or cancel."
                )
            for skill in selected:
                console.print()
                console.print(f"Name: {escape_terminal_controls(skill.name)}")
                console.print(f"Review source: {escape_terminal_controls(skill.path)}")
                console.print(
                    f"Description: {escape_terminal_controls(skill.description)}"
                )
            console.print(
                "A skill is not automatically trustworthy because it comes "
                "from a package. "
                "Review SKILL.md and its supporting files before making them available "
                "to an agent."
            )
            console.print()
            backend = Prompt.ask(
                "Backend", choices=list(BACKENDS), default="agents", console=console
            )
            selection = SkillSelection(selected, backend)
        else:
            console.print("New skill", style="bold")
            name = Prompt.ask("Skill name", console=console)
            description = Prompt.ask(
                "Description (when to use this skill)", console=console
            )
            _validate_metadata(name, description)
            selection = (name, description)
        console.print()
        console.print("Destination", style="bold")
        console.print(
            f"project = current directory: {escape_terminal_controls(Path.cwd())}"
        )
        console.print(
            "Home-directory changes require starting quickstart with --global."
        )
        scope = Prompt.ask(
            "Scope",
            choices=["project", "home"],
            default="home" if global_scope else "project",
            console=console,
        )
        root = Path.home() if scope == "home" else Path.cwd()
        if not global_scope and (
            scope == "home" or root.resolve() == Path.home().resolve()
        ):
            raise ValueError(
                "Use --global explicitly when changing skills in your home directory"
            )
        console.print()
        console.print("Review changes", style="bold")
        if isinstance(selection, SkillSelection):
            for target in selection.destinations(root):
                console.print(f"Link destination: {escape_terminal_controls(target)}")
        else:
            name, description = selection
            console.print(f"Create skeleton: {escape_terminal_controls(root / name)}")
            console.print(f"Description: {escape_terminal_controls(description)}")
        console.print()
        confirmed = Confirm.ask(
            "Proceed with this change?", default=False, console=console
        )
    except (EOFError, KeyboardInterrupt):
        console.print("Cancelled. No changes made.")
        return
    if not confirmed:
        console.print("Cancelled. No changes made.")
    elif isinstance(selection, SkillSelection):
        console.print()
        for skill in selection.skills:
            link(skill, root, selection.backend)
    else:
        console.print()
        init(*selection, root)
