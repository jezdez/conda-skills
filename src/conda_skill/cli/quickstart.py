from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..links import BACKENDS, destination
from ..skills import validate_description, validate_name
from .init import execute as init
from .install import execute as install
from .output import escape_terminal_controls

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..skills import Skill


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
        "This guide creates an authoring skeleton or links an installed skill. "
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
        selected = None
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
                "Package ownership does not establish trust. Review SKILL.md and its "
                "supporting files before exposing them to an agent."
            )
            backend = Prompt.ask(
                "Backend", choices=list(BACKENDS), default="agents", console=console
            )
        else:
            name = Prompt.ask("Skill name", console=console)
            description = Prompt.ask(
                "Description (when to use this skill)", console=console
            )
            validate_name(name)
            validate_description(description)
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
        if selected is not None:
            target = destination(root, backend) / selected.name
            console.print(f"Link destination: {escape_terminal_controls(target)}")
        else:
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
    elif selected is not None:
        install(selected, root, backend)
    else:
        init(name, description, root)
