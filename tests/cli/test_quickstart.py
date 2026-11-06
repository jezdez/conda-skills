from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from conda.exceptions import CondaError


@pytest.fixture
def interactive(render_cli, monkeypatch):
    """Supply terminal input while exercising real dispatch and filesystem writes."""
    monkeypatch.setattr(type(sys.stdin), "isatty", lambda self: True)
    monkeypatch.setattr(type(sys.stdout), "isatty", lambda self: True)

    def run(answers: list[str], *args: str) -> str:
        replies = iter(answers)

        def read(prompt: str = "") -> str:
            try:
                return next(replies)
            except StopIteration:
                raise EOFError from None

        monkeypatch.setattr("builtins.input", read)
        return render_cli("quickstart", *args)

    return run


def test_quickstart_noninteractive_fails_cleanly(run_cli, tmp_path: Path) -> None:
    result = run_cli("quickstart")
    assert result.returncode != 0
    assert "interactive terminal" in result.stderr
    assert "init" in result.stderr and "install" in result.stderr
    assert not (tmp_path / ".agents").exists()


@pytest.mark.parametrize("configured", [True, False])
def test_quickstart_rejects_json_before_prompting(run_cli, configured: bool) -> None:
    result = run_cli(
        "quickstart",
        *([] if configured else ["--json"]),
        env={"CONDA_JSON": str(configured).lower()},
    )
    assert result.returncode != 0
    assert "JSON" in json.loads(result.stdout)["message"]
    assert "Choose" not in result.stdout


@pytest.mark.parametrize("stream", ["stdin", "stdout"])
def test_quickstart_requires_both_streams_to_be_terminals(
    interactive, monkeypatch, stream: str
) -> None:
    monkeypatch.setattr(type(getattr(sys, stream)), "isatty", lambda self: False)
    with pytest.raises(CondaError, match="interactive terminal"):
        interactive([])


@pytest.mark.parametrize("backend", ["agents", "claude"])
def test_quickstart_links_reviewed_package_skill(
    interactive, prefix: Path, tmp_path: Path, backend: str
) -> None:
    output = interactive(["link", "1", backend, "project", "y"], "-p", str(prefix))
    target = tmp_path / f".{backend}/skills/example"
    assert target.is_symlink()
    assert target.resolve() == prefix / "share/agent-skills/example"
    assert str(prefix / "share/agent-skills/example") in output.replace("\n", "")
    assert "Example: useful guidance" in output
    assert "Review" in output and "trust" in output


@pytest.mark.parametrize("confirmation", ["n", ""])
def test_quickstart_link_cancellation_has_no_effects(
    interactive, prefix: Path, tmp_path: Path, confirmation: str
) -> None:
    interactive(["link", "1", "agents", "project", confirmation], "-p", str(prefix))
    assert not (tmp_path / ".agents").exists()


def test_quickstart_new_skill_uses_init_without_source_lookup(
    interactive, tmp_path: Path
) -> None:
    output = interactive(
        ["new", "new-skill", "Useful guidance", "project", "y"],
        "-p",
        str(tmp_path / "missing-env"),
    )
    assert (tmp_path / "new-skill/SKILL.md").is_file()
    assert (tmp_path / "new-skill/recipe/recipe.yaml").is_file()
    assert "not installed" in output.lower()
    assert not (tmp_path / "missing-env").exists()
    assert not (tmp_path / ".agents").exists()


@pytest.mark.parametrize(
    "answers", [["cancel"], [], ["new", "new-skill", "Useful", "project", "n"]]
)
def test_quickstart_new_cancellation_has_no_effects(
    interactive, tmp_path: Path, answers: list[str]
) -> None:
    before = set(tmp_path.iterdir())
    assert "Cancelled" in interactive(answers)
    assert set(tmp_path.iterdir()) == before


def test_quickstart_home_requires_global(
    interactive, prefix: Path, tmp_path: Path
) -> None:
    with pytest.raises(CondaError, match="--global"):
        interactive(["link", "1", "agents", "home", "y"], "-p", str(prefix))
    assert not (tmp_path / "home/.agents").exists()


def test_quickstart_explicit_home_link(
    interactive, prefix: Path, tmp_path: Path
) -> None:
    interactive(["link", "1", "agents", "home", "y"], "-p", str(prefix), "--global")
    assert (tmp_path / "home/.agents/skills/example").is_symlink()


def test_quickstart_refuses_project_at_home(
    interactive, prefix: Path, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path / "home")
    with pytest.raises(CondaError, match="--global"):
        interactive(["link", "1", "agents", "project", "y"], "-p", str(prefix))
    assert not (tmp_path / "home/.agents").exists()


def test_quickstart_empty_environment_makes_no_changes(
    interactive, tmp_path: Path
) -> None:
    prefix = tmp_path / "empty"
    (prefix / "conda-meta").mkdir(parents=True)
    (prefix / "conda-meta/history").touch()
    before = set(tmp_path.iterdir())
    output = interactive(["link"], "-p", str(prefix))
    assert "No package-owned skills found" in output
    assert set(tmp_path.iterdir()) == before


def test_quickstart_missing_environment_is_not_created(
    interactive, tmp_path: Path
) -> None:
    prefix = tmp_path / "missing"
    with pytest.raises(CondaError):
        interactive(["link"], "-p", str(prefix))
    assert not prefix.exists()


def test_quickstart_description_preview_is_literal(interactive, tmp_path: Path) -> None:
    description = "[bold]literal[/bold]\x1b[31m"
    output = interactive(["new", "new-skill", description, "project", "n"])
    assert "[bold]literal[/bold]" in output
    assert "\\x1b[31m" in output
    assert "\x1b[31m" not in output
    assert not (tmp_path / "new-skill").exists()
