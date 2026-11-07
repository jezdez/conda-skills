"""Resolve package metadata for release checks and conda builds."""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import date
from pathlib import Path

from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager


def main() -> None:
    """Reject mismatched versions or missing release notes without publishing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?", help="Bare release version (without v).")
    parser.add_argument(
        "--build-conda",
        action="store_true",
        help="Build the conda recipe with the version resolved by Hatch.",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = ProjectMetadata(str(root), PluginManager()).version
    if args.version is None and not args.build_conda:
        parser.error("Provide a release version or use --build-conda.")
    if args.version is not None and args.version != version:
        parser.error(
            f"Tag and resolved package version ({version}) must match exactly."
        )
    if args.build_conda:
        subprocess.run(
            [
                "rattler-build",
                "build",
                "--recipe",
                "recipe/recipe.yaml",
                "--output-dir",
                "conda-dist",
                "-c",
                "conda-forge",
            ],
            cwd=root,
            env={**os.environ, "CONDA_SKILLS_VERSION": version},
            check=True,
        )
        return
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
