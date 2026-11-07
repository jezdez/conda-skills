from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest
from conda.core.prefix_data import PrefixData

from conda_skill.skills import Skill, discover


@pytest.mark.parametrize("operation", ["files", "read_file"])
def test_skill_rejects_root_replaced_after_discovery(
    prefix: Path, tmp_path: Path, operation: str
) -> None:
    [skill] = discover(prefix)
    outside = tmp_path / "outside"
    skill.path.rename(outside)
    skill.path.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes environment"):
        if operation == "files":
            skill.files()
        else:
            skill.read_file("references/example.md")


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


def test_skill_files_are_sorted_without_following_symlinks(prefix: Path) -> None:
    [skill] = discover(prefix)
    (skill.path / "assets").mkdir()
    (skill.path / "assets/data.bin").write_bytes(b"\x00")
    (skill.path / "scripts").mkdir()
    (skill.path / "scripts/run.py").write_text("raise SystemExit(42)\n")
    (skill.path / "loop").symlink_to("loop")
    (skill.path / "reference-link").symlink_to("references", target_is_directory=True)
    assert skill.files() == [
        ("SKILL.md", "file"),
        ("assets", "directory"),
        ("assets/data.bin", "file"),
        ("loop", "symlink"),
        ("reference-link", "symlink"),
        ("references", "directory"),
        ("references/example.md", "file"),
        ("scripts", "directory"),
        ("scripts/run.py", "file"),
    ]


@pytest.mark.parametrize(
    "content,expected",
    [
        (b"", ""),
        (
            b"line\r\n[bold]literal[/bold]\t\x1b[31m\n",
            "line\r\n[bold]literal[/bold]\t\x1b[31m\n",
        ),
        (b"\x00data", None),
        (b"\xffdata", None),
        (b"x" * 1024 * 1024, "x" * 1024 * 1024),
    ],
    ids=["empty", "literal-text", "nul", "invalid-utf8", "limit"],
)
def test_skill_reads_text_or_reports_binary(
    prefix: Path, content: bytes, expected: str | None
) -> None:
    [skill] = discover(prefix)
    (skill.path / "references/example.md").write_bytes(content)
    assert skill.read_file("references/example.md") == expected


@pytest.mark.parametrize(
    "relative",
    [
        "",
        ".",
        "..",
        "../SKILL.md",
        "references/../SKILL.md",
        "/SKILL.md",
        "C:/SKILL.md",
        "C:SKILL.md",
        "//server/share/file",
        r"references\example.md",
        r"\\server\share\file",
        "SKILL.md:stream",
        "references/./example.md",
        "references//example.md",
        "references/",
    ],
)
def test_skill_read_rejects_nonportable_or_traversing_paths(
    prefix: Path, relative: str
) -> None:
    [skill] = discover(prefix)
    with pytest.raises(ValueError, match="skill-relative"):
        skill.read_file(relative)


@pytest.mark.parametrize("directory", [False, True])
def test_skill_read_rechecks_symlinks_after_discovery(
    prefix: Path, tmp_path: Path, directory: bool
) -> None:
    [skill] = discover(prefix)
    external = tmp_path / "external"
    external.mkdir()
    (external / "example.md").write_text("private")
    reference = skill.path / "references/example.md"
    reference.unlink()
    if directory:
        reference.parent.rmdir()
        reference.parent.symlink_to(external, target_is_directory=True)
    else:
        reference.symlink_to(external / "example.md")
    with pytest.raises(ValueError, match="escapes skill"):
        skill.read_file("references/example.md")


def test_skill_read_allows_internal_symlink(prefix: Path) -> None:
    [skill] = discover(prefix)
    (skill.path / "reference.md").symlink_to("references/example.md")
    assert skill.read_file("reference.md") == (
        skill.path / "references/example.md"
    ).read_bytes().decode("utf-8")


def test_skill_read_rejects_large_files(prefix: Path) -> None:
    [skill] = discover(prefix)
    (skill.path / "large").write_bytes(b"x" * (1024 * 1024 + 1))
    with pytest.raises(ValueError, match="1 MiB"):
        skill.read_file("large")


def test_skill_read_missing_file(prefix: Path) -> None:
    [skill] = discover(prefix)
    with pytest.raises(FileNotFoundError):
        skill.read_file("missing")


def test_skill_read_rejects_directory(prefix: Path) -> None:
    [skill] = discover(prefix)
    with pytest.raises(ValueError, match="regular file"):
        skill.read_file("references")


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFOs require POSIX")
def test_skill_lists_fifo_but_refuses_to_open_it(prefix: Path, monkeypatch) -> None:
    [skill] = discover(prefix)
    os.mkfifo(skill.path / "pipe")

    def refuse_open(*args, **kwargs):
        pytest.fail("A special file must be rejected before opening")

    monkeypatch.setattr(os, "open", refuse_open)
    assert ("pipe", "special") in skill.files()
    with pytest.raises(ValueError, match="regular file"):
        skill.read_file("pipe")


@pytest.mark.parametrize(
    "content,message", [(b"x" * (1024 * 1024 + 1), "1 MiB"), (b"\xff", "text")]
)
def test_discovery_rejects_oversized_or_binary_header(
    prefix: Path, content: bytes, message: str
) -> None:
    (prefix / "share/agent-skills/example/SKILL.md").write_bytes(content)
    with pytest.raises(ValueError, match=message):
        discover(prefix)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFOs require POSIX")
def test_discovery_rejects_special_header_before_opening(
    prefix: Path, monkeypatch
) -> None:
    header = prefix / "share/agent-skills/example/SKILL.md"
    header.unlink()
    os.mkfifo(header)
    path_open = Path.open

    def guarded_open(path, *args, **kwargs):
        if path == header:
            pytest.fail("Discovery must not open a FIFO header")
        return path_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    with pytest.raises(ValueError, match="regular file"):
        discover(prefix)


@pytest.mark.parametrize("replacement", ["file", "escape", "fifo"])
@pytest.mark.skipif(os.name == "nt", reason="Windows refuses renaming open CRT handles")
def test_skill_rechecks_opened_file_before_reading(
    prefix: Path, tmp_path: Path, monkeypatch, replacement: str
) -> None:
    if replacement == "fifo" and not hasattr(os, "mkfifo"):
        pytest.skip("FIFOs require POSIX")
    [skill] = discover(prefix)
    path = skill.path / "references/example.md"
    external = tmp_path / "external.md"
    external.write_text("private")
    original_open = os.open
    descriptors = []

    def replace_on_open(filename, flags):
        if replacement == "fifo":
            path.unlink()
            os.mkfifo(path)
        descriptor = original_open(filename, flags)
        descriptors.append(descriptor)
        if replacement != "fifo":
            path.rename(path.with_name("old.md"))
            if replacement == "escape":
                path.symlink_to(external)
            else:
                path.write_text("replacement")
        return descriptor

    monkeypatch.setattr(os, "open", replace_on_open)
    message = {
        "file": "changed while opening",
        "escape": "escapes skill",
        "fifo": "regular file",
    }[replacement]
    with pytest.raises(ValueError, match=message):
        skill.read_file("references/example.md")
    for descriptor in descriptors:
        with pytest.raises(OSError):
            os.fstat(descriptor)


def test_skill_read_cycle_is_validation_error(prefix: Path) -> None:
    [skill] = discover(prefix)
    (skill.path / "cycle").symlink_to("cycle")
    with pytest.raises((ValueError, OSError)):
        skill.read_file("cycle")
