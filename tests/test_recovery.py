from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from conda.common.serialize import yaml


@pytest.fixture
def recovery() -> dict:
    """Read the narrowly scoped workflow, including its shared identity check."""
    return yaml.loads(
        (
            Path(__file__).parents[1] / ".github/workflows/recover-release.yml"
        ).read_text()
    )


def test_recovery_preserves_original_artifacts_and_publication_boundaries(recovery):
    """Only the protected uploader and final draft job may mutate remote state."""
    assert recovery["on"] == {"workflow_dispatch": None}
    jobs = recovery["jobs"]
    assert set(jobs) == {"verify", "publish", "finalize"}
    assert "github.ref == 'refs/heads/main'" in jobs["verify"]["if"]
    assert jobs["verify"]["permissions"] == {
        "actions": "read",
        "attestations": "read",
        "contents": "read",
    }
    assert jobs["publish"]["needs"] == "verify"
    assert jobs["publish"]["environment"]["name"] == "anaconda"
    assert jobs["finalize"]["needs"] == ["verify", "publish"]
    assert jobs["finalize"]["permissions"] == {"contents": "write"}
    for job in jobs.values():
        for step in job["steps"]:
            if step.get("uses", "").startswith("actions/download-artifact@"):
                assert step["with"]["run-id"] == 42319158589
                assert step["with"]["repository"] == "jezdez/conda-skills"
                assert step["with"]["github-token"] == "${{ github.token }}"
    identity = next(s for s in jobs["verify"]["steps"] if s.get("id") == "identity")
    for job in ("publish", "finalize"):
        assert identity in jobs[job]["steps"]


@pytest.mark.parametrize(
    "channel", ["https://conda.anaconda.org/jezdez", "", "https://evil.invalid"]
)
@pytest.mark.parametrize(
    "shape", ["single", "empty", "duplicate", "multiple-documents"]
)
def test_recovery_publication_predicate_fails_closed(recovery, channel, shape):
    """Evaluate the actual jq gate on verified-statement result shapes."""
    jq = shutil.which("jq")
    if not jq:
        pytest.skip("jq is unavailable")
    step = next(
        s for s in recovery["jobs"]["verify"]["steps"] if s.get("id") == "evidence"
    )
    predicate = re.search(r"jq -se '(.*?)'", step["run"], re.DOTALL).group(1)
    item = {
        "verificationResult": {
            "statement": {
                "predicateType": "https://schemas.conda.org/attestations-publish-1.schema.json",
                "predicate": {"targetChannel": channel},
            }
        }
    }
    data = json.dumps(
        [] if shape == "empty" else [item, item] if shape == "duplicate" else [item]
    )
    if shape == "multiple-documents":
        data += "\n" + data
    result = subprocess.run(
        [jq, "-se", predicate], input=data, text=True, capture_output=True, timeout=10
    )
    assert (result.returncode == 0) == (
        shape == "single" and channel == "https://conda.anaconda.org/jezdez"
    )


@pytest.mark.parametrize(
    "changed", [None, "CURRENT_ID", "CURRENT_RELEASE", "EXPECTED_RELEASE"]
)
def test_recovery_finalization_refuses_changed_identity(recovery, tmp_path, changed):
    """Run the final shell gate offline; a recording gh function replaces the write."""
    bash = shutil.which("bash")
    if not bash or not shutil.which("jq"):
        pytest.skip("Release shell tools are unavailable")
    step = recovery["jobs"]["finalize"]["steps"][-1]
    script = tmp_path / "finalize.sh"
    script.write_text(
        'gh() { printf \'%s\\n\' "$*" > "$RECORD"; '
        'printf \'%s\\n\' \'{"id":123,"tag_name":"0.1.0","draft":false}\'; }\n'
        + step["run"]
    )
    record = tmp_path / "request"
    env = {
        **os.environ,
        "RECORD": str(record),
        "RELEASE_ID": "123",
        "CURRENT_ID": "123",
        "EXPECTED_RELEASE": "a" * 64,
        "CURRENT_RELEASE": "a" * 64,
        "GH_REPO": "jezdez/conda-skills",
    }
    if changed:
        env[changed] = "456"
    result = subprocess.run(
        [bash, str(script)], env=env, text=True, capture_output=True, timeout=10
    )
    assert (result.returncode == 0) == (changed is None), result.stderr
    assert record.exists() == (changed is None)
    if record.exists():
        assert record.read_text().strip() == (
            "api --method PATCH repos/jezdez/conda-skills/releases/123 -F draft=false"
        )
