from __future__ import annotations

import re
from collections.abc import Iterable

from rich.console import Console
from rich.table import Table
from rich.text import Text

TERMINAL_CONTROL_PATTERN = re.compile(r"[\x00-\x1f\x7f-\x9f]")


def escape_terminal_controls(value: object) -> str:
    """Render terminal control characters visibly in human-facing values."""
    return TERMINAL_CONTROL_PATTERN.sub(
        lambda match: f"\\x{ord(match[0]):02x}",
        str(value),
    )


def print_table(columns: tuple[str, ...], rows: Iterable[Iterable[object]]) -> None:
    """Print labeled rows as literal text with visible terminal controls."""
    table = Table(show_edge=False, pad_edge=False)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*(Text(escape_terminal_controls(value)) for value in row))
    Console(markup=False, highlight=False).print(table)
