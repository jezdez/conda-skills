"""Test the example and generated skills in temporary environments and projects."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> None:
    """Install the example and verify listing, linking, status, removal, and cleanup."""
    root = Path(__file__).resolve().parents[1]
    package = root / "conda-dist/noarch/conda-skills-example-0.1.0-0.conda"
    if not package.is_file():
        raise SystemExit("Build the documentation example package first.")
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        home = directory / "home"
        home.mkdir()
        project = directory / "project"
        project.mkdir()
        source = directory / "source-env"
        condarc = directory / "condarc"
        condarc.write_text("{}\n", encoding="utf-8")
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("CONDA_") and key not in {"CONDARC", "PYTHONPATH"}
        }
        environment.update(
            HOME=str(home),
            USERPROFILE=str(home),
            XDG_CONFIG_HOME=str(home / ".config"),
            CONDARC=str(condarc),
            CONDA_NO_PLUGINS="false",
            CONDA_JSON="false",
            CONDA_PKGS_DIRS=str(directory / "package-cache"),
            RATTLER_CACHE_DIR=str(directory / "rattler-cache"),
            CONDA_AUTO_UPDATE_CONDA="false",
            CONDA_NOTIFY_OUTDATED_CONDA="false",
        )

        def run(*arguments: str) -> str:
            """Run the real installed conda command from the tutorial project."""
            result = subprocess.run(
                [sys.executable, "-m", "conda", *arguments],
                cwd=project,
                env=environment,
                text=True,
                capture_output=True,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            return result.stdout

        run("create", "--yes", "--offline", "--prefix", str(source), str(package))
        listed = json.loads(run("skill", "list", "-p", "../source-env", "--json"))
        assert [skill["name"] for skill in listed] == ["review-notes"]
        assert listed[0]["package"] == "conda-skills-example"
        assert "review-notes" in run("skill", "list", "-p", "../source-env")
        for _ in range(2):
            assert "Linked review-notes at" in run(
                "skill", "link", "review-notes", "-p", "../source-env"
            )
        link = project / ".agents/skills/review-notes"
        assert link.is_symlink()
        assert (link / "SKILL.md").read_text(encoding="utf-8") == (
            root / "docs/examples/review-notes/SKILL.md"
        ).read_text(encoding="utf-8")
        assert "linked" in run("skill", "status")
        [entry] = json.loads(run("skill", "status", "--json"))
        assert entry["state"] == "linked"
        assert (
            Path(entry["target"])
            == (source / "share/agent-skills/review-notes").resolve()
        )
        assert "Removed link for review-notes." in run(
            "skill", "unlink", "review-notes"
        )
        assert json.loads(run("skill", "status", "--json")) == []
        assert (source / "share/agent-skills/review-notes/SKILL.md").is_file()
        run("remove", "--yes", "--prefix", str(source), "--all")

        created = json.loads(
            run(
                "skill",
                "init",
                "generated-notes",
                "--description",
                "Example guidance",
                "--json",
            )
        )
        skeleton = project / "generated-notes"
        assert Path(created["path"]) == skeleton.resolve()
        output = directory / "packages"
        subprocess.run(
            [
                "rattler-build",
                "build",
                "--recipe",
                str(skeleton / "recipe/recipe.yaml"),
                "--output-dir",
                str(output),
                "-c",
                "conda-forge",
            ],
            cwd=project,
            env=environment,
            check=True,
        )
        [generated_package] = (output / "noarch").glob("*.conda")
        run(
            "create",
            "--yes",
            "--offline",
            "--prefix",
            str(source),
            str(generated_package),
        )
        environment["CONDA_PREFIX"] = str(source)
        [generated] = json.loads(run("skill", "list", "--json"))
        assert generated["name"] == "generated-notes"
        assert generated["description"] == "Example guidance"
        run("skill", "link", "generated-notes", "--json")
        assert (project / ".agents/skills/generated-notes").is_symlink()
        environment["CONDA_PREFIX"] = str(directory / "unrelated-missing-environment")
        run("skill", "unlink", "generated-notes", "--json")
        run("remove", "--yes", "--prefix", str(source), "--all")
    print("Tutorial and generated skeleton build/install/link/unlink workflows passed.")


if __name__ == "__main__":
    main()
