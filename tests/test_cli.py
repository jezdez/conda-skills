from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
from conda.base.context import reset_context

from conda_skill.cli import execute
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


@pytest.mark.parametrize("backend", ["agents", "claude"])
def test_installed_cli_roundtrip(prefix: Path, run_cli, backend: str) -> None:
    listed = run_cli("list", "-p", str(prefix), "--json")
    assert listed.returncode == 0, listed.stderr + listed.stdout
    assert json.loads(listed.stdout)[0]["name"] == "example"
    for _ in range(2):
        installed = run_cli(
            "install",
            "example",
            "-p",
            str(prefix),
            "--backend",
            backend,
            "--json",
        )
        assert installed.returncode == 0, installed.stderr + installed.stdout
        assert Path(json.loads(installed.stdout)["path"]).is_symlink()
    state = run_cli("status", "--backend", backend, "--json")
    assert state.returncode == 0, state.stderr
    assert json.loads(state.stdout)[0]["state"] == "linked"
    removed = run_cli(
        "remove", "example", "-p", str(prefix), "--backend", backend, "--json"
    )
    assert removed.returncode == 0, removed.stderr + removed.stdout
    assert json.loads(removed.stdout)["removed"] is True
    assert (prefix / "share/agent-skills/example/SKILL.md").is_file()


def test_installed_global_is_explicit_and_isolated(
    prefix: Path, tmp_path: Path, run_cli
) -> None:
    result = run_cli("install", "example", "-p", str(prefix), "--global", "--json")
    assert result.returncode == 0, result.stderr + result.stdout
    assert (
        Path(json.loads(result.stdout)["path"])
        == tmp_path / "home/.agents/skills/example"
    )
    assert not (tmp_path / ".agents").exists()


def test_installed_json_errors(prefix: Path, tmp_path: Path, run_cli) -> None:
    target = tmp_path / ".agents/skills/example"
    target.mkdir(parents=True)
    result = run_cli("install", "example", "-p", str(prefix), "--json")
    assert result.returncode != 0
    assert "Refusing" in json.loads(result.stdout)["error"]
    assert target.is_dir()
    result = run_cli("install", "absent", "-p", str(prefix), "--json")
    assert result.returncode != 0
    assert "No package-owned" in json.loads(result.stdout)["error"]


def test_malformed_yaml_is_a_normal_cli_error(prefix: Path, run_cli) -> None:
    (prefix / "share/agent-skills/example/SKILL.md").write_text(
        "---\nname: example\ndescription: [broken\n---\n", encoding="utf-8"
    )
    result = run_cli("list", "-p", str(prefix), "--json")
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["exception_name"] == "CondaError"
    assert "traceback" not in payload


def test_home_mutation_requires_global(prefix: Path, tmp_path: Path, run_cli) -> None:
    home = tmp_path / "home"
    result = run_cli("install", "example", "-p", str(prefix), "--json", cwd=home)
    assert result.returncode != 0
    assert "--global" in json.loads(result.stdout)["error"]
    assert not (home / ".agents").exists()


def test_unknown_environment_lookup_does_not_create_directories(
    tmp_path: Path, run_cli
) -> None:
    envs = tmp_path / "not-created"
    result = run_cli(
        "list",
        "-n",
        "absent-skill-test",
        "--json",
        env={"CONDA_ENVS_PATH": str(envs)},
    )
    assert result.returncode != 0
    assert "EnvironmentNameNotFound" in json.loads(result.stdout)["exception_name"]
    assert not envs.exists()


def test_human_output_roundtrip(prefix: Path, render_cli) -> None:
    listed = render_cli("list", "-p", str(prefix))
    for text in ("Name", "Package", "Version", "Description", "Path", "example"):
        assert text in listed
    installed = render_cli("install", "example", "-p", str(prefix))
    assert "Linked example at " in installed
    state = render_cli("status")
    for text in ("Name", "State", "Path", "Target", "linked", "example"):
        assert text in state
    removed = render_cli("remove", "example", "-p", str(prefix))
    assert "Removed link for example." in removed
    absent = render_cli("remove", "example", "-p", str(prefix))
    assert "No link to remove for example." in absent


@pytest.mark.parametrize("command", ["list", "status"])
def test_empty_output(prefix: Path, render_cli, command: str) -> None:
    (prefix / "conda-meta/agent-skill-example-1.0-0.json").unlink()
    args = ("list", "-p", str(prefix)) if command == "list" else ("status",)
    result = render_cli(*args)
    assert (
        "No package-owned skills found."
        if command == "list"
        else "No skill entries found."
    ) in result
    assert json.loads(render_cli(*args, "--json")) == []


def test_package_text_is_literal_and_json_is_unchanged(
    prefix: Path, render_cli
) -> None:
    description = "[bold]literal[/bold]\x1b[31m\nnext\x85line"
    (prefix / "share/agent-skills/example/SKILL.md").write_text(
        f"---\nname: example\ndescription: {json.dumps(description)}\n---\n",
        encoding="utf-8",
    )
    result = render_cli("list", "-p", str(prefix))
    assert r"[bold]literal[/bold]\x1b[31m\x0anext\x85line" in result
    assert "\x1b" not in result
    structured = render_cli("list", "-p", str(prefix), "--json")
    assert json.loads(structured)[0]["description"] == description


def test_destination_names_are_literal(tmp_path: Path, render_cli) -> None:
    directory = tmp_path / ".agents/skills"
    directory.mkdir(parents=True)
    (directory / "[bold]local").mkdir()
    result = render_cli("status")
    assert "[bold]local" in result
    assert "unmanaged" in result
    assert "State" in result


def test_cli_ignores_inherited_xdg_config(tmp_path: Path, monkeypatch, request) -> None:
    config = tmp_path / "external-config/conda"
    config.mkdir(parents=True)
    (config / "condarc").write_text("channels: [\n", encoding="utf-8")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config.parent))
    run_cli = request.getfixturevalue("run_cli")
    result = run_cli("status", "--json")
    assert result.returncode == 0, result.stderr + result.stdout
    assert json.loads(result.stdout) == []


@pytest.mark.skipif(sys.platform == "win32", reason="Windows forbids controls in paths")
def test_error_paths_are_safe_in_human_output(tmp_path: Path, run_cli) -> None:
    project = tmp_path / "project\x1b[31m"
    project.mkdir()
    (project / ".agents").symlink_to(tmp_path, target_is_directory=True)
    result = run_cli("status", cwd=project)
    assert result.returncode != 0
    assert "\x1b" not in result.stderr
    assert r"project\x1b[31m" in result.stderr
    structured = run_cli("status", "--json", cwd=project)
    assert structured.returncode != 0
    assert "project\x1b[31m" in json.loads(structured.stdout)["error"]


def test_status_survives_deleted_source(prefix: Path, tmp_path: Path, run_cli) -> None:
    installed = run_cli("install", "example", "-p", str(prefix), "--json")
    assert installed.returncode == 0, installed.stderr
    target = json.loads(installed.stdout)["path"]
    source = str(prefix / "share/agent-skills/example")
    shutil.rmtree(prefix)
    result = run_cli(
        "status", "--json", env={"CONDA_PREFIX": str(tmp_path / "missing")}
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [
        {"name": "example", "state": "broken", "path": target, "target": source}
    ]
