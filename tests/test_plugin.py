from __future__ import annotations

import argparse
import os
import subprocess
import sys
from importlib.metadata import distribution
from pathlib import Path

import pytest
from conda.plugins.hookspec import CondaSpecs
from conda.plugins.manager import CondaPluginManager

from conda_skill.plugin import conda_subcommands, configure_parser, run


def test_registers_skill_subcommand() -> None:
    [command] = conda_subcommands()
    assert command.name == "skill"
    assert command.action is run
    assert command.configure_parser is configure_parser
    parser = argparse.ArgumentParser(prog="conda skill")
    configure_parser(parser)
    args = parser.parse_args(["list", "--json"])
    assert args.skill_command == "list"
    assert args.json is True


@pytest.mark.parametrize(
    "args,code",
    [
        (("--help",), 0),
        (("list", "--help"), 0),
        (("list", "--unknown"), 2),
        ((), 2),
        (("list", "-n", "x", "-p", "y"), 2),
    ],
)
def test_standard_argument_behavior(args: tuple[str, ...], code: int) -> None:
    parser = argparse.ArgumentParser(prog="conda skill")
    configure_parser(parser)
    with pytest.raises(SystemExit) as error:
        parser.parse_args(args)
    assert error.value.code == code


def test_installed_discovery() -> None:
    entry_points = [
        entry
        for entry in distribution("conda-skills").entry_points
        if entry.group == "conda"
    ]
    assert [(entry.name, entry.value) for entry in entry_points] == [
        ("conda-skills", "conda_skill.plugin")
    ]
    manager = CondaPluginManager()
    manager.add_hookspecs(CondaSpecs)
    assert manager.load_entrypoints("conda", name="conda-skills") == 1
    [command] = manager.get_hook_results("subcommands")
    assert command.name == "skill"
    parser = argparse.ArgumentParser(prog="conda skill")
    command.configure_parser(parser)
    assert parser.parse_args(["status"]).skill_command == "status"


def test_lazy_registration(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve())],
        cwd=tmp_path,
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


if __name__ == "__main__":
    # Pytest collection imports implementations; check startup in a fresh process.
    test_installed_discovery()
    for module in sys.modules:
        assert module not in {
            "conda_skill.cli",
            "conda_skill.skills",
            "conda_skill.links",
        } and not module.startswith("conda_skill.cli."), module
