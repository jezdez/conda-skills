from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

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


def install(skill: Skill, root: Path, backend: str) -> Path:
    """Create a skill symlink in the agent's directory and return its path.

    Reuse an existing link to the same source; reject all other conflicts.
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


def remove(skill: Skill, root: Path, backend: str) -> bool:
    """Remove a matching symlink without changing the source skill.

    Return False if absent, True if removed, and raise ValueError for conflicts.
    """
    target = destination(root, backend) / skill.name
    if not target.exists() and not target.is_symlink():
        return False
    if (
        not target.is_symlink()
        or not target.exists()
        or target.resolve() != skill.path.resolve()
    ):
        raise ValueError(f"Refusing to remove unrelated destination: {target}")
    target.unlink()
    return True


def status(root: Path, backend: str) -> list[dict[str, str]]:
    """List destination entries by name as linked, broken, or unmanaged.

    A linked entry points to a directory containing SKILL.md. These states
    describe the filesystem only; they do not establish package or link ownership.
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
                # Python 3.11 raises RuntimeError for cycles; newer Python uses OSError.
                state, target = "broken", str(path.readlink())
        else:
            state, target = "unmanaged", ""
        result.append(
            {"name": path.name, "state": state, "path": str(path), "target": target}
        )
    return result
