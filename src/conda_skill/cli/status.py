from __future__ import annotations

import json
from pathlib import Path

from conda.base.context import context
from rich.console import Console

from ..links import BACKENDS, status
from .output import print_table


def execute(root: Path, backend: str, *, all_backends: bool = False) -> None:
    """Report files and links in the agent's skill directory, without source lookup."""
    entries = (
        [
            {"backend": name, **entry}
            for name in BACKENDS
            for entry in status(root, name)
        ]
        if all_backends
        else status(root, backend)
    )
    if context.json:
        print(json.dumps(entries, ensure_ascii=True))
    elif not entries:
        Console(markup=False, highlight=False).print("No skill entries found.")
    else:
        columns = ("name", "state", "path", "target")
        if all_backends:
            columns = ("backend", *columns)
        print_table(
            tuple(column.title() for column in columns),
            (tuple(entry[column] for column in columns) for entry in entries),
        )
