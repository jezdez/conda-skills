"""Check installed plugin discovery and harmless commands outside the checkout."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from importlib.metadata import distribution
from pathlib import Path

from conda.plugins.hookspec import CondaSpecs
from conda.plugins.manager import CondaPluginManager

import conda_skill


def main() -> None:
    """Check installed metadata, lazy registration, and isolated JSON output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed-prefix", type=Path)
    args = parser.parse_args()
    if args.installed_prefix:
        assert (
            Path(conda_skill.__file__)
            .resolve()
            .is_relative_to(args.installed_prefix.resolve())
        ), "The smoke test imported the checkout instead of the installed wheel"
    entries = distribution("conda-skills").entry_points
    assert any(
        entry.group == "conda"
        and entry.name == "conda-skills"
        and entry.value == "conda_skill.plugin"
        for entry in entries
    )
    manager = CondaPluginManager()
    manager.add_hookspecs(CondaSpecs)
    assert manager.load_entrypoints("conda", name="conda-skills") == 1
    [command] = manager.get_hook_results("subcommands")
    assert command.name == "skill"
    command.configure_parser(argparse.ArgumentParser())
    assert "conda_skill.cli.main" not in sys.modules
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        home = root / "home"
        home.mkdir()
        condarc = root / "condarc"
        condarc.write_text("{}\n", encoding="utf-8")
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("CONDA_") and key not in {"CONDARC", "PYTHONPATH"}
        }
        environment.update(
            HOME=str(home),
            USERPROFILE=str(home),
            XDG_CONFIG_HOME=str(home / ".config"),
            CONDARC=str(condarc),
            CONDA_NO_PLUGINS="false",
            CONDA_JSON="false",
        )
        for arguments in (("--help",), ("status", "--json")):
            result = subprocess.run(
                [sys.executable, "-I", "-m", "conda", "skill", *arguments],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            if arguments == ("--help",):
                assert "install" in result.stdout and "remove" in result.stdout
            else:
                assert json.loads(result.stdout) == []
    print("Installed plugin smoke checks passed.")


if __name__ == "__main__":
    main()
