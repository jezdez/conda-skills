from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Self

from conda.common.serialize import yaml
from conda.core.prefix_data import PrefixData
from ruamel.yaml.error import YAMLError

if TYPE_CHECKING:
    from conda.models.records import PrefixRecord


@dataclass(frozen=True)
class Skill:
    """A discovered skill directory and its owning conda package's metadata."""

    name: str
    description: str
    path: Path
    package: str
    version: str

    @classmethod
    def from_directory(cls, path: Path, record: PrefixRecord, *, prefix: Path) -> Self:
        """Load one skill's header and validate its name and filesystem boundaries.

        The caller establishes package ownership; prefix bounds the skill root,
        while companion files must remain inside that root.
        """
        name = path.name
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            raise ValueError(f"Invalid skill directory name: {name!r}")
        prefix = prefix.resolve()
        resolved = path.resolve()
        header = path / "SKILL.md"
        if not resolved.is_relative_to(prefix):
            raise ValueError(f"Skill escapes environment: {path}")
        if not header.resolve().is_relative_to(prefix):
            raise ValueError(f"Skill escapes environment: {path}")
        # Link entire folders, so reject external redirects in their contents too.
        for child in path.rglob("*"):
            if not child.resolve().is_relative_to(resolved):
                raise ValueError(f"Skill contains an escaping link: {child}")

        lines = header.read_text(encoding="utf-8").split("\n")
        if lines[0] != "---":
            raise ValueError(f"Missing YAML frontmatter: {header}")
        try:
            end = lines.index("---", 1)
        except ValueError:
            raise ValueError(f"Missing YAML frontmatter: {header}") from None
        try:
            metadata = yaml.load(io.StringIO("\n".join(lines[1:end])))
        except YAMLError as exc:
            raise ValueError(f"Invalid skill YAML in {header}: {exc}") from exc
        if not isinstance(metadata, dict) or metadata.get("name") != name:
            raise ValueError(f"Skill name must match its directory: {path}")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Skill needs a text description: {path}")
        if len(description) > 1024:
            raise ValueError(f"Skill description exceeds 1024 characters: {path}")
        return cls(name, description, path, record.name, record.version)


def discover(prefix: Path) -> list[Skill]:
    """Return package-owned skills from an existing environment, sorted by name.

    Ignore untracked directories. Reject invalid headers, duplicate ownership,
    skill roots outside the environment, and contents escaping their skill root.
    """
    prefix = prefix.resolve()
    data = PrefixData(prefix, interoperability=False)
    data.assert_environment()
    skills: dict[str, Skill] = {}
    for record in data.iter_records():
        for filename in record.files:
            parts = PurePosixPath(filename).parts
            if len(parts) != 4 or parts[:2] != ("share", "agent-skills"):
                continue
            if parts[3] != "SKILL.md":
                continue
            name = parts[2]
            path = prefix / "share/agent-skills" / name
            skill = Skill.from_directory(path, record, prefix=prefix)
            if name in skills:
                raise ValueError(f"Multiple packages own skill {name!r}")
            skills[name] = skill
    return [skills[name] for name in sorted(skills)]
