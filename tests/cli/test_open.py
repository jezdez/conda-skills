from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from conda.exceptions import CondaError

from conda_skill.cli import open as open_command
from conda_skill.skills import discover


@pytest.mark.parametrize("platform", ["darwin", "linux", "win32"])
def test_open_uses_file_manager_for_directory(
    prefix: Path, render_cli, monkeypatch, platform: str
) -> None:
    calls = []

    def run(args, *, check, stdout, stderr):
        assert check is True
        assert stdout == subprocess.DEVNULL
        assert stderr == subprocess.PIPE
        calls.append(args)

    def startfile(path, operation):
        calls.append([path, operation])

    monkeypatch.setattr(open_command.sys, "platform", platform)
    monkeypatch.setattr(open_command.subprocess, "run", run)
    monkeypatch.setattr(open_command.os, "startfile", startfile, raising=False)
    result = json.loads(render_cli("open", "example", "-p", str(prefix), "--json"))
    path = str(prefix / "share/agent-skills/example")
    assert result == {"name": "example", "path": path, "opened": True}
    expected = {
        "darwin": ["open", "-a", "Finder", path],
        "linux": ["xdg-open", path],
        "win32": [path, "explore"],
    }
    assert calls == [expected[platform]]


def test_open_human_output(prefix: Path, render_cli, monkeypatch) -> None:
    monkeypatch.setattr(open_command.sys, "platform", "linux")

    def run(args, *, check, stdout, stderr):
        pass

    monkeypatch.setattr(open_command.subprocess, "run", run)
    output = render_cli("open", "example", "-p", str(prefix))
    assert "Requested file manager" in output
    assert str(prefix / "share/agent-skills/example") in output


@pytest.mark.parametrize("failure", ["missing", "exit"])
def test_open_failure_is_a_conda_error(
    prefix: Path, render_cli, monkeypatch, failure: str
) -> None:
    monkeypatch.setattr(open_command.sys, "platform", "linux")

    def run(args, *, check, stdout, stderr):
        if failure == "missing":
            raise FileNotFoundError("xdg-open is unavailable")
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(open_command.subprocess, "run", run)
    with pytest.raises(CondaError, match="file manager"):
        render_cli("open", "example", "-p", str(prefix))


def test_open_rechecks_replaced_source(prefix: Path, tmp_path: Path) -> None:
    [skill] = discover(prefix)
    outside = tmp_path / "outside"
    skill.path.rename(outside)
    skill.path.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes environment"):
        open_command.execute(skill)


def test_open_refuses_file_even_if_validation_is_bypassed(
    prefix: Path, tmp_path: Path, monkeypatch
) -> None:
    [skill] = discover(prefix)
    skill.path.rename(tmp_path / "saved-skill")
    skill.path.write_text("not a directory")

    def validated(path, root):
        pass

    monkeypatch.setattr(open_command, "_validate_directory", validated)
    with pytest.raises(ValueError, match="not a directory"):
        open_command.execute(skill)
