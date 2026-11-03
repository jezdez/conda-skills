from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def prefix(tmp_path: Path) -> Path:
    prefix = tmp_path / "env"
    (prefix / "conda-meta").mkdir(parents=True)
    (prefix / "conda-meta/history").touch()
    skill = prefix / "share/agent-skills/example"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        '---\nname: example\ndescription: "Example: useful guidance"\n---\n'
        "# Example\nSee [reference](references/example.md).\n",
        encoding="utf-8",
    )
    (skill / "references/example.md").write_text("# Reference\n", encoding="utf-8")
    (prefix / "conda-meta/agent-skill-example-1.0-0.json").write_text(
        json.dumps(
            {
                "name": "agent-skill-example",
                "version": "1.0",
                "build": "0",
                "build_number": 0,
                "channel": "https://example.invalid/skills",
                "subdir": "noarch",
                "fn": "agent-skill-example-1.0-0.conda",
                "files": [
                    "share/agent-skills/example/SKILL.md",
                    "share/agent-skills/example/references/example.md",
                ],
            }
        ),
        encoding="utf-8",
    )
    return prefix
