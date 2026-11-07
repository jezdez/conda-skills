from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console

from ..skills import _validate_directory
from .output import escape_terminal_controls

if TYPE_CHECKING:
    from ..skills import Skill


def execute(skill: Skill) -> None:
    """Request the OS file manager for a skill directory, never a packaged file."""
    _validate_directory(skill.path, skill.path.parents[2])
    path = skill.path.resolve(strict=True)
    if not path.is_dir():
        raise ValueError(f"Skill is not a directory: {path}")
    try:
        if sys.platform == "win32":
            os.startfile(str(path), "explore")
        else:
            command = (
                ["open", "-a", "Finder"] if sys.platform == "darwin" else ["xdg-open"]
            )
            subprocess.run(
                [*command, str(path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(
            f"Could not open a file manager for {path}. "
            "Use conda skill inspect to review files in a terminal."
        ) from exc
    if context.json:
        print(json.dumps({"name": skill.name, "path": str(path), "opened": True}))
    else:
        Console(markup=False, highlight=False).print(
            f"Requested file manager for {escape_terminal_controls(path)}"
        )
