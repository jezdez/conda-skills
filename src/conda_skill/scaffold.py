from __future__ import annotations

from pathlib import Path

from conda.common.serialize import yaml

from .skills import validate_description, validate_name

DEFAULT_DESCRIPTION = "Authoring placeholder: replace with when to use this skill."


def create(name: str, description: str, root: Path) -> Path:
    """Create an authoring skeleton, refusing any existing destination.

    Validate and serialize metadata before writing. The recipe packages only
    SKILL.md; no skill content is executed and no license is assigned.
    """
    validate_name(name)
    validate_description(description)
    header = yaml.dumps({"name": name, "description": description})
    recipe = yaml.dumps(
        {
            "schema_version": 1,
            "package": {"name": f"agent-skill-{name}", "version": "0.1.0"},
            "source": {"path": ".."},
            "build": {
                "number": 0,
                "string": "0",
                "noarch": "generic",
                "script": ["python build.py"],
            },
            "requirements": {"build": ["python >=3.11"]},
            "tests": [
                {
                    "package_contents": {
                        "files": [f"share/agent-skills/{name}/SKILL.md"],
                        "strict": True,
                    }
                }
            ],
            "about": {"summary": f"Agent skill: {name}"},
        }
    )
    path = root.resolve() / name
    path.mkdir()
    (path / "SKILL.md").write_text(
        f"---\n{header}---\n\n# {name}\n\n"
        "Authoring placeholder. Replace this text before using or distributing "
        "the skill.\n\n"
        "Describe when to use the skill, its steps, and how to check the result.\n",
        encoding="utf-8",
    )
    (path / "recipe").mkdir()
    (path / "recipe/recipe.yaml").write_text(recipe, encoding="utf-8")
    (path / "build.py").write_text(
        '"""Copy the authored skill into a conda build prefix."""\n\n'
        "from __future__ import annotations\n\n"
        "import os\nimport shutil\nfrom pathlib import Path\n\n"
        'source = Path(__file__).parent / "SKILL.md"\n'
        f'destination = Path(os.environ["PREFIX"]) / "share/agent-skills/{name}"\n'
        "destination.mkdir(parents=True)\n"
        'shutil.copy2(source, destination / "SKILL.md")\n',
        encoding="utf-8",
    )
    return path
