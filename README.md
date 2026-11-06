# conda-skills

`conda skill` makes skills from conda packages available to your agent through directory links in a project or your home directory. Conda manages the package versions; you choose which skills to use.

Inspired by Pavel Zwerschke's [pixi-skills](https://github.com/pavelzw/pixi-skills) and [skill-forge](https://github.com/pavelzw/skill-forge), conda-skills brings the same package-manager approach to conda's Python stack. See [prior art](docs/explanation/prior-art.md) for the background and shared conventions.

The project is unreleased and requires Python 3.11 or newer and conda 26.9 or newer. Install conda through a conda distribution, not PyPI. Python package versions come from Git through Hatchling and hatch-vcs; the conda recipe's current release candidate is `0.1.0`.

## Installation

After the first release, install into the environment that runs conda, usually `base`:

```sh
conda install -n base --override-channels -c jezdez -c conda-forge conda-skills
conda skill --help
```

Until the package is available on the channel or PyPI, install from a checkout with `conda-pypi` in the environment that runs conda:

```sh
conda install -n base --override-channels -c conda-forge "conda-pypi>=0.12" "hatchling>=1.27" "hatch-vcs>=0.4" "rich>=13" "ruamel.yaml>=0.11.14,<0.20"
conda pypi install -n base -e .
conda skill --help
```

Run these commands from the repository root. The first supplies build requirements and runtime dependencies, which editable installs do not resolve. If another prefix owns your conda executable, replace `-n base` with `-p /path/to/conda-prefix` in both commands.

The [first-use tutorial](docs/tutorials/first-skill.md) takes you from building a local example package to installing it in a separate source environment, linking it, and removing the link.

See [installation](docs/how-to/installation.md) for PyPI and local-artifact alternatives. Installing the plugin in an unrelated environment does not register it with another conda executable.

## Documentation

- [Documentation home](https://jezdez.github.io/conda-skills/)
- [Install conda-skills](docs/how-to/installation.md)
- [Use a skill from skill-forge](docs/tutorials/skill-forge.md)
- [Manage reproducible project skills](docs/how-to/project-skills.md)
- [Update and pin skills](docs/how-to/update-skills.md)
- [Build a skill locally](docs/tutorials/first-skill.md)
- [Watch the demos](docs/demos.md)
- [Package a skill](docs/how-to/package-a-skill.md)
- [Commands](docs/reference/commands.md) and [JSON output](docs/reference/json.md)
- [Source environments and destination scope](docs/explanation/scope.md)
- [Package ownership and trust](docs/explanation/ownership-and-trust.md)
- [Troubleshooting](docs/how-to/troubleshooting.md)

The default destination is `.agents/skills/` under the current directory. `--backend claude` selects `.claude/skills/`; `--global` uses your home directory. Read skill content before exposing it to an agent. The plugin does not execute instructions or verify their trustworthiness.

## Development

Development environments and tasks live in the root `conda.toml`, with resolved dependencies in `conda.lock`. Install conda-workspaces, then install each environment before running its tasks:

```sh
conda install -n base --yes --override-channels -c conda-forge 'conda>=26.9' 'conda-workspaces>=0.12'
conda workspace install --locked -e default
conda task run -e default check
conda workspace install --locked -e docs
conda task run -e docs docs
```

See [Contributing](CONTRIBUTING.md), [Release preparation](RELEASING.md), and the [Changelog](CHANGELOG.md). The Docs workflow checks pull requests and deploys documentation from `main` to [GitHub Pages](https://jezdez.github.io/conda-skills/).

## License

Original code is licensed under [Apache-2.0](LICENSE).
