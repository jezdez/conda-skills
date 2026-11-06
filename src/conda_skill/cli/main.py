from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context, determine_target_prefix, locate_prefix_by_name
from conda.exceptions import CondaError

from ..skills import discover
from .init import execute as init
from .install import execute as install
from .list import execute as list_skills
from .output import escape_terminal_controls
from .quickstart import execute as quickstart
from .remove import execute as remove
from .status import execute as status

if TYPE_CHECKING:
    from argparse import Namespace


def execute(args: Namespace) -> int:
    """Resolve scope, dispatch a skill command, and translate errors for conda."""
    try:
        root = Path.home() if getattr(args, "global_scope", False) else Path.cwd()
        if (
            args.skill_command in ("install", "remove", "init")
            and not args.global_scope
            and root.resolve() == Path.home().resolve()
        ):
            raise ValueError(
                "Use --global explicitly when changing skills in your home directory"
            )
        if args.skill_command == "init":
            init(args.skill_name, args.description, root)
        elif args.skill_command == "quickstart":
            quickstart(
                lambda: discover(source_prefix(args)), global_scope=args.global_scope
            )
        elif args.skill_command == "status":
            status(root, args.backend, all_backends=args.all_backends)
        else:
            prefix = source_prefix(args)
            skills = discover(prefix)
            if args.skill_command == "list":
                list_skills(skills)
            else:
                selected = next(
                    (skill for skill in skills if skill.name == args.skill_name), None
                )
                if selected is None:
                    raise ValueError(
                        f"No package-owned skill {args.skill_name!r} in {prefix}"
                    )
                if args.skill_command == "install":
                    install(selected, root, args.backend)
                else:
                    remove(selected, root, args.backend)
        return 0
    except (ValueError, OSError) as exc:
        message = str(exc) if context.json else escape_terminal_controls(exc)
        raise CondaError(message) from exc


def source_prefix(args: Namespace) -> Path:
    """Resolve the selected source through conda without creating an environment."""
    return Path(
        locate_prefix_by_name(args.name)
        if args.name is not None
        else determine_target_prefix(context, args)
    )
