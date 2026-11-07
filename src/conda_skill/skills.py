from __future__ import annotations

import os
import re
import stat
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
DEFAULT_DESCRIPTION = "Authoring placeholder: replace with when to use this skill."


@dataclass(frozen=True)
class Skill:
    """An installed skill directory and its owning conda package's metadata."""

    name: str
    description: str
    path: Path
    package: str
    version: str

    def __post_init__(self) -> None:
        """Reject invalid metadata when constructing an installed skill."""
        _validate_metadata(self.name, self.description)

    def files(self) -> list[tuple[str, str]]:
        """List relative paths and entry types in tree order without following links."""
        root = self.path.resolve(strict=True)
        if not root.is_relative_to(self.path.parents[2].resolve(strict=True)):
            raise ValueError(f"Skill escapes environment: {self.path}")
        result: list[tuple[str, str]] = []
        pending = sorted(root.iterdir(), reverse=True)
        while pending:
            path = pending.pop()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                kind = "symlink"
            elif stat.S_ISDIR(mode):
                kind = "directory"
                if not path.resolve(strict=True).is_relative_to(root):
                    raise ValueError(f"Directory escapes skill: {path}")
                pending.extend(sorted(path.iterdir(), reverse=True))
            elif stat.S_ISREG(mode):
                kind = "file"
            else:
                kind = "special"
            result.append((path.relative_to(root).as_posix(), kind))
        return result

    def read_file(self, relative: str) -> str | None:
        """Read at most 1 MiB of confined UTF-8 text, returning None for binary data.

        Require forward-slash-separated relative paths. Refuse special files and
        recheck containment and the opened file before reading any bytes.
        """
        if (
            "\\" in relative
            or ":" in relative
            or any(part in {"", ".", ".."} for part in relative.split("/"))
        ):
            raise ValueError(f"Expected a skill-relative file path: {relative!r}")
        return _read_file(self.path, relative, prefix=self.path.parents[2])

    @staticmethod
    def create_skeleton(name: str, description: str, root: Path) -> Path:
        """Create authoring files and return their path, without installing a skill.

        Validate and serialize before writing. Refuse any existing destination.
        Package only SKILL.md and leave the license for the author to choose.
        """
        _validate_metadata(name, description)
        header = yaml.dumps({"name": name, "description": description})
        recipe = yaml.dumps(
            {
                "schema_version": 1,
                "package": {"name": f"agent-skill-{name}", "version": "0.1.0"},
                "source": {"path": ".."},
                "build": {
                    "number": 0,
                    "string": "0",
                    "noarch": "generic",
                    "script": ["python build.py"],
                },
                "requirements": {"build": ["python >=3.11"]},
                "tests": [
                    {
                        "package_contents": {
                            "files": [f"share/agent-skills/{name}/SKILL.md"],
                            "strict": True,
                        }
                    }
                ],
                "about": {"summary": f"Agent skill: {name}"},
            }
        )
        path = root.resolve() / name
        path.mkdir()
        (path / "SKILL.md").write_text(
            f"---\n{header}---\n\n# {name}\n\n"
            "Authoring placeholder. Replace this text before using or distributing "
            "the skill.\n\n"
            "Describe when to use the skill, its steps, and how to check the result.\n",
            encoding="utf-8",
        )
        (path / "recipe").mkdir()
        (path / "recipe/recipe.yaml").write_text(recipe, encoding="utf-8")
        (path / "build.py").write_text(
            '"""Copy the authored skill into a conda build prefix."""\n\n'
            "from __future__ import annotations\n\n"
            "import os\nimport shutil\nfrom pathlib import Path\n\n"
            'source = Path(__file__).parent / "SKILL.md"\n'
            'destination = Path(os.environ["PREFIX"]) / '
            f'"share/agent-skills/{name}"\n'
            "destination.mkdir(parents=True)\n"
            'shutil.copy2(source, destination / "SKILL.md")\n',
            encoding="utf-8",
        )
        return path

    @classmethod
    def from_directory(cls, path: Path, record: PrefixRecord, *, prefix: Path) -> Self:
        """Load one skill's header and validate its metadata and filesystem containment.

        The caller establishes package ownership. Prefix contains the skill root,
        while companion files must remain inside that root.
        """
        _validate_directory(path, prefix)
        header = path / "SKILL.md"
        text = _read_file(path, "SKILL.md", prefix=prefix)
        if text is None:
            raise ValueError(f"Skill header must be UTF-8 text: {header}")
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
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
        return cls(
            path.name, metadata.get("description"), path, record.name, record.version
        )


def _read_file(root: Path, relative: str, *, prefix: Path) -> str | None:
    """Read a confined regular file up to 1 MiB, returning None for binary data."""
    try:
        root = root.resolve(strict=True)
        if not root.is_relative_to(prefix.resolve(strict=True)):
            raise ValueError(f"Skill escapes environment: {root}")
        path = (root / relative).resolve(strict=True)
    except RuntimeError as exc:
        raise ValueError(f"Cannot resolve skill file {relative}: {exc}") from exc
    if not path.is_relative_to(root):
        raise ValueError(f"File escapes skill: {relative}")
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"Not a regular file: {relative}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError(f"Not a regular file: {relative}")
        resolved = (root / relative).resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise ValueError(f"File escapes skill: {relative}")
        if not os.path.samestat(opened, resolved.stat()):
            raise ValueError(f"File changed while opening: {relative}")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            content = stream.read(1024 * 1024 + 1)
    except RuntimeError as exc:
        raise ValueError(f"Cannot resolve skill file {relative}: {exc}") from exc
    finally:
        os.close(descriptor)
    if len(content) > 1024 * 1024:
        raise ValueError(f"File exceeds the 1 MiB inspection limit: {relative}")
    if b"\x00" in content:
        return None
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _validate_name(name: str) -> None:
    """Reject unsafe or nonportable skill directory names."""
    if (
        not isinstance(name, str)
        or not SKILL_NAME_PATTERN.fullmatch(name)
        or len(name) > 64
        or name in WINDOWS_DEVICE_NAMES
    ):
        raise ValueError(f"Invalid skill directory name: {name!r}")


def _validate_metadata(name: str, description: str) -> None:
    """Apply the same name and description rules to installed and authored skills."""
    _validate_name(name)
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Skill needs a text description")
    if len(description) > 1024:
        raise ValueError("Skill description exceeds 1024 characters")


def _validate_directory(path: Path, prefix: Path) -> None:
    """Reject links escaping the environment or skill root before reading files."""
    try:
        prefix = prefix.resolve(strict=True)
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(prefix):
            raise ValueError(f"Skill escapes environment: {path}")
        if not (path / "SKILL.md").resolve(strict=True).is_relative_to(prefix):
            raise ValueError(f"Skill escapes environment: {path}")
        # Link entire folders, so reject external redirects in their contents too.
        for child in path.rglob("*"):
            if not child.resolve(strict=True).is_relative_to(resolved):
                raise ValueError(f"Skill contains an escaping link: {child}")
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"Cannot resolve skill files in {path}: {exc}") from exc


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
