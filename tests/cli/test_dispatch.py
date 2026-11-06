from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


def test_plural_alias_uses_same_commands(prefix: Path, run_cli) -> None:
    result = run_cli("list", "-p", str(prefix), "--json", command="skills")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)[0]["name"] == "example"


def test_installed_cli_roundtrip(prefix: Path, run_cli) -> None:
    listed = run_cli("list", "-p", str(prefix), "--json")
    assert listed.returncode == 0, listed.stderr
    assert json.loads(listed.stdout)[0]["name"] == "example"
    installed = run_cli("install", "example", "-p", str(prefix), "--json")
    assert installed.returncode == 0, installed.stderr
    target = Path(json.loads(installed.stdout)["path"])
    assert target.is_symlink()
    state = run_cli("status", "--json")
    assert state.returncode == 0, state.stderr
    assert json.loads(state.stdout)[0]["state"] == "linked"
    removed = run_cli("remove", "example", "-p", str(prefix), "--json")
    assert removed.returncode == 0, removed.stderr
    assert json.loads(removed.stdout)["removed"] is True
    assert not target.is_symlink()
    assert (prefix / "share/agent-skills/example/SKILL.md").is_file()


def test_installed_cli_uses_configured_json(prefix: Path, run_cli) -> None:
    result = run_cli("list", "-p", str(prefix), env={"CONDA_JSON": "true"})
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)[0]["name"] == "example"


@pytest.mark.parametrize("backend", ["agents", "claude"])
@pytest.mark.parametrize("json_from_env", [False, True])
def test_cli_roundtrip(
    prefix: Path, render_cli, monkeypatch, backend: str, json_from_env: bool
) -> None:
    json_args = () if json_from_env else ("--json",)
    if json_from_env:
        monkeypatch.setenv("CONDA_JSON", "true")
    listed = render_cli("list", "-p", str(prefix), *json_args)
    assert json.loads(listed)[0]["name"] == "example"
    for _ in range(2):
        installed = render_cli(
            "install",
            "example",
            "-p",
            str(prefix),
            "--backend",
            backend,
            *json_args,
        )
        assert Path(json.loads(installed)["path"]).is_symlink()
    state = render_cli("status", "--backend", backend, *json_args)
    assert json.loads(state)[0]["state"] == "linked"
    removed = render_cli(
        "remove",
        "example",
        "-p",
        str(prefix),
        "--backend",
        backend,
        *json_args,
    )
    assert json.loads(removed)["removed"] is True
    assert (prefix / "share/agent-skills/example/SKILL.md").is_file()


@pytest.mark.parametrize("json_from_env", [False, True])
def test_malformed_yaml_is_a_normal_cli_error(
    prefix: Path, run_cli, json_from_env: bool
) -> None:
    (prefix / "share/agent-skills/example/SKILL.md").write_text(
        "---\nname: example\ndescription: [broken\n---\n", encoding="utf-8"
    )
    json_args = () if json_from_env else ("--json",)
    env = {"CONDA_JSON": "true"} if json_from_env else None
    result = run_cli("list", "-p", str(prefix), *json_args, env=env)
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["exception_name"] == "CondaError"
    assert "traceback" not in payload


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
