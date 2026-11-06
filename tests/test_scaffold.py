from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from conda_skill.skills import Skill


def test_skill_is_immutable(tmp_path: Path) -> None:
    skill = Skill("example", "Example instructions", tmp_path, "example-package", "1.0")
    with pytest.raises(FrozenInstanceError):
        skill.name = "changed"


@pytest.mark.parametrize(
    "name,description",
    [("../outside", "Instructions"), ("con", "Instructions"), ("example", " ")],
)
def test_skeleton_validates_before_writing(
    name: str, description: str, tmp_path: Path
) -> None:
    with pytest.raises(ValueError):
        Skill.create_skeleton(name, description, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_create_skeleton_returns_path(tmp_path: Path) -> None:
    path = Skill.create_skeleton("example", "Example instructions", tmp_path)
    assert path == tmp_path / "example"
    assert (tmp_path / "example/SKILL.md").is_file()


@pytest.mark.parametrize("skeleton", [True, False])
@pytest.mark.parametrize(
    "name,description",
    [
        ("../outside", "Instructions"),
        ("nul", "Instructions"),
        ("example", ""),
        ("example", "x" * 1025),
        ("example", None),
        ("example", 42),
    ],
)
def test_loading_and_authoring_share_metadata_validation(
    skeleton, name, description, tmp_path: Path
) -> None:
    with pytest.raises(ValueError):
        if skeleton:
            Skill.create_skeleton(name, description, tmp_path)
        else:
            Skill(name, description, tmp_path, "example-package", "1.0")
    assert list(tmp_path.iterdir()) == []
