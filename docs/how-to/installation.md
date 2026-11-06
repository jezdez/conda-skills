# Install conda-skills

The plugin requires Python 3.11 or newer and conda 26.9 or newer. Install it into the environment that runs conda, usually `base`, rather than an environment that only stores skill packages.

The commands below use `-n base` for a standard conda installation. If your conda executable belongs to another prefix, replace `-n base` with `-p /path/to/conda-prefix` throughout, using its actual path.

## Install from the jezdez channel

Releases will go to the `jezdez` channel, with dependencies supplied by conda-forge.

:::{warning}
As checked on November 6, 2026, `conda-skills` is not yet published on anaconda.org or PyPI. The following channel and PyPI commands are for use after the first release. Until then, use a local package or the checkout instructions below.
:::

```sh
conda install -n base --override-channels -c jezdez -c conda-forge conda-skills
conda skill --help
```

The `main` label is the default for `-c jezdez`; no `/label/main` suffix is needed. The release plan does not include conda-forge or a canary label.

## Install from PyPI with conda-pypi

After the first PyPI release, `conda-pypi` can convert the wheel into a conda package. Install `conda-pypi` from conda-forge into the environment that runs conda first:

```sh
conda install -n base --override-channels -c conda-forge "conda-pypi>=0.12"
conda pypi install -n base conda-skills
conda skill --help
```

This command searches configured conda channels first, then converts missing wheels from PyPI, including dependencies. Conda itself remains an external prerequisite supplied by a conda distribution or channel.

:::{note}
Upstream marks `conda pypi install` for package installs as pending deprecation and recommends `conda install` with its wheel channel and Rattler solver configuration. See the [conda-pypi quickstart](https://conda.github.io/conda-pypi/quickstart/) for that alternative. The editable `-e` workflow below remains supported. Prefer the project's `jezdez` conda package when it becomes available.
:::

## Use a local conda package

If you have built the plugin's recipe, substitute its actual artifact path:

```sh
conda install -n base --override-channels -c conda-forge /path/to/conda-skills-0.1.0-BUILD.conda
conda skill --help
```

`BUILD` is a placeholder for the build string in the filename. See {doc}`../contributing` for building artifacts; installing a local artifact does not upload it.

## Install an unpublished checkout

Identify the environment that owns the conda executable you intend to use. In a standard conda installation this is `base`, whose path is printed by:

```sh
conda info --base
conda --version
```

From the checkout root, for a standard installation:

```sh
conda run -n base python --version
conda install -n base --override-channels -c conda-forge "conda-pypi>=0.12" "hatchling>=1.27" "hatch-vcs>=0.4" "rich>=13" "ruamel.yaml>=0.11.14,<0.20"
conda pypi install -n base -e .
conda skill --help
```

Check the reported Python and conda versions against the minimum requirements before installing. Use `conda-pypi` 0.12 or newer, which fixes explicit `--name` and `--prefix` selection. An editable installation continues to read Python source from the checkout; keep the checkout at the same path.

`conda-pypi` builds a PEP 660 editable wheel and installs it as a conda package. That editable installation does not resolve runtime dependencies, so the `conda install` command supplies `rich` and `ruamel.yaml` explicitly, along with the Hatchling and hatch-vcs build requirements. Only install a checkout whose build code you trust.

Hatchling and hatch-vcs derive the Python package version from Git. Untagged or modified checkouts can produce development versions. The `0.1.0` fallback for source without usable version metadata is only for development; it does not indicate a published release. The local conda recipe uses its own candidate version, currently `0.1.0`, for both conda and Python package metadata.

To preview the checkout path and target environment without building or installing:

```sh
conda pypi install -n base --dry-run -e .
```

This preview does not validate the build or its dependencies.

## Prepare your agent's directories

The `agents` backend uses `.agents/skills/`; the `claude` backend uses `.claude/skills/`. The plugin only manages filesystem links. Consult your agent's documentation for whether it reads those paths and when it reloads skills.

On Windows, directory symlinks require Developer Mode or suitable privileges. Enable these under your organization's policy before following the tutorial. If symlink creation fails, the plugin reports the error without copying directories as a fallback.

Continue with {doc}`../tutorials/first-skill`, which builds a local example instead of assuming a skill package is available from a public channel. For an unrecognized command, see {doc}`troubleshooting`.
