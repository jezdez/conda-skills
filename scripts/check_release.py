"""Check a proposed bare release tag against package and recipe versions."""

from __future__ import annotations

import argparse
import tomllib
from datetime import date
from pathlib import Path

from conda.common.serialize import yaml


def main() -> None:
    """Reject mismatched versions or missing release notes without publishing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Bare version, for example 0.1.0 (without v).")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    recipe = yaml.loads((root / "recipe/recipe.yaml").read_text(encoding="utf-8"))
    if (
        args.version != project["project"]["version"]
        or args.version != recipe["context"]["version"]
    ):
        parser.error("Tag, pyproject.toml, and recipe version must match exactly.")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = next(
        (
            line
            for line in changelog.splitlines()
            if line.startswith(f"## {args.version} - ")
        ),
        None,
    )
    if heading is None:
        parser.error("Add a dated release heading to CHANGELOG.md before tagging.")
    try:
        date.fromisoformat(heading.removeprefix(f"## {args.version} - "))
    except ValueError:
        parser.error("The release heading must use a valid YYYY-MM-DD date.")
    print(f"Release metadata agrees on {args.version}; nothing was published.")


if __name__ == "__main__":
    main()
