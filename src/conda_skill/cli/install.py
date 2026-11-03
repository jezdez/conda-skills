from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console

from ..links import install
from .output import escape_terminal_controls

if TYPE_CHECKING:
    from ..skills import Skill


def execute(skill: Skill, root: Path, backend: str) -> None:
    """Install the selected skill link and print its name and destination."""
    path = install(skill, root, backend)
    if context.json:
        print(json.dumps({"name": skill.name, "path": str(path)}, ensure_ascii=True))
    else:
        Console(markup=False, highlight=False).print(
            f"Linked {escape_terminal_controls(skill.name)} at "
            f"{escape_terminal_controls(path)}"
        )
