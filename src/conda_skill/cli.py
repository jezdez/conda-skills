from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context, determine_target_prefix, locate_prefix_by_name
from conda.exceptions import CondaError
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .links import install, remove, status
from .skills import discover

if TYPE_CHECKING:
    from argparse import Namespace


def escape_terminal_controls(value: object) -> str:
    """Render terminal control characters visibly in human-facing values."""
    return re.sub(
        r"[\x00-\x1f\x7f-\x9f]",
        lambda match: f"\\x{ord(match[0]):02x}",
        str(value),
    )


def execute(args: Namespace) -> int:
    """Run a parsed skill command, print its result, and return zero on success.

    Require explicit global scope for home-directory mutations and translate
    validation and filesystem failures into conda's normal error handling.
    """
    try:
        root = Path.home() if getattr(args, "global_scope", False) else Path.cwd()
        if (
            args.skill_command in ("install", "remove")
            and not args.global_scope
            and root.resolve() == Path.home().resolve()
        ):
            raise ValueError(
                "Use --global explicitly when changing skills in your home directory"
            )
        if args.skill_command == "status":
            result = status(root, args.backend)
        else:
            prefix = Path(
                locate_prefix_by_name(args.name)
                if args.name is not None
                else determine_target_prefix(context, args)
            )
            skills = discover(prefix)
            if args.skill_command == "list":
                result = [
                    {**asdict(skill), "path": str(skill.path)} for skill in skills
                ]
            else:
                selected = next(
                    (skill for skill in skills if skill.name == args.skill_name), None
                )
                if selected is None:
                    raise ValueError(
                        f"No package-owned skill {args.skill_name!r} in {prefix}"
                    )
                if args.skill_command == "install":
                    result = {
                        "name": selected.name,
                        "path": str(install(selected, root, args.backend)),
                    }
                else:
                    result = {
                        "name": selected.name,
                        "removed": remove(selected, root, args.backend),
                    }
        if context.json:
            print(json.dumps(result, ensure_ascii=True))
        else:
            console = Console(markup=False, highlight=False)
            if isinstance(result, list):
                if not result:
                    console.print(
                        "No package-owned skills found."
                        if args.skill_command == "list"
                        else "No skill entries found."
                    )
                else:
                    columns = (
                        ("name", "package", "version", "description", "path")
                        if args.skill_command == "list"
                        else ("name", "state", "path", "target")
                    )
                    table = Table(show_edge=False, pad_edge=False)
                    for column in columns:
                        table.add_column(column.title())
                    for row in result:
                        table.add_row(
                            *(
                                Text(escape_terminal_controls(row[column]))
                                for column in columns
                            )
                        )
                    console.print(table)
            elif args.skill_command == "install":
                console.print(
                    f"Linked {escape_terminal_controls(result['name'])} at "
                    f"{escape_terminal_controls(result['path'])}"
                )
            else:
                message = (
                    "Removed link for" if result["removed"] else "No link to remove for"
                )
                console.print(f"{message} {escape_terminal_controls(result['name'])}.")
        return 0
    except (ValueError, OSError) as exc:
        message = str(exc) if context.json else escape_terminal_controls(exc)
        raise CondaError(message) from exc
