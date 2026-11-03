from __future__ import annotations

import json
from pathlib import Path


def test_human_list_output(prefix: Path, render_cli) -> None:
    listed = render_cli("list", "-p", str(prefix))
    for text in ("Name", "Package", "Version", "Description", "Path", "example"):
        assert text in listed


def test_empty_list_output(prefix: Path, render_cli) -> None:
    (prefix / "conda-meta/agent-skill-example-1.0-0.json").unlink()
    result = render_cli("list", "-p", str(prefix))
    assert "No package-owned skills found." in result
    assert json.loads(render_cli("list", "-p", str(prefix), "--json")) == []


def test_package_text_is_literal_and_json_is_unchanged(
    prefix: Path, render_cli
) -> None:
    description = "[bold]literal[/bold]\x1b[31m\nnext\x85line"
    (prefix / "share/agent-skills/example/SKILL.md").write_text(
        f"---\nname: example\ndescription: {json.dumps(description)}\n---\n",
        encoding="utf-8",
    )
    result = render_cli("list", "-p", str(prefix))
    assert r"[bold]literal[/bold]\x1b[31m\x0anext\x85line" in result
    assert "\x1b" not in result
    structured = render_cli("list", "-p", str(prefix), "--json")
    assert json.loads(structured)[0]["description"] == description
