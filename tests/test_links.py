from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import conda_skill.links as links
from conda_skill.links import link, status, unlink
from conda_skill.skills import Skill, discover


@pytest.fixture
def skill(prefix: Path) -> Skill:
    path = prefix / "share/agent-skills/example"
    return Skill("example", "Example guidance", path, "agent-skill-example", "1.0")


def test_link_roundtrip(skill: Skill, tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    target = link(skill, root, "agents")
    assert target.is_symlink()
    assert not Path(target.readlink()).is_absolute()
    assert (target / "references/example.md").read_text() == "# Reference\n"
    assert link(skill, root, "agents") == target
    assert status(root, "agents")[0]["state"] == "linked"
    original = {
        path: path.read_bytes() for path in skill.path.rglob("*") if path.is_file()
    }
    assert unlink(skill.name, root, "agents")
    assert not unlink(skill.name, root, "agents")
    assert all(path.read_bytes() == content for path, content in original.items())
    assert skill.path.is_dir()


@pytest.mark.parametrize("component", ["example", "agent-skills"])
def test_unlink_verifies_internal_source_alias(
    prefix: Path, tmp_path: Path, component: str
) -> None:
    recorded = prefix / "share/agent-skills"
    if component == "example":
        recorded /= "example"
    relocated = prefix / "skill-data"
    recorded.rename(relocated)
    recorded.symlink_to(relocated, target_is_directory=True)
    [skill] = discover(prefix)
    target = link(skill, tmp_path, "agents")
    assert target.is_dir()
    assert unlink(skill.name, tmp_path, "agents")
    assert not target.is_symlink()
    assert relocated.is_dir()


def test_unlink_preserves_parent_traversal_after_source_alias(
    prefix: Path, tmp_path: Path
) -> None:
    (prefix / "subdir").mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(prefix / "subdir", target_is_directory=True)
    target = tmp_path / ".agents/skills/example"
    target.parent.mkdir(parents=True)
    target.symlink_to(alias / "../share/agent-skills/example", target_is_directory=True)
    assert target.resolve() == prefix / "share/agent-skills/example"
    assert unlink("example", tmp_path, "agents")
    assert (prefix / "share/agent-skills/example/SKILL.md").is_file()


@pytest.mark.parametrize("kind", ["directory", "file", "foreign", "broken", "cycle"])
def test_conflicts_are_preserved(skill: Skill, tmp_path: Path, kind: str) -> None:
    target = tmp_path / ".agents/skills/example"
    target.parent.mkdir(parents=True)
    if kind == "directory":
        target.mkdir()
    elif kind == "file":
        target.write_text("keep", encoding="utf-8")
    elif kind == "cycle":
        target.symlink_to(target.name, target_is_directory=True)
    else:
        foreign = tmp_path / "foreign"
        if kind == "foreign":
            foreign.mkdir()
        target.symlink_to(foreign, target_is_directory=True)
    with pytest.raises(ValueError, match="Refusing"):
        link(skill, tmp_path, "agents")
    with pytest.raises(ValueError, match="Refusing"):
        unlink(skill.name, tmp_path, "agents")
    assert target.exists() or target.is_symlink()
    if kind in {"directory", "file"}:
        with pytest.raises(ValueError, match="Refusing"):
            unlink(skill.name, tmp_path, "agents", force=True)
        assert target.exists()
    else:
        assert unlink(skill.name, tmp_path, "agents", force=True)
        assert not target.is_symlink()
        if kind == "foreign":
            assert foreign.is_dir()


@pytest.mark.parametrize("redirect", [".agents", ".agents/skills"])
@pytest.mark.parametrize("operation", ["link", "unlink", "force-unlink"])
def test_redirected_destination_is_rejected(
    skill: Skill,
    tmp_path: Path,
    redirect: str,
    operation: str,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    redirected = project / redirect
    redirected.parent.mkdir(parents=True, exist_ok=True)
    redirected.symlink_to(outside, target_is_directory=True)
    target = (outside / "skills" if redirect == ".agents" else outside) / skill.name
    if operation != "link":
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(skill.path, target_is_directory=True)
        original_target = target.readlink()
    with pytest.raises(ValueError, match="Refusing redirected client directory"):
        if operation == "link":
            link(skill, project, "agents")
        else:
            unlink(skill.name, project, "agents", force=operation == "force-unlink")
    assert redirected.is_symlink()
    if operation != "link":
        assert target.is_symlink()
        assert target.readlink() == original_target
        assert (target / "SKILL.md").read_text() == (
            skill.path / "SKILL.md"
        ).read_text()
    else:
        assert list(outside.iterdir()) == []


@pytest.mark.parametrize("force", [False, True])
@pytest.mark.parametrize(
    "name",
    ["../example", "a/b", r"a\b", "/example", "", ".", "..", "con", "A", "a" * 65],
)
def test_unlink_rejects_unsafe_names(tmp_path: Path, name: str, force: bool) -> None:
    with pytest.raises(ValueError, match="Invalid skill directory name"):
        unlink(name, tmp_path, "agents", force=force)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "failure",
    [
        "removed-env",
        "missing-record",
        "duplicate-owner",
        "invalid-header",
        "invalid-record",
        "wrong-name",
        "escaping-file",
    ],
)
def test_unlink_requires_verified_package_target(
    prefix: Path, skill: Skill, tmp_path: Path, failure: str
) -> None:
    target = link(skill, tmp_path, "agents")
    record = prefix / "conda-meta/agent-skill-example-1.0-0.json"
    if failure == "removed-env":
        shutil.rmtree(prefix)
    elif failure == "missing-record":
        record.unlink()
    elif failure == "duplicate-owner":
        data = json.loads(record.read_text())
        data["name"] = "other-package"
        (record.parent / "other-package-1.0-0.json").write_text(json.dumps(data))
    elif failure == "invalid-header":
        (skill.path / "SKILL.md").write_text("not frontmatter")
    elif failure == "invalid-record":
        record.write_text("invalid json")
    elif failure == "wrong-name":
        target.rename(target.with_name("other"))
        target = target.with_name("other")
    else:
        (skill.path / "escape").symlink_to(tmp_path, target_is_directory=True)
    original = target.readlink()
    with pytest.raises(ValueError, match="--force") as error:
        unlink(target.name, tmp_path, "agents")
    assert "status" in str(error.value)
    assert target.readlink() == original
    assert unlink(target.name, tmp_path, "agents", force=True)
    assert not target.is_symlink()
    if failure != "removed-env":
        assert skill.path.is_dir()


def test_unlink_absent_does_not_create_destination(tmp_path: Path) -> None:
    assert not unlink("example", tmp_path, "agents")
    assert not (tmp_path / ".agents").exists()


@pytest.mark.parametrize("replacement", ["symlink", "file", "redirected-parent"])
def test_unlink_refuses_destination_changed_during_verification(
    skill: Skill, tmp_path: Path, monkeypatch, replacement: str
) -> None:
    target = link(skill, tmp_path, "agents")

    def discover_then_replace(prefix: Path) -> list[Skill]:
        skills = discover(prefix)
        if replacement == "redirected-parent":
            directory = target.parent
            moved = tmp_path / "moved-skills"
            directory.rename(moved)
            directory.symlink_to(moved, target_is_directory=True)
        else:
            target.rename(target.with_name("original"))
            if replacement == "symlink":
                target.symlink_to(skill.path, target_is_directory=True)
            else:
                target.write_text("keep", encoding="utf-8")
        return skills

    monkeypatch.setattr(links, "discover", discover_then_replace)
    with pytest.raises(ValueError, match="Refusing"):
        unlink(skill.name, tmp_path, "agents")
    if replacement == "file":
        assert target.read_text() == "keep"
    else:
        assert target.is_symlink()
    assert (skill.path / "SKILL.md").is_file()


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


@pytest.mark.parametrize("mutual", [False, True], ids=["self", "mutual"])
def test_status_preserves_cyclic_links(tmp_path: Path, mutual: bool) -> None:
    directory = tmp_path / ".agents/skills"
    directory.mkdir(parents=True)
    (directory / "loop").symlink_to(
        "other" if mutual else "loop", target_is_directory=True
    )
    if mutual:
        (directory / "other").symlink_to("loop", target_is_directory=True)
    (directory / "unmanaged").mkdir()
    entries = {entry["name"]: entry for entry in status(tmp_path, "agents")}
    for name in ("loop", "other") if mutual else ("loop",):
        assert entries[name]["state"] == "broken"
        assert entries[name]["target"] == str((directory / name).readlink())
        assert (directory / name).is_symlink()
    assert entries["unmanaged"]["state"] == "unmanaged"


def test_status_preserves_cycle_after_missing_component(tmp_path: Path) -> None:
    directory = tmp_path / ".agents/skills"
    directory.mkdir(parents=True)
    (directory / "loop").symlink_to("loop", target_is_directory=True)
    entry = directory / "entry"
    entry.symlink_to("missing/../loop", target_is_directory=True)
    entries = {entry["name"]: entry for entry in status(tmp_path, "agents")}
    assert entries["entry"]["state"] == "broken"
    assert entries["entry"]["target"] in {
        str(entry.readlink()),
        str(directory / "loop"),
    }
    assert entries["loop"]["state"] == "broken"
