from __future__ import annotations

import json
from pathlib import Path


def test_human_link_output(prefix: Path, render_cli) -> None:
    linked = render_cli("link", "example", "-p", str(prefix))
    assert "Linked example at " in linked


def test_installed_global_is_explicit_and_isolated(
    prefix: Path, tmp_path: Path, run_cli
) -> None:
    result = run_cli("link", "example", "-p", str(prefix), "--global", "--json")
    assert result.returncode == 0, result.stderr + result.stdout
    assert (
        Path(json.loads(result.stdout)["path"])
        == tmp_path / "home/.agents/skills/example"
    )
    assert not (tmp_path / ".agents").exists()


def test_installed_json_errors(prefix: Path, tmp_path: Path, run_cli) -> None:
    target = tmp_path / ".agents/skills/example"
    target.mkdir(parents=True)
    result = run_cli("link", "example", "-p", str(prefix), "--json")
    assert result.returncode != 0
    assert "Refusing" in json.loads(result.stdout)["error"]
    assert target.is_dir()
    result = run_cli("link", "absent", "-p", str(prefix), "--json")
    assert result.returncode != 0
    assert "No package-owned" in json.loads(result.stdout)["error"]


def test_home_mutation_requires_global(prefix: Path, tmp_path: Path, run_cli) -> None:
    home = tmp_path / "home"
    result = run_cli("link", "example", "-p", str(prefix), "--json", cwd=home)
    assert result.returncode != 0
    assert "--global" in json.loads(result.stdout)["error"]
    assert not (home / ".agents").exists()
