from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from conda.exceptions import CondaError
from rich.console import Console
from rich.text import Text

from conda_skill.cli import inspect as inspect_command


def test_inspect_metadata_and_sorted_tree(prefix: Path, render_cli) -> None:
    path = prefix / "share/agent-skills/example"
    (path / "scripts").mkdir()
    (path / "scripts/run.py").write_text("raise SystemExit(42)\n")
    (path / "assets").mkdir()
    (path / "assets/data.bin").write_bytes(b"\x00")
    (path / "ref-link").symlink_to("references", target_is_directory=True)
    payload = json.loads(render_cli("inspect", "example", "-p", str(prefix), "--json"))
    assert payload == {
        "name": "example",
        "description": "Example: useful guidance",
        "package": "agent-skill-example",
        "version": "1.0",
        "path": str(path),
        "files": [
            {"path": "SKILL.md", "type": "file"},
            {"path": "assets", "type": "directory"},
            {"path": "assets/data.bin", "type": "file"},
            {"path": "ref-link", "type": "symlink"},
            {"path": "references", "type": "directory"},
            {"path": "references/example.md", "type": "file"},
            {"path": "scripts", "type": "directory"},
            {"path": "scripts/run.py", "type": "file"},
        ],
    }
    output = render_cli("inspect", "example", "-p", str(prefix))
    for text in (
        "Name",
        "Description",
        "Package",
        "Version",
        "Path",
        "example",
        "Example: useful guidance",
        "1.0",
        str(path),
        "SKILL.md",
        "references",
        "example.md",
        "scripts",
        "run.py",
        "assets",
        "data.bin",
        "ref-link",
        "symlink",
    ):
        assert text in output


def test_inspect_file_keeps_literal_multiline_text(prefix: Path, render_cli) -> None:
    path = prefix / "share/agent-skills/example/references/example.md"
    content = "# Heading\r\n[bold]literal[/bold]\n\tindent\x1b[31m\x85last\n"
    path.write_bytes(content.encode("utf-8"))
    args = ("inspect", "example", "-p", str(prefix), "--file", "references/example.md")
    output = render_cli(*args)
    assert "# Heading\n[bold]literal[/bold]\n" in output
    assert r"\x09indent\x1b[31m\x85last" in output
    assert "\x1b" not in output
    payload = json.loads(render_cli(*args, "--json"))
    assert payload == {
        "name": "example",
        "description": "Example: useful guidance",
        "package": "agent-skill-example",
        "version": "1.0",
        "path": str(path.parent.parent),
        "file": "references/example.md",
        "kind": "text",
        "content": content,
    }


@pytest.mark.parametrize("content", [b"\x00data", b"\xffdata"])
def test_inspect_binary_is_not_displayed(
    prefix: Path, render_cli, content: bytes
) -> None:
    (prefix / "share/agent-skills/example/binary").write_bytes(content)
    args = ("inspect", "example", "-p", str(prefix), "--file", "binary")
    assert "Binary file: binary (not displayed)." in render_cli(*args)
    payload = json.loads(render_cli(*args, "--json"))
    assert payload["kind"] == "binary"
    assert payload["content"] is None


def test_inspect_metadata_and_filenames_are_literal(prefix: Path, render_cli) -> None:
    path = prefix / "share/agent-skills/example"
    description = "[bold]literal[/bold]\x1b[31m\nnext"
    (path / "SKILL.md").write_text(
        f"---\nname: example\ndescription: {json.dumps(description)}\n---\n"
    )
    name = "[bold]literal[/bold]".replace("/", "-")
    (path / name).touch()
    output = render_cli("inspect", "example", "-p", str(prefix))
    assert r"[bold]literal[/bold]\x1b[31m\x0anext" in output
    assert name in output
    assert "\x1b" not in output


@pytest.mark.parametrize(
    "file,message",
    [
        ("missing", "missing"),
        ("../SKILL.md", "skill-relative"),
        ("references", "regular file"),
        ("large", "1 MiB"),
    ],
)
def test_inspect_errors_use_conda_handler(
    prefix: Path, run_cli, file: str, message: str
) -> None:
    (prefix / "share/agent-skills/example/large").write_bytes(b"x" * (1024 * 1024 + 1))
    result = run_cli("inspect", "example", "-p", str(prefix), "--file", file, "--json")
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["exception_name"] == "CondaError"
    assert message in payload["error"]
    assert "traceback" not in payload


@pytest.mark.skipif(os.name == "nt", reason="POSIX file permissions required")
def test_inspect_permission_error_uses_conda_handler(prefix: Path, render_cli) -> None:
    path = prefix / "share/agent-skills/example/references/example.md"
    path.chmod(0)
    try:
        if os.access(path, os.R_OK):
            pytest.skip("User can read files despite mode 000")
        with pytest.raises(CondaError, match="Permission denied"):
            render_cli(
                "inspect",
                "example",
                "-p",
                str(prefix),
                "--file",
                "references/example.md",
            )
    finally:
        path.chmod(0o600)


@pytest.mark.skipif(
    os.name == "nt", reason="Windows disallows control characters in filenames"
)
def test_inspect_escapes_filename_controls(prefix: Path, render_cli) -> None:
    name = "literal\x1b[31m\tname"
    (prefix / "share/agent-skills/example" / name).touch()
    output = render_cli("inspect", "example", "-p", str(prefix))
    assert r"literal\x1b[31m\x09name" in output
    assert "\x1b" not in output


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFOs require POSIX")
def test_inspect_labels_special_entries_without_reading(
    prefix: Path, render_cli
) -> None:
    os.mkfifo(prefix / "share/agent-skills/example/pipe")
    output = render_cli("inspect", "example", "-p", str(prefix))
    assert "pipe (special)" in output
    with pytest.raises(CondaError, match="regular file"):
        render_cli("inspect", "example", "-p", str(prefix), "--file", "pipe")


@pytest.mark.parametrize("content", ["", "no final newline"])
def test_inspect_text_without_trailing_newline(
    prefix: Path, render_cli, content: str
) -> None:
    (prefix / "share/agent-skills/example/text").write_text(content)
    output = render_cli("inspect", "example", "-p", str(prefix), "--file", "text")
    assert output == content + "\n"


def test_inspect_nonterminal_skips_syntax_highlighting(
    prefix: Path, render_cli, monkeypatch
) -> None:
    content = "# Review\r\n" + "long line " * 100 + "\n\ttext\x1b[31m"
    (prefix / "share/agent-skills/example/review.md").write_bytes(
        content.encode("utf-8")
    )

    def plain_console(**kwargs):
        return Console(**kwargs, force_terminal=False, width=40)

    def unexpected_lexer(*args, **kwargs):
        pytest.fail("Nonterminal output must not invoke syntax highlighting")

    monkeypatch.setattr(inspect_command, "Console", plain_console)
    monkeypatch.setattr(inspect_command.Syntax, "guess_lexer", unexpected_lexer)
    output = render_cli("inspect", "example", "-p", str(prefix), "--file", "review.md")
    assert output == "# Review\n" + "long line " * 100 + "\n\\x09text\\x1b[31m\n"
    payload = json.loads(
        render_cli(
            "inspect", "example", "-p", str(prefix), "--file", "review.md", "--json"
        )
    )
    assert payload["content"] == content


@pytest.mark.parametrize(
    "filename,content",
    [
        (
            "review.md",
            "# Review\n<!-- keep this visible -->\n[guide](https://example.com)\n",
        ),
        (
            "example.py",
            "# Show source, never execute it\nraise RuntimeError('not executed')\n",
        ),
        ("unknown.extension", "Plain text without a recognized extension\n"),
    ],
)
def test_inspect_highlights_source_without_hiding_syntax(
    prefix: Path, render_cli, monkeypatch, filename: str, content: str
) -> None:
    (prefix / "share/agent-skills/example" / filename).write_text(
        content, encoding="utf-8", newline="\n"
    )

    def terminal_console(**kwargs):
        return Console(
            **kwargs, force_terminal=True, color_system="standard", no_color=False
        )

    monkeypatch.setattr(inspect_command, "Console", terminal_console)
    output = render_cli("inspect", "example", "-p", str(prefix), "--file", filename)
    assert Text.from_ansi(output).plain == content
    if filename.endswith((".md", ".py")):
        assert "\x1b[" in output
    payload = json.loads(
        render_cli(
            "inspect", "example", "-p", str(prefix), "--file", filename, "--json"
        )
    )
    assert payload["content"] == content
