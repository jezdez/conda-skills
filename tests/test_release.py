from __future__ import annotations

import gzip
import io
import json
import os
import runpy
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest
from conda.common.serialize import yaml


def test_conda_publisher_receives_required_environment_secret() -> None:
    """Pass the environment secret explicitly across the reusable workflow boundary."""
    workflows = Path(__file__).parents[1] / ".github/workflows"
    release = yaml.loads((workflows / "release.yml").read_text(encoding="utf-8"))
    publisher = yaml.loads(
        (workflows / "publish-conda.yml").read_text(encoding="utf-8")
    )
    assert release["jobs"]["publish-conda"]["secrets"] == {
        "ANACONDA_API_KEY": "${{ secrets.ANACONDA_API_KEY }}"
    }
    assert (
        publisher["on"]["workflow_call"]["secrets"]["ANACONDA_API_KEY"]["required"]
        is True
    )
    assert publisher["jobs"]["publish"]["environment"]["name"] == "anaconda"


@pytest.mark.parametrize(
    "metadata,inspect_status,message",
    [
        ('{"index":{"build":"py_0"}}', 0, ""),
        ('{"index":{"build":"py_0"}}', 7, "package inspection"),
        ('{"index":{}}', 0, "package build field"),
        ('{"index":{"build":""}}', 0, "package build field"),
        ('{"index":{"build":42}}', 0, "package build field"),
        ("not JSON", 0, "package build field"),
    ],
)
def test_post_upload_inspection_diagnostics(
    tmp_path: Path, metadata: str, inspect_status: int, message: str
) -> None:
    """Exercise the real pre-poll checks without uploading or querying a channel."""
    bash = shutil.which("bash")
    if not bash or not shutil.which("jq") or not shutil.which("sha256sum"):
        pytest.skip("Release shell tools are unavailable")
    workflow = yaml.loads(
        (Path(__file__).parents[1] / ".github/workflows/publish-conda.yml").read_text(
            encoding="utf-8"
        )
    )
    step = next(
        step
        for step in workflow["jobs"]["publish"]["steps"]
        if step.get("name") == "Verify indexed package"
    )
    package = tmp_path / "package.conda"
    package.write_bytes(b"package")
    script = tmp_path / "inspect.sh"
    script.write_text(
        'conda() { printf "%s\\n" "$INSPECTION"; return "$INSPECT_STATUS"; }\n'
        'stat() { printf "7\\n"; }\n' + step["run"].split("for _ in {1..12}; do")[0],
        encoding="utf-8",
    )
    result = subprocess.run(
        [bash, str(script)],
        capture_output=True,
        text=True,
        timeout=10,
        env={
            **os.environ,
            "PACKAGE": str(package),
            "INSPECTION": metadata,
            "INSPECT_STATUS": str(inspect_status),
            "ANACONDA_API_KEY": "do-not-log",
        },
    )
    assert (result.returncode == 0) == (message == ""), result.stderr
    if message:
        assert message in result.stderr
        assert "status=" in result.stderr
        if not inspect_status:
            assert json.dumps(metadata) in result.stderr
    assert "do-not-log" not in result.stdout + result.stderr


@pytest.mark.parametrize("damage", ["none", "truncated", "checksum"])
def test_release_checks_gzip_before_recording_digest(
    tmp_path: Path, damage: str
) -> None:
    bash = shutil.which("bash")
    if not bash or not shutil.which("gzip") or not shutil.which("sha256sum"):
        pytest.skip("Release shell tools are unavailable")
    workflow = yaml.loads(
        (Path(__file__).parents[1] / ".github/workflows/release.yml").read_text(
            encoding="utf-8"
        )
    )
    step = next(
        step
        for step in workflow["jobs"]["build"]["steps"]
        if step.get("id") == "artifacts"
    )
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "conda_skills-0.1.0-py3-none-any.whl").touch()
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as archive:
        metadata = b"Metadata-Version: 2.4\nName: conda-skills\nVersion: 0.1.0\n"
        member = tarfile.TarInfo("conda_skills-0.1.0/PKG-INFO")
        member.size = len(metadata)
        archive.addfile(member, io.BytesIO(metadata))
    compressed = gzip.compress(raw.getvalue())
    if damage == "truncated":
        compressed = compressed[:-8]
    elif damage == "checksum":
        compressed = compressed[:-8] + bytes([compressed[-8] ^ 1]) + compressed[-7:]
    (dist / "conda_skills-0.1.0.tar.gz").write_bytes(compressed)
    script = tmp_path / "check-artifacts.sh"
    script.write_text(step["run"], encoding="utf-8")
    output = tmp_path / "output"
    result = subprocess.run(
        [bash, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "RELEASE_TAG": "0.1.0", "GITHUB_OUTPUT": str(output)},
        timeout=30,
    )
    if damage == "none":
        assert result.returncode == 0, result.stderr
        assert output.read_text().startswith("source_sha256=")
    else:
        assert result.returncode != 0
        assert not output.exists()


@pytest.fixture(params=["static", "vcs"])
def release_tree(tmp_path: Path, request, monkeypatch) -> Path:
    """Create a release fixture independent of the checkout's unreleased notes."""
    (tmp_path / "scripts").mkdir()
    script = tmp_path / "scripts/check_release.py"
    shutil.copyfile(Path(__file__).parents[1] / "scripts/check_release.py", script)
    (tmp_path / "recipe").mkdir()
    monkeypatch.delenv("SETUPTOOLS_SCM_PRETEND_VERSION", raising=False)
    monkeypatch.delenv(
        "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_RELEASE_FIXTURE", raising=False
    )
    metadata = '[project]\nname = "release-fixture"\n'
    if request.param == "vcs":
        metadata += (
            'dynamic = ["version"]\n'
            '[tool.hatch.version]\nsource = "vcs"\n'
            '[tool.hatch.version.raw-options]\nfallback_version = "0.1.0"\n'
        )
    else:
        metadata += 'version = "0.1.0"\n'
    (tmp_path / "pyproject.toml").write_text(metadata, encoding="utf-8")
    (tmp_path / "recipe/recipe.yaml").write_text(
        'context:\n  version: "0.1.0"\n', encoding="utf-8"
    )
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 0.1.0 - 2026-11-06\n\nInitial release.\n", encoding="utf-8"
    )
    return script


@pytest.mark.parametrize("version", ["0.2.0", "v0.1.0"])
def test_release_version_must_match(
    release_tree: Path, monkeypatch, version: str
) -> None:
    monkeypatch.setattr(sys, "argv", [str(release_tree), version])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2


def test_release_requires_dated_notes(release_tree: Path, monkeypatch) -> None:
    (release_tree.parents[1] / "CHANGELOG.md").write_text(
        "# Changelog\n\n## Unreleased\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2


def test_release_metadata_matches(release_tree: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    runpy.run_path(str(release_tree), run_name="__main__")
    assert "nothing was published" in capsys.readouterr().out


def test_release_recipe_version_must_match(release_tree: Path, monkeypatch) -> None:
    (release_tree.parents[1] / "recipe/recipe.yaml").write_text(
        'context:\n  version: "0.2.0"\n', encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2


def test_release_package_version_must_match(release_tree: Path, monkeypatch) -> None:
    project = release_tree.parents[1] / "pyproject.toml"
    project.write_text(
        project.read_text(encoding="utf-8").replace('"0.1.0"', '"0.2.0"'),
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2


def test_release_rejects_placeholder_date(release_tree: Path, monkeypatch) -> None:
    (release_tree.parents[1] / "CHANGELOG.md").write_text(
        "## 0.1.0 - YYYY-MM-DD\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "argv", [str(release_tree), "0.1.0"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(release_tree), run_name="__main__")
    assert error.value.code == 2
