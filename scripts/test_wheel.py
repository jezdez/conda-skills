"""Install the built wheel into a disposable environment and check discovery."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    """Test an installed wheel using conda dependencies from the build environment."""
    root = Path(__file__).resolve().parents[1]
    wheels = list((root / "dist").glob("conda_skills-*.whl"))
    if len(wheels) != 1:
        raise SystemExit(
            "Expected exactly one conda-skills wheel in dist; "
            "build a wheel if missing, or remove extra wheels."
        )
    with tempfile.TemporaryDirectory() as temporary:
        prefix = Path(temporary) / "wheel-env"
        subprocess.run(
            [sys.executable, "-m", "venv", "--system-site-packages", str(prefix)],
            check=True,
        )
        python = prefix / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--ignore-installed",
                str(wheels[0]),
            ],
            cwd=temporary,
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-I",
                str(root / "scripts/smoke_plugin.py"),
                "--installed-prefix",
                str(prefix),
            ],
            cwd=temporary,
            check=True,
        )


if __name__ == "__main__":
    main()
