# conda-skills

`conda skill` finds agent skills installed by conda and creates directory links so your agent can use them in a project or from your home directory. Conda manages the package versions; you choose which skills to make available.

This is unreleased development software; no public package release is available yet. Python package versions come from Git through Hatchling and hatch-vcs. The conda recipe's current release candidate is `0.1.0`. It requires Python 3.11 or newer and conda 26.9 or newer. Conda must come from a conda installation, not PyPI.

## Installation

After the first release, install into the environment that runs conda, usually `base`:

```sh
conda install -n base --override-channels -c jezdez -c conda-forge conda-skills
conda skill --help
```

This package is not yet available on the channel or PyPI. Until it is published, install from a checkout with `conda-pypi` in the environment that runs conda:

```sh
conda install -n base --override-channels -c conda-forge "conda-pypi>=0.12" "hatchling>=1.27" "hatch-vcs>=0.4" "rich>=13" "ruamel.yaml>=0.11.14,<0.20"
conda pypi install -n base -e .
conda skill --help
```

Run the checkout commands from this repository root. The first command supplies build requirements and runtime dependencies; editable installs do not resolve runtime dependencies. If another prefix owns your conda executable, replace `-n base` with `-p /path/to/conda-prefix` in both commands. The [first-use tutorial](docs/tutorials/first-skill.md) builds a supplied example package locally, installs it in a separate source environment, and walks through linking and removal.

See [installation](docs/how-to/installation.md) for PyPI and local-artifact alternatives. Installing the plugin in an unrelated environment does not register it with another conda executable.

## Documentation

- [Documentation home](docs/index.md)
- [Install conda-skills](docs/how-to/installation.md)
- [Set up a skill for your agent](docs/tutorials/first-skill.md)
- [Package a skill](docs/how-to/package-a-skill.md)
- [Commands](docs/reference/commands.md) and [JSON output](docs/reference/json.md)
- [Source environments and destination scope](docs/explanation/scope.md)
- [Package ownership and trust](docs/explanation/ownership-and-trust.md)
- [Troubleshooting](docs/how-to/troubleshooting.md)

The default destination is `.agents/skills/` under the current directory. `--backend claude` selects `.claude/skills/`; `--global` uses your home directory. Read skill content before exposing it to an agent. The plugin does not execute instructions or verify their trustworthiness.

## Development

The root `conda.toml` defines the development environments and tasks; `conda.lock` records their resolved dependencies. Bootstrap conda-workspaces, then install each environment before running its tasks:

```sh
conda install -n base --yes --override-channels -c conda-forge 'conda>=26.9' 'conda-workspaces>=0.12'
conda workspace install --locked -e default
conda task run -e default check
conda workspace install --locked -e docs
conda task run -e docs docs
```

See [Contributing](CONTRIBUTING.md), [Release preparation](RELEASING.md), and the [Changelog](CHANGELOG.md). Documentation builds locally; no public documentation URL is configured.

## License and prior art

Original code is licensed under [Apache-2.0](LICENSE). The idea of distributing skills through a package manager comes from Pavel Zwerschke's [Managing Agent Skills with Your Package Manager](https://pavel.pink/blog/pixi-skills). This project uses conda environments instead of Pixi workspace discovery and does not bundle pixi-skills source code.
