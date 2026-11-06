from __future__ import annotations

import json
import shutil
from pathlib import Path


def test_human_status_output(prefix: Path, render_cli) -> None:
    render_cli("install", "example", "-p", str(prefix))
    state = render_cli("status")
    for text in ("Name", "State", "Path", "Target", "linked", "example"):
        assert text in state


def test_empty_status_output(prefix: Path, render_cli) -> None:
    (prefix / "conda-meta/agent-skill-example-1.0-0.json").unlink()
    result = render_cli("status")
    assert "No skill entries found." in result
    assert json.loads(render_cli("status", "--json")) == []


def test_destination_names_are_literal(tmp_path: Path, render_cli) -> None:
    directory = tmp_path / ".agents/skills"
    directory.mkdir(parents=True)
    (directory / "[bold]local").mkdir()
    result = render_cli("status")
    assert "[bold]local" in result
    assert "unmanaged" in result
    assert "State" in result


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


def test_status_json_preserves_cycle(tmp_path: Path, run_cli) -> None:
    path = tmp_path / ".agents/skills/loop"
    path.parent.mkdir(parents=True)
    path.symlink_to("loop", target_is_directory=True)
    result = run_cli("status", "--json")
    assert result.returncode == 0, result.stderr + result.stdout
    assert json.loads(result.stdout) == [
        {"name": "loop", "state": "broken", "path": str(path), "target": "loop"}
    ]
