from __future__ import annotations

import runpy
import shutil
import sys
from pathlib import Path

import pytest


@pytest.fixture
def release_tree(tmp_path: Path) -> Path:
    """Create a release fixture independent of the checkout's unreleased notes."""
    (tmp_path / "scripts").mkdir()
    script = tmp_path / "scripts/check_release.py"
    shutil.copyfile(Path(__file__).parents[1] / "scripts/check_release.py", script)
    (tmp_path / "recipe").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion = "0.1.0"\n', encoding="utf-8"
    )
    (tmp_path / "recipe/recipe.yaml").write_text(
        'context:\n  version: "0.1.0"\n', encoding="utf-8"
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 0.1.0 - 2026-11-06\n\nInitial release.\n", encoding="utf-8"
    )
    return script


@pytest.mark.parametrize("version", ["0.2.0", "v0.1.0"])
def test_release_version_must_match(
    release_tree: Path, monkeypatch, version: str
) -> None:
    monkeypatch.setattr(sys, "argv", [str(release_tree), version])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2


def test_release_requires_dated_notes(release_tree: Path, monkeypatch) -> None:
    (release_tree.parents[1] / "CHANGELOG.md").write_text(
        "# Changelog\n\n## Unreleased\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2


def test_release_metadata_matches(release_tree: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    runpy.run_path(str(release_tree), run_name="__main__")
    assert "nothing was published" in capsys.readouterr().out


def test_release_recipe_version_must_match(release_tree: Path, monkeypatch) -> None:
    (release_tree.parents[1] / "recipe/recipe.yaml").write_text(
        'context:\n  version: "0.2.0"\n', encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2


def test_release_rejects_placeholder_date(release_tree: Path, monkeypatch) -> None:
    (release_tree.parents[1] / "CHANGELOG.md").write_text(
        "## 0.1.0 - YYYY-MM-DD\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2
