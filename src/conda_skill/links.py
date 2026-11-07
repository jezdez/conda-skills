from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import TYPE_CHECKING

from conda.exceptions import CondaError

from .skills import _validate_name, discover

if TYPE_CHECKING:
    from .skills import Skill

BACKENDS = {"agents": ".agents/skills", "claude": ".claude/skills"}


def destination(root: Path, backend: str) -> Path:
    """Return the backend's skill directory under root without creating it.

    Raise ValueError if any client directory redirects through a symlink.
    """
    root = root.resolve()
    path = root
    for part in Path(BACKENDS[backend]).parts:
        path = path / part
        if path.is_symlink() or path.resolve() != path:
            raise ValueError(f"Refusing redirected client directory: {path}")
    return path


def link(skill: Skill, root: Path, backend: str) -> Path:
    """Create a skill symlink in the agent's directory and return its path.

    Reuse an existing link to the same source and reject all other conflicts.
    Use a relative target unless the source is on a different Windows drive.
    """
    directory = destination(root, backend)
    target = directory / skill.name
    if (
        target.is_symlink()
        and target.exists()
        and target.resolve() == skill.path.resolve()
    ):
        return target
    if target.exists() or target.is_symlink():
        raise ValueError(f"Refusing to replace existing destination: {target}")
    directory.mkdir(parents=True, exist_ok=True)
    if skill.path.drive.casefold() != directory.drive.casefold():
        link_target = str(skill.path)
    else:
        link_target = os.path.relpath(skill.path, directory)
    target.symlink_to(link_target, target_is_directory=True)
    return target


def unlink(name: str, root: Path, backend: str, *, force: bool = False) -> bool:
    """Remove a destination symlink without changing its source or package.

    Verify package ownership in the prefix inferred from the recorded target path.
    Force skips source verification only. Return False if absent, True if removed,
    and raise ValueError for unsafe destinations or unverifiable sources.
    """
    _validate_name(name)
    target = destination(root, backend) / name
    try:
        original = target.lstat()
    except FileNotFoundError:
        return False
    if not stat.S_ISLNK(original.st_mode):
        raise ValueError(
            f"Refusing to remove a destination that is not a symlink: {target}"
        )
    raw_target = target.readlink()
    if not force:
        try:
            source = target.resolve(strict=True)
            recorded = target.parent / raw_target
            if recorded.parts[-3:] != ("share", "agent-skills", name):
                raise ValueError(
                    "Target does not match the packaged skill layout and name"
                )
            skills = discover(recorded.parents[2])
            if not any(
                skill.name == name and skill.path.resolve(strict=True) == source
                for skill in skills
            ):
                raise ValueError("No package records own the target skill header")
        except (
            ValueError,
            OSError,
            RuntimeError,
            CondaError,
            KeyError,
            TypeError,
        ) as exc:
            raise ValueError(
                f"Refusing to remove unverified symlink: {target}. {exc}. "
                "Inspect it with conda skill status, then use --force to remove only "
                "this symlink."
            ) from exc
    # Recheck known changes. Filesystem operations are not a transaction.
    destination(root, backend)
    current = target.lstat()
    if (
        not stat.S_ISLNK(current.st_mode)
        or not os.path.samestat(original, current)
        or target.readlink() != raw_target
    ):
        raise ValueError(f"Refusing to remove changed destination: {target}")
    target.unlink()
    return True


def status(root: Path, backend: str) -> list[dict[str, str]]:
    """List destination entries by name as linked, broken, or unmanaged.

    A linked entry points to a directory containing SKILL.md. These states
    describe the filesystem only, without identifying package or link ownership.
    """
    directory = destination(root, backend)
    if not directory.exists():
        return []
    result = []
    for path in sorted(directory.iterdir()):
        if path.is_symlink():
            state = (
                "linked"
                if path.is_dir() and (path / "SKILL.md").is_file()
                else "broken"
            )
            try:
                try:
                    target = str(path.resolve(strict=True))
                except FileNotFoundError:
                    target = str(path.resolve())
            except (OSError, RuntimeError):
                # Python 3.11 raises RuntimeError for cycles, newer Python uses OSError.
                state, target = "broken", str(path.readlink())
        else:
            state, target = "unmanaged", ""
        result.append(
            {"name": path.name, "state": state, "path": str(path), "target": target}
        )
    return result
