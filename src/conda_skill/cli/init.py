from __future__ import annotations

import json
from pathlib import Path

from conda.base.context import context
from rich.console import Console

from ..scaffold import DEFAULT_DESCRIPTION, create
from .output import escape_terminal_controls


def execute(name: str, description: str | None, root: Path) -> None:
    """Create an authoring skeleton and report paths and remaining author tasks."""
    path = create(
        name, DEFAULT_DESCRIPTION if description is None else description, root
    )
    recipe = path / "recipe/recipe.yaml"
    if context.json:
        print(json.dumps({"name": name, "path": str(path), "recipe": str(recipe)}))
    else:
        console = Console(markup=False, highlight=False)
        console.print(f"Created {escape_terminal_controls(path / 'SKILL.md')}")
        console.print(f"Recipe: {escape_terminal_controls(recipe)}")
        console.print(
            "The skeleton is not installed. Replace the placeholder instructions "
            "and review the description before use."
        )
        console.print(
            "Review recipe metadata and choose a license before distribution. "
            "The generated build.py packages SKILL.md only."
        )
        console.print(
            "From the new directory, build with: "
            "rattler-build build --recipe recipe/recipe.yaml -c conda-forge"
        )
