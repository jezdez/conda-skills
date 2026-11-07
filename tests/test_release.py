from __future__ import annotations

import gzip
import hashlib
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


def test_release_source_url_uses_normalized_distribution_name() -> None:
    """Use PyPI's underscore-normalized directory for the published source archive."""
    recipe = yaml.loads(
        (Path(__file__).parents[1] / "recipe/recipe.yaml").read_text(encoding="utf-8")
    )
    assert recipe["source"][0]["then"]["url"] == (
        "https://files.pythonhosted.org/packages/source/c/conda_skills/"
        "conda_skills-${{ version }}.tar.gz"
    )


def test_conda_publication_requires_verified_release_tag() -> None:
    """Publish only through the release caller using its unchanged tagged source."""
    workflow = yaml.loads(
        (Path(__file__).parents[1] / ".github/workflows/publish-conda.yml").read_text(
            encoding="utf-8"
        )
    )
    assert set(workflow["on"]) == {"workflow_call"}
    build = workflow["jobs"]["build"]
    assert build["steps"][0]["with"]["ref"] == "refs/tags/${{ inputs.version }}"
    validation = next(step for step in build["steps"] if step.get("id") == "release")
    assert 'test "$GITHUB_REF" = "refs/tags/$RELEASE_TAG"' in validation["run"]
    assert 'test "$release_sha" = "$GITHUB_SHA"' in validation["run"]
    assert not any(
        "workflow_dispatch" in step.get("run", "") for step in build["steps"]
    )
    assert workflow["jobs"]["publish"]["environment"]["name"] == "anaconda"


def test_conda_publisher_receives_required_environment_secret() -> None:
    """Pass the environment secret explicitly to the reusable publisher."""
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


@pytest.mark.parametrize("response", ["matching", "retry", "mismatch", "malformed"])
def test_channel_verification_in_login_shell(tmp_path: Path, response: str) -> None:
    """Check the whole polling step, including login-shell cleanup after success."""
    bash = shutil.which("bash")
    if (
        os.name == "nt"
        or not bash
        or not shutil.which("jq")
        or not shutil.which("sha256sum")
    ):
        pytest.skip("POSIX release shell tools are unavailable")
    workflow = yaml.loads(
        (Path(__file__).parents[1] / ".github/workflows/publish-conda.yml").read_text()
    )
    step = next(
        step
        for step in workflow["jobs"]["publish"]["steps"]
        if step.get("name") == "Verify indexed package"
    )
    package = tmp_path / "package.conda"
    package.write_bytes(b"package")
    digest = hashlib.sha256(b"package").hexdigest()
    fields = {
        "name": "conda-skills",
        "version": "0.2.0",
        "build": "py_0",
        "build_number": 0,
        "subdir": "noarch",
        "noarch": "python",
        "license": "Apache-2.0",
        "sha256": digest,
        "size": 7,
    }
    distribution = {
        "basename": "noarch/package.conda",
        "version": "0.2.0",
        "sha256": digest if response != "mismatch" else "0" * 64,
        "size": 7,
        "labels": ["main"],
        "attrs": fields,
    }
    (tmp_path / "distribution.json").write_text(json.dumps(distribution))
    (tmp_path / "repodata.json").write_text(
        "invalid JSON"
        if response == "malformed"
        else json.dumps({"packages.conda": {package.name: fields}})
    )
    # Ubuntu's clear_console may fail silently during explicit login-shell exit.
    (tmp_path / ".bash_logout").write_text(
        'printf "logout cleanup ran\\n" >&2\nfalse\n'
    )
    script = tmp_path / "verify.sh"
    script.write_text(
        'conda() { printf \'{"index":{"build":"py_0"}}\\n\'; }\n'
        'stat() { printf "7\\n"; }\n'
        'sleep() { printf "retry\\n" >> "$HOME/retries"; }\n'
        "curl() {\n"
        '  if [ "$RESPONSE" = retry ] && [ ! -e "$HOME/retries" ]; then return 22; fi\n'
        '  case "$*" in\n'
        '    *repodata.json*) command cat "$HOME/repodata.json" ;;\n'
        '    *) command cat "$HOME/distribution.json" ;;\n'
        "  esac\n"
        "}\n" + step["run"],
        encoding="utf-8",
    )
    result = subprocess.run(
        [bash, "--noprofile", "--norc", "-el", str(script)],
        capture_output=True,
        text=True,
        timeout=15,
        env={
            **os.environ,
            "HOME": str(tmp_path),
            "PACKAGE": str(package),
            "RELEASE_TAG": "0.2.0",
            "RESPONSE": response,
        },
    )
    assert (result.returncode == 0) == (response in {"matching", "retry"}), (
        result.stderr
    )
    if response in {"matching", "retry"}:
        assert "logout cleanup ran" not in result.stderr
    else:
        assert "Could not verify the published package" in result.stderr
    retries = tmp_path / "retries"
    expected = {"matching": 0, "retry": 1, "mismatch": 12, "malformed": 12}[response]
    assert (
        len(retries.read_text().splitlines()) if retries.exists() else 0
    ) == expected


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
    assert "Nothing was published." in capsys.readouterr().out


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
