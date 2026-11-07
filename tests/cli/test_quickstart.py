from __future__ import annotations

import json
import os
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


@pytest.fixture
def batch_prefix(prefix: Path) -> Path:
    """Add two package-owned skills to the selected source environment."""
    record_path = prefix / "conda-meta/agent-skill-example-1.0-0.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    for name in ("second", "spare"):
        skill = prefix / "share/agent-skills" / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Guidance for {name}\n---\n",
            encoding="utf-8",
        )
        record["files"].append(f"share/agent-skills/{name}/SKILL.md")
    record_path.write_text(json.dumps(record), encoding="utf-8")
    return prefix


@pytest.mark.parametrize("choice", ["1 2", "1,2", "1, 2 1,2", "all"])
def test_quickstart_links_selected_batch(
    interactive, batch_prefix: Path, tmp_path: Path, choice: str
) -> None:
    output = interactive(["link", choice, "", "project", "y"], "-p", str(batch_prefix))
    names = ("example", "second", "spare") if choice == "all" else ("example", "second")
    directory = tmp_path / ".agents/skills"
    assert {path.name for path in directory.iterdir()} == set(names)
    for name in names:
        source = batch_prefix / "share/agent-skills" / name
        assert (directory / name).resolve() == source
        assert str(source) in output.replace("\n", "")
        assert (
            output.replace("\n", "").count(f"Link destination: {directory / name}") == 1
        )
    assert output.count("Example: useful guidance") == 2
    assert output.count("Guidance for second") == 2
    assert output.index("Guidance for spare") < output.index("Review source:")


@pytest.mark.parametrize("invalid", ["", "0", "-1", "4", "1 nope", "1 4", "all 1", ","])
def test_quickstart_invalid_selection_retries_without_partial_selection(
    interactive, batch_prefix: Path, tmp_path: Path, invalid: str
) -> None:
    output = interactive(
        ["link", invalid, "2", "agents", "project", "y"], "-p", str(batch_prefix)
    )
    assert "Invalid selection" in output
    assert {path.name for path in (tmp_path / ".agents/skills").iterdir()} == {"second"}


@pytest.mark.parametrize(
    "answers", [["link", "cancel"], ["link", "all", "agents", "project", "n"]]
)
def test_quickstart_batch_cancellation_has_no_effects(
    interactive, batch_prefix: Path, tmp_path: Path, answers: list[str]
) -> None:
    output = interactive(answers, "-p", str(batch_prefix))
    assert "Cancelled" in output
    assert "Invalid selection" not in output
    assert not (tmp_path / ".agents").exists()


@pytest.mark.parametrize(
    "conflict", ["file", "directory", "dangling", "unrelated", "cycle"]
)
def test_quickstart_preflights_second_destination_before_confirmation(
    interactive, batch_prefix: Path, tmp_path: Path, monkeypatch, conflict: str
) -> None:
    target = tmp_path / ".agents/skills/second"
    target.parent.mkdir(parents=True)
    if conflict == "file":
        target.write_text("keep", encoding="utf-8")
    elif conflict == "directory":
        target.mkdir()
    else:
        source = {
            "dangling": tmp_path / "missing",
            "unrelated": batch_prefix / "share/agent-skills/spare",
            "cycle": target,
        }[conflict]
        target.symlink_to(source, target_is_directory=True)

    def confirm(*args, **kwargs):
        pytest.fail("Conflicting batches must be rejected before confirmation")

    monkeypatch.setattr("conda_skill.cli.quickstart.Confirm.ask", confirm)
    with pytest.raises(CondaError, match="Refusing to replace existing destination"):
        interactive(["link", "1 2", "agents", "project", "y"], "-p", str(batch_prefix))
    assert not os.path.lexists(target.parent / "example")
    assert os.path.lexists(target)


@pytest.mark.parametrize("redirect", [".agents", ".agents/skills"])
def test_quickstart_preflights_redirected_client_directory(
    interactive, batch_prefix: Path, tmp_path: Path, redirect: str
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    target = tmp_path / redirect
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(outside, target_is_directory=True)
    with pytest.raises(CondaError, match="redirected client directory"):
        interactive(["link", "all", "agents", "project", "y"], "-p", str(batch_prefix))
    assert not list(outside.iterdir())


def test_quickstart_reuses_matching_and_preserves_unselected_links(
    interactive, batch_prefix: Path, tmp_path: Path
) -> None:
    directory = tmp_path / ".agents/skills"
    directory.mkdir(parents=True)
    for name in ("example", "spare"):
        (directory / name).symlink_to(
            batch_prefix / "share/agent-skills" / name, target_is_directory=True
        )
    original = (directory / "example").lstat().st_ino
    original_target = (directory / "example").readlink()
    interactive(["link", "1 2", "agents", "project", "y"], "-p", str(batch_prefix))
    assert (directory / "example").lstat().st_ino == original
    assert (directory / "example").readlink() == original_target
    for name in ("example", "second", "spare"):
        assert (
            directory / name
        ).resolve() == batch_prefix / "share/agent-skills" / name


def test_quickstart_batch_reviews_before_writes(
    interactive, batch_prefix: Path, tmp_path: Path, monkeypatch, capsys
) -> None:
    def confirm(*args, **kwargs):
        output = capsys.readouterr().out.replace("\n", "")
        assert not (tmp_path / ".agents").exists()
        for name, description in (
            ("example", "Example: useful guidance"),
            ("second", "Guidance for second"),
        ):
            assert f"Name: {name}" in output
            assert (
                f"Review source: {batch_prefix / 'share/agent-skills' / name}" in output
            )
            assert f"Description: {description}" in output
        return True

    monkeypatch.setattr("conda_skill.cli.quickstart.Confirm.ask", confirm)
    interactive(["link", "1 2", "agents", "project"], "-p", str(batch_prefix))
    assert (tmp_path / ".agents/skills/second").is_symlink()


@pytest.mark.skipif(
    os.name == "nt", reason="Windows paths cannot contain escape characters"
)
def test_quickstart_installed_source_preview_is_literal(
    interactive, batch_prefix: Path, tmp_path: Path
) -> None:
    source = batch_prefix.rename(tmp_path / "[bold]env\x1b[31m")
    skill_file = source / "share/agent-skills/second/SKILL.md"
    skill_file.write_text(
        '---\nname: second\ndescription: "[bold]literal[/bold]\\e[31m"\n---\n',
        encoding="utf-8",
    )
    output = interactive(["link", "all", "agents", "project", "n"], "-p", str(source))
    assert "[bold]env\\x1b[31m" in output
    assert "[bold]literal[/bold]\\x1b[31m" in output
    assert "\x1b[31m" not in output
    assert not (tmp_path / ".agents").exists()


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
    assert output.index("New skill") < output.index("Destination")
    assert output.index("Destination") < output.index("Review changes")
    assert output.index("Review changes") < output.index("Next steps")
    assert "install packages or create environments" in output
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
    interactive, batch_prefix: Path, tmp_path: Path
) -> None:
    with pytest.raises(CondaError, match="--global"):
        interactive(["link", "all", "agents", "home", "y"], "-p", str(batch_prefix))
    assert not (tmp_path / "home/.agents").exists()


def test_quickstart_explicit_home_link(
    interactive, batch_prefix: Path, tmp_path: Path
) -> None:
    interactive(
        ["link", "all", "agents", "home", "y"], "-p", str(batch_prefix), "--global"
    )
    for name in ("example", "second", "spare"):
        assert (tmp_path / "home/.agents/skills" / name).is_symlink()


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
