"""Check a proposed bare release tag against package and recipe versions."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from conda.common.serialize import yaml
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager


def main() -> None:
    """Reject mismatched versions or missing release notes without publishing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Bare version, for example 0.1.0 (without v).")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = ProjectMetadata(str(root), PluginManager()).version
    recipe = yaml.loads((root / "recipe/recipe.yaml").read_text(encoding="utf-8"))
    if args.version != version or args.version != recipe["context"]["version"]:
        parser.error(
            f"Tag, resolved package version ({version}), and recipe version "
            "must match exactly."
        )
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
    print(f"Release metadata agrees on {args.version}. Nothing was published.")


if __name__ == "__main__":
    main()
