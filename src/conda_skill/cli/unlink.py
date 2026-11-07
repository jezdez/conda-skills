from __future__ import annotations

import json
from pathlib import Path

from conda.base.context import context
from rich.console import Console

from ..links import unlink
from .output import escape_terminal_controls


def execute(name: str, root: Path, backend: str, *, force: bool = False) -> None:
    """Remove the named destination link and report the result."""
    removed = unlink(name, root, backend, force=force)
    if context.json:
        print(json.dumps({"name": name, "removed": removed}, ensure_ascii=True))
    else:
        message = "Removed link for" if removed else "No link to remove for"
        Console(markup=False, highlight=False).print(
            f"{message} {escape_terminal_controls(name)}. "
            "Source environment and package unchanged."
        )
