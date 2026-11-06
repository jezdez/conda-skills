from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console

from ..links import remove
from .output import escape_terminal_controls

if TYPE_CHECKING:
    from ..skills import Skill


def execute(skill: Skill, root: Path, backend: str) -> None:
    """Remove a matching skill link and report the result."""
    removed = remove(skill, root, backend)
    if context.json:
        print(json.dumps({"name": skill.name, "removed": removed}, ensure_ascii=True))
    else:
        message = "Removed link for" if removed else "No link to remove for"
        Console(markup=False, highlight=False).print(
            f"{message} {escape_terminal_controls(skill.name)}."
        )
