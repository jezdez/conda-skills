from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console

from .output import print_table

if TYPE_CHECKING:
    from ..skills import Skill


def execute(skills: list[Skill]) -> None:
    """Print discovered skills as a table or one JSON array."""
    if context.json:
        print(
            json.dumps(
                [{**asdict(skill), "path": str(skill.path)} for skill in skills],
                ensure_ascii=True,
            )
        )
    elif not skills:
        Console(markup=False, highlight=False).print("No package-owned skills found.")
    else:
        print_table(
            ("Name", "Package", "Version", "Description", "Path"),
            (
                (
                    skill.name,
                    skill.package,
                    skill.version,
                    skill.description,
                    skill.path,
                )
                for skill in skills
            ),
        )
