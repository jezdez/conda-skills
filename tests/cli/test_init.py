from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from conda.common.serialize import yaml
from conda.exceptions import CondaError
from conda.models.records import PrefixRecord

from conda_skill.skills import Skill


@pytest.mark.parametrize(
    "description",
    [
        "Useful guidance",
        'Quotes: "yes"; [bold]literal[/bold]',
        "line one\n---\nname: injected\nrun: bad",
        "controls: \x1b[31m\x00\r\t",
        "${{ invalid_template() }}",
        "x" * 1024,
    ],
)
def test_init_serializes_metadata_and_generates_buildable_layout(
    render_cli, tmp_path: Path, description: str
) -> None:
    result = json.loads(
        render_cli("init", "new-skill", "--description", description, "--json")
    )
    path = tmp_path / "new-skill"
    assert result == {
        "name": "new-skill",
        "path": str(path),
        "recipe": str(path / "recipe/recipe.yaml"),
    }
    record = PrefixRecord(
        name="agent-skill-new-skill", version="0.1.0", build="0", build_number=0
    )
    skill = Skill.from_directory(path, record, prefix=tmp_path)
    assert skill.description == description
    recipe = yaml.loads((path / "recipe/recipe.yaml").read_text(encoding="utf-8"))
    assert recipe["package"]["name"] == "agent-skill-new-skill"
    assert recipe["source"]["path"] == ".."
    assert recipe["build"]["noarch"] == "generic"
    assert recipe["tests"][0]["package_contents"]["strict"] is True
    assert "license" not in recipe.get("about", {})
    assert description not in recipe["about"]["summary"]
    destination = tmp_path / "build-prefix"
    build = subprocess.run(
        [sys.executable, str(path / "build.py")],
        env={**os.environ, "PREFIX": str(destination)},
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert build.returncode == 0, build.stderr
    assert (destination / "share/agent-skills/new-skill/SKILL.md").read_bytes() == (
        path / "SKILL.md"
    ).read_bytes()
    assert sorted(
        p.name for p in (destination / "share/agent-skills/new-skill").iterdir()
    ) == ["SKILL.md"]


@pytest.mark.parametrize(
    "name",
    [
        "../escape",
        "Upper",
        "a_b",
        "a--b",
        "a" * 65,
        "a\x1b",
        "con",
        "prn",
        "aux",
        "nul",
        "com1",
        "com9",
        "lpt1",
        "lpt9",
    ],
)
def test_init_rejects_invalid_names_without_writes(
    render_cli, tmp_path: Path, name: str
) -> None:
    before = set(tmp_path.iterdir())
    with pytest.raises(CondaError, match="Invalid skill directory name"):
        render_cli("init", name)
    assert set(tmp_path.iterdir()) == before


@pytest.mark.parametrize("description", ["", " \n\t", "x" * 1025])
def test_init_rejects_invalid_descriptions_without_writes(
    render_cli, tmp_path: Path, description: str
) -> None:
    with pytest.raises(CondaError, match="description"):
        render_cli("init", "new-skill", "--description", description)
    assert not (tmp_path / "new-skill").exists()


@pytest.mark.parametrize("kind", ["file", "directory", "symlink", "dangling"])
def test_init_preserves_existing_destination(
    render_cli, tmp_path: Path, kind: str
) -> None:
    target = tmp_path / "new-skill"
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "keep"
    marker.write_text("unchanged", encoding="utf-8")
    if kind == "file":
        target.write_text("unchanged", encoding="utf-8")
    elif kind == "directory":
        target.mkdir()
    else:
        target.symlink_to(
            outside if kind == "symlink" else tmp_path / "absent",
            target_is_directory=True,
        )
    with pytest.raises(CondaError):
        render_cli("init", "new-skill")
    assert marker.read_text(encoding="utf-8") == "unchanged"
    if kind == "file":
        assert target.read_text(encoding="utf-8") == "unchanged"
    elif kind == "directory":
        assert list(target.iterdir()) == []
    else:
        assert target.is_symlink()


def test_init_human_output_explains_placeholder_and_next_steps(
    render_cli, tmp_path: Path
) -> None:
    output = render_cli("init", "new-skill")
    assert str(tmp_path / "new-skill/SKILL.md") in output
    assert str(tmp_path / "new-skill/recipe/recipe.yaml") in output
    assert "placeholder" in output.lower()
    assert "rattler-build" in output
    assert "not installed" in output.lower()
    assert "Next steps" in output
    assert "license" in output
    assert "build.py packages SKILL.md only" in output


def test_init_home_requires_explicit_global(
    render_cli, tmp_path: Path, monkeypatch
) -> None:
    home = tmp_path / "home"
    monkeypatch.chdir(home)
    with pytest.raises(CondaError, match="--global"):
        render_cli("init", "new-skill")
    assert not (home / "new-skill").exists()
    result = json.loads(render_cli("init", "new-skill", "--global", "--json"))
    assert result["path"] == str(home / "new-skill")


def test_init_installed_json_uses_configured_json(run_cli, tmp_path: Path) -> None:
    result = run_cli("init", "new-skill", env={"CONDA_JSON": "true"})
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["path"] == str(tmp_path / "new-skill")
