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


@pytest.fixture
def parser() -> argparse.ArgumentParser:
    """Configure a fresh parser for argument and help behavior tests."""
    parser = argparse.ArgumentParser(prog="conda skill")
    configure_parser(parser)
    return parser


def test_registers_skill_subcommand() -> None:
    [command] = conda_subcommands()
    assert command.name == "skill"
    assert command.aliases == ("skills",)
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
def test_standard_argument_behavior(parser, args: tuple[str, ...], code: int) -> None:
    with pytest.raises(SystemExit) as error:
        parser.parse_args(args)
    assert error.value.code == code


@pytest.mark.parametrize("command", ["install", "remove"])
def test_rejects_old_command_spellings(parser, command: str, capsys) -> None:
    with pytest.raises(SystemExit) as error:
        parser.parse_args([command, "example"])
    assert error.value.code == 2
    assert f"invalid choice: '{command}'" in capsys.readouterr().err


@pytest.mark.parametrize(
    "command,terms",
    [
        ("list", ("package-owned", "source environment")),
        ("inspect", ("inspect", "supporting files")),
        ("open", ("directory", "file manager")),
        ("status", ("destination", "entries")),
        ("link", ("link", "packaged skill")),
        ("unlink", ("destination", "link")),
        ("init", ("create", "skeleton")),
        ("quickstart", ("interactive", "guide")),
    ],
)
@pytest.mark.parametrize("overview", [True, False])
def test_help_explains_command_meaning(
    parser, command: str, terms: tuple[str, ...], overview: bool, capsys
) -> None:
    with pytest.raises(SystemExit) as error:
        parser.parse_args(["--help"] if overview else [command, "--help"])
    assert error.value.code == 0
    output = capsys.readouterr()
    assert output.err == ""
    text = " ".join(output.out.lower().split())
    if overview:
        text = next(
            line.strip().lower()
            for line in output.out.splitlines()
            if line.strip().startswith(f"{command} ")
        )
    for term in terms:
        assert term in text


@pytest.mark.parametrize("command", ["status", "link", "unlink", "init", "quickstart"])
def test_destination_help_names_current_directory(parser, command: str, capsys) -> None:
    with pytest.raises(SystemExit):
        parser.parse_args([command, "--help"])
    output = " ".join(capsys.readouterr().out.split())
    assert "current directory" in output
    assert "current project" not in output


def test_unlink_help_explains_force_limits(parser, capsys) -> None:
    with pytest.raises(SystemExit):
        parser.parse_args(["unlink", "--help"])
    output = " ".join(capsys.readouterr().out.split())
    assert "--force" in output
    assert "unverified symlink" in output
    assert "directories" in output
    assert "files" in output
    assert "redirected" in output


@pytest.mark.parametrize("selector", ["-n", "--name", "-p", "--prefix"])
def test_unlink_rejects_source_selectors(parser, selector: str, capsys) -> None:
    with pytest.raises(SystemExit) as error:
        parser.parse_args(["unlink", "example", selector, "source"])
    assert error.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err


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
    for name in ("link", "unlink"):
        args = parser.parse_args([name, "example"])
        assert args.skill_command == name
        assert args.skill_name == "example"


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
    # Pytest collection imports implementations, so check startup in a fresh process.
    test_installed_discovery()
    for module in sys.modules:
        assert module not in {
            "conda_skill.skills",
            "conda_skill.links",
            "conda_skill.scaffold",
        } and (
            not module.startswith("conda_skill.cli.")
            or module == "conda_skill.cli.parser"
        ), module
