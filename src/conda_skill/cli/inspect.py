from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from conda.base.context import context
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree

from .output import escape_terminal_controls, print_table

if TYPE_CHECKING:
    from ..skills import Skill


def execute(skill: Skill, file: str | None = None) -> None:
    """Show installed metadata and files, or one bounded file without executing it."""
    metadata = {**asdict(skill), "path": str(skill.path)}
    console = Console(markup=False, highlight=False)
    if file is not None:
        content = skill.read_file(file)
        if context.json:
            print(
                json.dumps(
                    {
                        **metadata,
                        "file": file,
                        "kind": "binary" if content is None else "text",
                        "content": content,
                    },
                    ensure_ascii=True,
                )
            )
        elif content is None:
            console.print(
                Text(f"Binary file: {escape_terminal_controls(file)} (not displayed).")
            )
        else:
            text = "\n".join(
                escape_terminal_controls(line)
                for line in content.replace("\r\n", "\n").split("\n")
            )
            if not text.endswith("\n"):
                text += "\n"
            preview = Text(text)
            if console.is_terminal:
                highlighted = Syntax(
                    text, Syntax.guess_lexer(file), theme="ansi_dark"
                ).highlight(text)
                # Some lexers normalize their input. Never hide inspected source.
                if highlighted.plain == text:
                    preview = highlighted
            console.print(preview, soft_wrap=True, end="")
        return

    files = skill.files()
    if context.json:
        print(
            json.dumps(
                {
                    **metadata,
                    "files": [{"path": path, "type": kind} for path, kind in files],
                },
                ensure_ascii=True,
            )
        )
        return
    print_table(
        ("Field", "Value"),
        ((key.capitalize(), value) for key, value in metadata.items()),
    )
    tree = Tree(Text("Files"))
    directories = {".": tree}
    for relative, kind in files:
        path = PurePosixPath(relative)
        label = escape_terminal_controls(path.name)
        if kind == "directory":
            label += "/"
        elif kind in {"symlink", "special"}:
            label += f" ({kind})"
        node = directories[str(path.parent)].add(Text(label))
        if kind == "directory":
            directories[relative] = node
    console.print(tree)
