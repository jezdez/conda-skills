from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from conda_skill.links import install, remove, status
from conda_skill.skills import Skill


@pytest.fixture
def skill(tmp_path: Path) -> Skill:
    path = tmp_path / "source/example"
    (path / "references").mkdir(parents=True)
    (path / "SKILL.md").write_text("# Example\n", encoding="utf-8")
    (path / "references/example.md").write_text("# Reference\n", encoding="utf-8")
    return Skill("example", "Example guidance", path, "agent-skill-example", "1.0")


def test_link_roundtrip(skill: Skill, tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    target = install(skill, root, "agents")
    assert target.is_symlink()
    assert not Path(target.readlink()).is_absolute()
    assert (target / "references/example.md").read_text() == "# Reference\n"
    assert install(skill, root, "agents") == target
    assert status(root, "agents")[0]["state"] == "linked"
    assert remove(skill, root, "agents")
    assert not remove(skill, root, "agents")
    assert skill.path.is_dir()


@pytest.mark.parametrize("kind", ["directory", "file", "foreign", "broken"])
def test_conflicts_are_preserved(skill: Skill, tmp_path: Path, kind: str) -> None:
    target = tmp_path / ".agents/skills/example"
    target.parent.mkdir(parents=True)
    if kind == "directory":
        target.mkdir()
    elif kind == "file":
        target.write_text("keep", encoding="utf-8")
    else:
        foreign = tmp_path / "foreign"
        if kind == "foreign":
            foreign.mkdir()
        target.symlink_to(foreign, target_is_directory=True)
    for operation in (install, remove):
        with pytest.raises(ValueError, match="Refusing"):
            operation(skill, tmp_path, "agents")
    assert target.exists() or target.is_symlink()


@pytest.mark.parametrize("redirect", [".agents", ".agents/skills"])
@pytest.mark.parametrize("operation", [install, remove], ids=["install", "remove"])
def test_redirected_destination_is_rejected(
    skill: Skill,
    tmp_path: Path,
    redirect: str,
    operation: Callable[[Skill, Path, str], Path | bool],
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    redirected = project / redirect
    redirected.parent.mkdir(parents=True, exist_ok=True)
    redirected.symlink_to(outside, target_is_directory=True)
    target = (outside / "skills" if redirect == ".agents" else outside) / skill.name
    if operation is remove:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(skill.path, target_is_directory=True)
    with pytest.raises(ValueError, match="Refusing redirected client directory"):
        operation(skill, project, "agents")
    assert redirected.is_symlink()
    if operation is remove:
        assert target.is_symlink()
        assert target.readlink() == skill.path
        assert (target / "SKILL.md").read_text() == "# Example\n"
    else:
        assert list(outside.iterdir()) == []


@pytest.mark.parametrize("kind", ["missing", "directory", "file"])
def test_status_reports_broken_links(tmp_path: Path, kind: str) -> None:
    source = tmp_path / "source"
    if kind == "directory":
        source.mkdir()
    elif kind == "file":
        source.write_text("not a skill directory", encoding="utf-8")
    target = tmp_path / ".agents/skills/example"
    target.parent.mkdir(parents=True)
    target.symlink_to(source, target_is_directory=kind != "file")

    assert status(tmp_path, "agents") == [
        {
            "name": "example",
            "state": "broken",
            "path": str(target),
            "target": str(source.resolve()),
        }
    ]
    assert target.is_symlink()
