from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest


def test_human_unlink_output(prefix: Path, render_cli) -> None:
    render_cli("link", "example", "-p", str(prefix))
    removed = render_cli("unlink", "example")
    assert "Removed link for example." in removed
    assert "Source environment and package unchanged." in removed
    absent = render_cli("unlink", "example")
    assert "No link to remove for example." in absent


@pytest.mark.parametrize("present", [False, True])
def test_unlink_ignores_missing_active_environment(
    prefix: Path, tmp_path: Path, run_cli, present: bool
) -> None:
    if present:
        linked = run_cli("link", "example", "-p", str(prefix), "--json")
        assert linked.returncode == 0, linked.stderr
    missing = tmp_path / "missing-env"
    result = run_cli(
        "unlink",
        "example",
        "--json",
        env={"CONDA_PREFIX": str(missing), "CONDA_DEFAULT_ENV": str(missing)},
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert json.loads(result.stdout) == {"name": "example", "removed": present}
    assert not missing.exists()
    assert (prefix / "share/agent-skills/example/SKILL.md").is_file()


def test_unlink_removed_source_requires_explicit_force(
    prefix: Path, tmp_path: Path, run_cli
) -> None:
    linked = run_cli("link", "example", "-p", str(prefix), "--json")
    assert linked.returncode == 0, linked.stderr
    target = Path(json.loads(linked.stdout)["path"])
    shutil.rmtree(prefix)
    refused = run_cli("unlink", "example", "--json")
    assert refused.returncode != 0
    error = json.loads(refused.stdout)
    assert error["exception_name"] == "CondaError"
    assert "--force" in error["error"] and "status" in error["error"]
    assert "traceback" not in error
    assert target.is_symlink()
    removed = run_cli("unlink", "example", "--force", "--json")
    assert removed.returncode == 0, removed.stderr
    assert json.loads(removed.stdout) == {"name": "example", "removed": True}
    assert not target.is_symlink()
    assert not prefix.exists()


@pytest.mark.parametrize(
    "invalid", ["missing-name", "invalid-build-number", "null", "array"]
)
def test_unlink_structurally_invalid_record_is_unverifiable(
    prefix: Path, tmp_path: Path, run_cli, invalid: str
) -> None:
    linked = run_cli("link", "example", "-p", str(prefix), "--json")
    assert linked.returncode == 0, linked.stderr
    target = Path(json.loads(linked.stdout)["path"])
    record = prefix / "conda-meta/agent-skill-example-1.0-0.json"
    data = json.loads(record.read_text())
    if invalid == "missing-name":
        data = {}
    elif invalid == "null":
        data = None
    elif invalid == "array":
        data = []
    else:
        data["build_number"] = "invalid"
    record.write_text(json.dumps(data), encoding="utf-8")
    refused = run_cli("unlink", "example", "--json")
    assert refused.returncode != 0
    error = json.loads(refused.stdout)
    assert error["exception_name"] == "CondaError"
    assert "--force" in error["error"] and "status" in error["error"]
    assert "traceback" not in error
    assert target.is_symlink()
    removed = run_cli("unlink", "example", "--force", "--json")
    assert removed.returncode == 0, removed.stderr
    assert json.loads(removed.stdout) == {"name": "example", "removed": True}
    assert (prefix / "share/agent-skills/example/SKILL.md").is_file()


def test_unlink_home_requires_global(prefix: Path, tmp_path: Path, run_cli) -> None:
    linked = run_cli("link", "example", "-p", str(prefix), "--global", "--json")
    assert linked.returncode == 0, linked.stderr
    target = Path(json.loads(linked.stdout)["path"])
    refused = run_cli("unlink", "example", "--force", cwd=tmp_path / "home")
    assert refused.returncode != 0
    assert "--global" in refused.stderr
    assert target.is_symlink()
    removed = run_cli("unlink", "example", "--global", "--json")
    assert removed.returncode == 0, removed.stderr
    assert json.loads(removed.stdout) == {"name": "example", "removed": True}
