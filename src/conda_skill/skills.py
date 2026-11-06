from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Self

from conda.common.serialize import yaml
from conda.core.prefix_data import PrefixData
from ruamel.yaml.error import YAMLError

if TYPE_CHECKING:
    from conda.models.records import PrefixRecord

SKILL_NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
WINDOWS_DEVICE_NAMES = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)}
)


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
        _validate_directory(path, prefix)
        description = _read_description(path)
        return cls(path.name, description, path, record.name, record.version)


def _validate_directory(path: Path, prefix: Path) -> None:
    """Reject invalid skill names and links escaping the environment or skill root."""
    validate_name(path.name)
    prefix = prefix.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(prefix):
        raise ValueError(f"Skill escapes environment: {path}")
    if not (path / "SKILL.md").resolve().is_relative_to(prefix):
        raise ValueError(f"Skill escapes environment: {path}")
    # Link entire folders, so reject external redirects in their contents too.
    for child in path.rglob("*"):
        if not child.resolve().is_relative_to(resolved):
            raise ValueError(f"Skill contains an escaping link: {child}")


def _read_description(path: Path) -> str:
    """Read SKILL.md and return its description after validating the frontmatter.

    Require a matching name and a nonempty description of at most 1024 characters.
    Raise ValueError for missing frontmatter, malformed YAML, or invalid metadata.
    """
    header = path / "SKILL.md"
    lines = header.read_text(encoding="utf-8").split("\n")
    if lines[0] != "---":
        raise ValueError(f"Missing YAML frontmatter: {header}")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError(f"Missing YAML frontmatter: {header}") from None
    try:
        metadata = yaml.loads("\n".join(lines[1:end]))
    except YAMLError as exc:
        raise ValueError(f"Invalid skill YAML in {header}: {exc}") from exc
    if not isinstance(metadata, dict) or metadata.get("name") != path.name:
        raise ValueError(f"Skill name must match its directory: {path}")
    description = metadata.get("description")
    return validate_description(description)


def validate_name(name: str) -> None:
    """Reject names that cannot identify a skill directory."""
    if (
        not SKILL_NAME_PATTERN.fullmatch(name)
        or len(name) > 64
        or name in WINDOWS_DEVICE_NAMES
    ):
        raise ValueError(f"Invalid skill directory name: {name!r}")


def validate_description(description: object) -> str:
    """Return a nonblank text description of at most 1024 characters."""
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Skill needs a text description")
    if len(description) > 1024:
        raise ValueError("Skill description exceeds 1024 characters")
    return description


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
