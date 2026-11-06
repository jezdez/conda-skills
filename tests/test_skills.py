from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from conda.core.prefix_data import PrefixData

from conda_skill.skills import Skill, discover


def test_package_owned_discovery(prefix: Path) -> None:
    unowned = prefix / "share/agent-skills/unowned"
    unowned.mkdir()
    (unowned / "SKILL.md").write_text("unowned", encoding="utf-8")
    [skill] = discover(prefix)
    assert skill.name == "example"
    assert skill.package == "agent-skill-example"
    assert skill.version == "1.0"
    assert skill.description == "Example: useful guidance"


@pytest.mark.parametrize(
    "metadata,message",
    [
        ({"name": "other", "description": "Guidance"}, "name must match"),
        ({"name": "example"}, "text description"),
        ({"name": "example", "description": ""}, "text description"),
        ({"name": "example", "description": " \t\n"}, "text description"),
        ({"name": "example", "description": 42}, "text description"),
        ({"name": "example", "description": "x" * 1025}, "exceeds 1024"),
    ],
    ids=["mismatched-name", "missing", "empty", "blank", "non-string", "too-long"],
)
def test_invalid_metadata_rejected(prefix: Path, metadata: dict, message: str) -> None:
    (prefix / "share/agent-skills/example/SKILL.md").write_text(
        f"---\n{json.dumps(metadata)}\n---\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match=message):
        discover(prefix)


@pytest.mark.parametrize("length", [1, 1024])
def test_description_length_boundaries(prefix: Path, length: int) -> None:
    description = "x" * length
    (prefix / "share/agent-skills/example/SKILL.md").write_text(
        f"---\nname: example\ndescription: {description}\n---\n", encoding="utf-8"
    )
    [skill] = discover(prefix)
    assert skill.description == description


@pytest.mark.parametrize(
    "name,valid",
    [
        ("a", True),
        ("a" * 64, True),
        ("skill-2", True),
        ("con-skill", True),
        ("com0", True),
        ("com10", True),
        ("a" * 65, False),
        ("Uppercase", False),
        ("under_score", False),
        ("-leading", False),
        ("trailing-", False),
        ("double--hyphen", False),
    ],
)
def test_skill_directory_names(prefix: Path, name: str, valid: bool) -> None:
    path = prefix / "share/agent-skills" / name
    path.mkdir()
    (path / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Guidance\n---\n", encoding="utf-8"
    )
    [record] = PrefixData(prefix, interoperability=False).iter_records()
    if valid:
        assert Skill.from_directory(path, record, prefix=prefix).name == name
    else:
        with pytest.raises(ValueError, match="Invalid skill directory name"):
            Skill.from_directory(path, record, prefix=prefix)


def test_external_skill_root_with_internal_header(prefix: Path, tmp_path: Path) -> None:
    path = prefix / "share/agent-skills/example"
    header = prefix / "header.md"
    header.write_bytes((path / "SKILL.md").read_bytes())
    shutil.rmtree(path)
    path.symlink_to(tmp_path, target_is_directory=True)
    (tmp_path / "SKILL.md").symlink_to(header)
    with pytest.raises(ValueError, match="escapes environment"):
        discover(prefix)


def test_external_reference_symlink_rejected(prefix: Path, tmp_path: Path) -> None:
    reference = prefix / "share/agent-skills/example/references/example.md"
    external = tmp_path / "external.md"
    external.write_bytes(reference.read_bytes())
    reference.unlink()
    reference.symlink_to(external)
    with pytest.raises(ValueError, match="escaping link"):
        discover(prefix)
    assert external.read_text(encoding="utf-8") == "# Reference\n"


def test_external_skill_header_symlink_rejected(prefix: Path, tmp_path: Path) -> None:
    header = prefix / "share/agent-skills/example/SKILL.md"
    external = tmp_path / "SKILL.md"
    external.write_bytes(header.read_bytes())
    header.unlink()
    header.symlink_to(external)
    with pytest.raises(ValueError, match="escapes environment"):
        discover(prefix)


def test_duplicate_package_ownership_rejected(prefix: Path) -> None:
    record = json.loads(
        (prefix / "conda-meta/agent-skill-example-1.0-0.json").read_text(
            encoding="utf-8"
        )
    )
    record.update(name="other-skill-package", fn="other-skill-package-1.0-0.conda")
    (prefix / "conda-meta/other-skill-package-1.0-0.json").write_text(
        json.dumps(record), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Multiple packages own skill 'example'"):
        discover(prefix)


@pytest.mark.parametrize(
    "text",
    [
        "---\nname: example\ndescription: Guidance\n---\n# Body\n---\n",
        "---\r\nname: example\r\ndescription: Guidance\r\n---\r\n",
        "---\nname: example\ndescription: Guidance\n---",
    ],
    ids=["body-delimiter", "crlf", "closing-delimiter-at-eof"],
)
def test_load_skill_directory(prefix: Path, text: str) -> None:
    path = prefix / "share/agent-skills/example"
    (path / "SKILL.md").write_bytes(text.encode("utf-8"))
    [record] = PrefixData(prefix, interoperability=False).iter_records()
    skill = Skill.from_directory(path, record, prefix=prefix)
    assert skill == Skill("example", "Guidance", path, "agent-skill-example", "1.0")


@pytest.mark.parametrize(
    "text",
    [
        "name: example\ndescription: Guidance\n---\n",
        "\n---\nname: example\ndescription: Guidance\n---\n",
        "---\nname: example\ndescription: Guidance\n",
        "---\nname: example\ndescription: Guidance\n---suffix\n",
    ],
    ids=["missing-open", "leading-blank", "missing-close", "invalid-close"],
)
def test_frontmatter_delimiters_required(prefix: Path, text: str) -> None:
    (prefix / "share/agent-skills/example/SKILL.md").write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="Missing YAML frontmatter"):
        discover(prefix)


@pytest.mark.parametrize("location", ["root", "header", "reference"])
@pytest.mark.parametrize("mutual", [False, True], ids=["self", "mutual"])
def test_discovery_rejects_symlink_cycles(
    prefix: Path, location: str, mutual: bool
) -> None:
    path = prefix / "share/agent-skills/example"
    if location == "root":
        shutil.rmtree(path)
    else:
        path = path / ("SKILL.md" if location == "header" else "references/example.md")
        path.unlink()
    path.symlink_to(
        "cycle-peer" if mutual else path.name, target_is_directory=location == "root"
    )
    if mutual:
        path.with_name("cycle-peer").symlink_to(
            path.name, target_is_directory=location == "root"
        )
    with pytest.raises(ValueError, match="Cannot resolve skill"):
        discover(prefix)
