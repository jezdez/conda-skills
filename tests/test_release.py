from __future__ import annotations

import gzip
import hashlib
import io
import os
import shutil
import subprocess
import tarfile
import tomllib
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
    assert arguments[-3:-1] == [
        "https://files.pythonhosted.org/packages/source/c/conda_skills/"
        "conda_skills-0.2.1.tar.gz",
        "-o",
    ]
    assert Path(arguments[-1]) == tmp_path / "release-source.tar.gz"
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


@pytest.mark.parametrize("filename", ["release.yml", "publish-conda.yml"])
def test_release_compares_hatch_version_directly(filename: str) -> None:
    """Compare Hatch's resolved version with the release tag without a helper script."""
    source = (Path(__file__).parents[1] / ".github/workflows" / filename).read_text(
        encoding="utf-8"
    )
    workflow = yaml.loads(source)
    command = "conda workspace run -e build -- python -m hatchling version"
    validation = next(
        step["run"]
        for step in workflow["jobs"]["build"]["steps"]
        if command in step.get("run", "")
    )
    assert "version=" in validation
    assert 'test "$version" = "$RELEASE_TAG"' in validation
    assert "check_release.py" not in source
    assert "check-release" not in source
    assert "CHANGELOG.md" not in validation


def test_conda_build_task_resolves_required_version() -> None:
    """Resolve Hatch metadata in each platform's task before invoking rattler-build."""
    manifest = tomllib.loads(
        (Path(__file__).parents[1] / "conda.toml").read_text(encoding="utf-8")
    )
    assert "check-release" not in manifest["tasks"]
    command = manifest["tasks"]["build-conda"]["cmd"]
    assert command.startswith("version=$(python -m hatchling version) && ")
    build = (
        "rattler-build build --recipe recipe/recipe.yaml "
        "--output-dir conda-dist -c conda-forge"
    )
    assert f'CONDA_SKILLS_VERSION="$version" {build}' in command
    windows = manifest["target"]["win-64"]["tasks"]["build-conda"]["cmd"]
    assert windows[0] == "powershell"
    assert "-Command" in windows
    assert "$version = python -m hatchling version" in windows[-1]
    assert "$env:CONDA_SKILLS_VERSION = $version" in windows[-1]
    assert build in windows[-1]
    assert windows[-1].count("exit $LASTEXITCODE") == 2


def test_recipe_requires_version_without_default() -> None:
    """Require the build task to supply the recipe version explicitly."""
    recipe = yaml.loads(
        (Path(__file__).parents[1] / "recipe/recipe.yaml").read_text(encoding="utf-8")
    )
    assert recipe["context"]["version"] == '${{ env.get("CONDA_SKILLS_VERSION") }}'


@pytest.mark.parametrize("failure", [0, 7])
def test_powershell_conda_build_propagates_failure(
    tmp_path: Path, failure: int
) -> None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell:
        pytest.skip("PowerShell is unavailable")
    manifest = tomllib.loads((Path(__file__).parents[1] / "conda.toml").read_text())
    command = manifest["target"]["win-64"]["tasks"]["build-conda"]["cmd"][-1]
    script = tmp_path / "build.ps1"
    script.write_text(
        "function python {\n"
        "  $global:LASTEXITCODE = [int]$env:SIMULATED_STATUS\n"
        "  '0.2.1'\n"
        "}\n"
        "function rattler-build {\n"
        "  if ($env:CONDA_SKILLS_VERSION -ne '0.2.1') { exit 99 }\n"
        "  $global:LASTEXITCODE = 0\n"
        "}\n" + command,
        encoding="utf-8",
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-File", str(script)],
        env={**os.environ, "SIMULATED_STATUS": str(failure)},
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == failure, result.stderr
