from __future__ import annotations

import gzip
import hashlib
import io
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


def test_conda_release_builds_attests_then_publishes() -> None:
    """Keep signing and protected, non-overwriting uploads before finalization."""
    workflows = Path(__file__).parents[1] / ".github/workflows"
    publisher = yaml.loads((workflows / "publish-conda.yml").read_text())
    jobs = publisher["jobs"]
    assert set(jobs) == {"build", "attest", "publish"}
    assert jobs["attest"]["needs"] == "build"
    assert set(jobs["publish"]["needs"]) == {"build", "attest"}
    attest = jobs["attest"]["steps"]
    assert {
        "Record GitHub build provenance",
        "Create CEP 27 publication attestation",
        "Verify publication evidence before upload",
    } <= {step.get("name") for step in attest}
    verification = next(
        step["run"]
        for step in attest
        if step.get("name") == "Verify publication evidence before upload"
    )
    assert 'gh attestation verify "${packages[0]}"' in verification
    assert '--source-digest "$GITHUB_SHA" --source-ref "$GITHUB_REF"' in verification
    assert jobs["publish"]["environment"]["name"] == "anaconda"
    preflight = next(
        step["run"]
        for step in jobs["publish"]["steps"]
        if step.get("name") == "Verify unchanged tag and absent channel release"
    )
    assert 'if [ "$status" != "404" ]; then' in preflight
    upload = next(
        step["run"]
        for step in jobs["publish"]["steps"]
        if step.get("name") == "Upload immutable package"
    )
    assert "unset ANACONDA_FORCE ANACONDA_SERVER_URL" in upload
    assert "rattler-build upload --no-config anaconda" in upload
    assert "--force" not in upload
    release = yaml.loads((workflows / "release.yml").read_text())
    assert "publish-conda" in release["jobs"]["publish-github-release"]["needs"]


@pytest.mark.parametrize("damage", ["none", "archive"])
def test_source_retrieval_retries_downloads_not_validation(
    tmp_path: Path, damage: str
) -> None:
    """Download the normalized source URL with bounded retries and check its digest."""
    bash = shutil.which("bash")
    if not bash or not shutil.which("sha256sum"):
        pytest.skip("Release shell tools are unavailable")
    workflow = yaml.loads(
        (Path(__file__).parents[1] / ".github/workflows/publish-conda.yml").read_text()
    )
    step = next(
        step
        for step in workflow["jobs"]["build"]["steps"]
        if step.get("name") == "Verify the published source distribution"
    )
    archive = b"original source archive"
    digest = hashlib.sha256(archive).hexdigest()
    (tmp_path / "archive").write_bytes(
        b"changed bytes" if damage == "archive" else archive
    )
    script = tmp_path / "source.sh"
    script.write_text(
        "curl() {\n"
        '  printf "%s\\n" "$@" >> "$RUNNER_TEMP/calls"\n'
        '  command cp "$RUNNER_TEMP/archive" "${@: -1}"\n'
        "}\n" + step["run"],
        encoding="utf-8",
    )
    result = subprocess.run(
        [bash, str(script)],
        capture_output=True,
        text=True,
        timeout=10,
        env={
            **os.environ,
            "RUNNER_TEMP": str(tmp_path),
            "RELEASE_TAG": "0.2.1",
            "CONDA_SKILLS_SOURCE_SHA256": digest,
        },
    )
    assert (result.returncode == 0) == (damage == "none"), result.stderr
    arguments = (tmp_path / "calls").read_text().splitlines()
    assert arguments.count("--retry") == 1
    assert arguments[arguments.index("--retry") + 1] == "3"
    assert "--retry-all-errors" in arguments
    assert arguments[arguments.index("--retry-delay") + 1] == "2"
    assert arguments[arguments.index("--retry-max-time") + 1] == "120"
    assert arguments[-3:] == [
        "https://files.pythonhosted.org/packages/source/c/conda_skills/"
        "conda_skills-0.2.1.tar.gz",
        "-o",
        str(tmp_path / "release-source.tar.gz"),
    ]
    if damage == "archive":
        assert "FAILED" in result.stdout
    assert "for " not in step["run"]
    assert "while " not in step["run"]


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


def test_conda_build_uses_resolved_metadata(release_tree: Path, monkeypatch) -> None:
    calls = []

    def build(command, *, cwd, env, check):
        calls.append(command)
        assert cwd == release_tree.parents[1]
        assert env["CONDA_SKILLS_VERSION"] == "0.1.0"
        assert check is True

    monkeypatch.setenv("CONDA_SKILLS_VERSION", "9.9.9")
    monkeypatch.setattr(subprocess, "run", build)
    monkeypatch.setattr(sys, "argv", [str(release_tree), "--build-conda"])
    runpy.run_path(str(release_tree), run_name="__main__")
    assert calls == [
        [
            "rattler-build",
            "build",
            "--recipe",
            "recipe/recipe.yaml",
            "--output-dir",
            "conda-dist",
            "-c",
            "conda-forge",
        ]
    ]


def test_recipe_requires_version_without_default() -> None:
    recipe = yaml.loads(
        (Path(__file__).parents[1] / "recipe/recipe.yaml").read_text(encoding="utf-8")
    )
    assert recipe["context"]["version"] == '${{ env.get("CONDA_SKILLS_VERSION") }}'


def test_release_check_requires_version(release_tree: Path, monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", [str(release_tree)])
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
