# Install conda-skills

Install the plugin into the environment that runs conda, usually `base`. It requires Python 3.11 or newer and conda 26.9 or newer. An environment that only stores skill packages does not need the plugin.

The commands below use `-n base` for a standard conda installation. If your conda executable belongs to another prefix, replace `-n base` with `-p /path/to/conda-prefix` throughout, using its actual path.

Start with the conda channel instructions below. If the package version you need is unavailable, use a [local package](#use-a-local-conda-package) or [checkout](#install-an-unpublished-checkout). The other sections are alternative installation methods, not steps you need to follow in sequence.

## Install from the jezdez channel

For published releases, use the `jezdez` channel, with dependencies supplied by conda-forge.

```sh
conda install -n base --override-channels -c jezdez -c conda-forge conda-skills
conda skill --help
```

The `main` label is the default for `-c jezdez`, so no `/label/main` suffix is needed.

## Install from PyPI with conda-pypi

Install `conda-pypi` in the environment that runs conda, then use it to install a published wheel:

```sh
conda install -n base --override-channels -c conda-forge "conda-pypi>=0.12"
conda pypi install -n base conda-skills
conda skill --help
```

The command searches configured conda channels first, then converts missing wheels from PyPI, including dependencies. Conda itself must already be installed.

:::{note}
Upstream marks `conda pypi install` for package installs as pending deprecation and recommends `conda install` with its wheel channel and Rattler solver configuration. See the [conda-pypi quickstart](https://conda.github.io/conda-pypi/quickstart/) for that alternative. The editable `-e` workflow below remains supported.
:::

(use-a-local-conda-package)=
## Use a local conda package

If you have built the plugin's recipe, substitute its actual artifact path:

```sh
conda install -n base --override-channels -c conda-forge /path/to/conda-skills-0.1.0-BUILD.conda
conda skill --help
```

Replace `BUILD` with the filename's build string. See {doc}`../contributing` to build your own artifact. Installing it locally does not upload it.

(install-an-unpublished-checkout)=
## Install from a checkout

Check the path and version of your conda installation:

```sh
conda info --base
conda --version
```

Then run from the checkout root, adjusting the target if needed:

```sh
conda run -n base python --version
conda install -n base --override-channels -c conda-forge "conda-pypi>=0.12" "hatchling>=1.27" "hatch-vcs>=0.4" "rich>=13" "ruamel.yaml>=0.11.14,<0.20"
conda pypi install -n base -e .
conda skill --help
```

Check that the reported Python and conda versions meet the requirements above. `conda-pypi` 0.12 fixes explicit `--name` and `--prefix` selection. An editable installation reads Python source from the checkout, so keep it at the same path.

Editable installs do not resolve runtime dependencies. The first command supplies `rich` and `ruamel.yaml`, plus Hatchling and hatch-vcs for the build. Conda-pypi builds a PEP 660 editable wheel and installs it as a conda package. Only install a checkout whose build code you trust.

To preview the checkout path and target environment without building or installing:

```sh
conda pypi install -n base --dry-run -e .
```

This preview does not validate the build or its dependencies.

## Prepare your agent's directories

The `agents` backend uses `.agents/skills/`, and the `claude` backend uses `.claude/skills/`. The plugin only manages filesystem links. Consult your agent's documentation for whether it reads those paths and when it reloads skills.

On Windows, directory symlinks require Developer Mode or suitable privileges. Enable these under your organization's policy before following the tutorial. If symlink creation fails, the plugin reports the error without copying directories as a fallback.

Continue with {doc}`../tutorials/skill-forge` to try one skill. If conda does not recognize a command, see {doc}`troubleshooting`.
