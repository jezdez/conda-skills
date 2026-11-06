from __future__ import annotations

import json
from pathlib import Path

from conda.base.context import context
from rich.console import Console

from ..links import status
from .output import print_table


def execute(root: Path, backend: str) -> None:
    """Report files and links in the agent's skill directory, without source lookup."""
    entries = status(root, backend)
    if context.json:
        print(json.dumps(entries, ensure_ascii=True))
    elif not entries:
        Console(markup=False, highlight=False).print("No skill entries found.")
    else:
        print_table(
            ("Name", "State", "Path", "Target"),
            (
                (entry["name"], entry["state"], entry["path"], entry["target"])
                for entry in entries
            ),
        )
