from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from conda.base.context import reset_context

from conda_skill.cli.main import execute
from conda_skill.plugin import configure_parser


@pytest.fixture
def run_cli(tmp_path: Path) -> Callable[..., subprocess.CompletedProcess[str]]:
    home = tmp_path / "home"
    home.mkdir()
    condarc = tmp_path / "condarc"
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
        CONDA_AUTO_UPDATE_CONDA="false",
        NO_COLOR="1",
        COLUMNS="240",
    )

    def run(
        *args: str,
        cwd: Path = tmp_path,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "conda", "skill", *args],
            cwd=cwd,
            env={**environment, **(env or {})},
            text=True,
            capture_output=True,
        )

    return run


@pytest.fixture
def render_cli(tmp_path: Path, monkeypatch, capsys):
    """Exercise real command output without starting another conda process."""
    for key in tuple(os.environ):
        if key.startswith("CONDA_") or key == "CONDARC":
            monkeypatch.delenv(key)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("COLUMNS", "240")
    monkeypatch.chdir(tmp_path)
    parser = argparse.ArgumentParser()
    configure_parser(parser)

    def render(*args: str) -> str:
        parsed = parser.parse_args(args)
        reset_context(search_path=(), argparse_args=parsed)
        assert execute(parsed) == 0
        output = capsys.readouterr()
        assert output.err == ""
        return output.out

    try:
        yield render
    finally:
        monkeypatch.undo()
        reset_context(search_path=())
