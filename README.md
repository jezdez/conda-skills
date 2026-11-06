# conda-skills

[![Tests](https://github.com/jezdez/conda-skills/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jezdez/conda-skills/actions/workflows/tests.yml)
[![Docs](https://github.com/jezdez/conda-skills/actions/workflows/docs.yml/badge.svg?branch=main)](https://jezdez.github.io/conda-skills/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://jezdez.github.io/conda-skills/how-to/installation/)
[![Conda 26.9+](https://img.shields.io/badge/conda-26.9%2B-44A833?logo=anaconda&logoColor=white)](https://jezdez.github.io/conda-skills/how-to/installation/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Lint: Ruff](https://img.shields.io/badge/lint-Ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)

`conda skill` makes skills from conda packages available to your agent through directory links in a project or your home directory. Conda manages the package versions. You choose which skills to use.

Inspired by Pavel Zwerschke's [pixi-skills](https://github.com/pavelzw/pixi-skills) and [skill-forge](https://github.com/pavelzw/skill-forge), conda-skills brings the same package-manager approach to conda's Python stack. See [prior art](https://jezdez.github.io/conda-skills/explanation/prior-art/) for the background and shared conventions.

Requires Python 3.11 or newer and conda 26.9 or newer. Install conda through a conda distribution, not PyPI.

## Installation

Install a published package into the environment that runs conda, usually `base`:

```sh
conda install -n base --override-channels -c jezdez -c conda-forge conda-skills
conda skill --help
```

To use a checkout, install it with `conda-pypi` in the environment that runs conda:

```sh
conda install -n base --override-channels -c conda-forge "conda-pypi>=0.12" "hatchling>=1.27" "hatch-vcs>=0.4" "rich>=13" "ruamel.yaml>=0.11.14,<0.20"
conda pypi install -n base -e .
conda skill --help
```

Run these commands from the repository root. The first supplies build requirements and runtime dependencies, which editable installs do not resolve. If another prefix owns your conda executable, replace `-n base` with `-p /path/to/conda-prefix` in both commands.

The [first-use tutorial](https://jezdez.github.io/conda-skills/tutorials/skill-forge/) takes you from downloading a skill package to reviewing its instructions, connecting it to a project, and removing the link.

See [installation](https://jezdez.github.io/conda-skills/how-to/installation/) for PyPI and local-artifact alternatives. Installing the plugin in an unrelated environment does not register it with another conda executable.

## Documentation

- [Documentation home](https://jezdez.github.io/conda-skills/)
- [Install conda-skills](https://jezdez.github.io/conda-skills/how-to/installation/)
- [Try your first skill](https://jezdez.github.io/conda-skills/tutorials/skill-forge/)
- [Share skills with conda-workspaces](https://jezdez.github.io/conda-skills/how-to/project-skills/)
- [Update or roll back a skill](https://jezdez.github.io/conda-skills/how-to/update-skills/)
- [Build and try a skill package](https://jezdez.github.io/conda-skills/tutorials/build-a-skill-package/)
- [Watch the demos](https://jezdez.github.io/conda-skills/demos/)
- [Package a skill](https://jezdez.github.io/conda-skills/how-to/package-a-skill/)
- [Commands](https://jezdez.github.io/conda-skills/reference/commands/) and [JSON output](https://jezdez.github.io/conda-skills/reference/json/)
- [How agents find skills](https://jezdez.github.io/conda-skills/explanation/agent-discovery/)
- [Skill safety](https://jezdez.github.io/conda-skills/explanation/skill-safety/)
- [Troubleshooting](https://jezdez.github.io/conda-skills/how-to/troubleshooting/)

The default destination is `.agents/skills/` under the current directory. Use `--backend claude` for `.claude/skills/` and `--global` for your home directory. Read skill content before exposing it to an agent. The plugin does not execute instructions or verify their trustworthiness.

## Development

Development environments and tasks live in the root `conda.toml`, with resolved dependencies in `conda.lock`. Install conda-workspaces, then install each environment before running its tasks:

```sh
conda install -n base --yes --override-channels -c conda-forge 'conda>=26.9' 'conda-workspaces>=0.12'
conda workspace install --locked -e default
conda task run -e default check
conda workspace install --locked -e docs
conda task run -e docs docs
```

See [Contributing](https://jezdez.github.io/conda-skills/contributing/), [Releasing conda-skills](https://jezdez.github.io/conda-skills/releasing/), and the [Changelog](https://jezdez.github.io/conda-skills/changelog/). The Docs workflow checks pull requests and deploys documentation from `main` to [GitHub Pages](https://jezdez.github.io/conda-skills/).

## License

Original code is licensed under [Apache-2.0](LICENSE).
