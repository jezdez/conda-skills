# Set up a skill for your agent

Set up a project so your agent can find instructions for organizing code-review findings. You will build a small skill package, install it into a separate conda environment, and create a symlink in a temporary project that points to the packaged skill directory. The example contains instructions, with no executable script. You can follow these steps without an agent client.

## Before you start

You need this repository checkout, [Pixi](https://pixi.sh), and a conda installation in which `conda skill --help` works. Follow {doc}`../how-to/installation` to install the plugin into the environment that runs your usual conda command. You will run that conda command outside Pixi. Setting up the locked build environment requires network access.

On Windows, enable Developer Mode or use an account with directory-symlink privileges. Use the PowerShell tab where commands differ. On macOS or Linux, use the POSIX tab. Start in the repository root. The commands create a new temporary directory, so they do not change your existing projects or home-directory skills.

## Read and build the example

Read the complete source skill before building it:

```{literalinclude} ../examples/review-notes/SKILL.md
:language: markdown
```

Its directory name and frontmatter name are both `review-notes`. The conda package name is different: `conda-skills-example`. Commands that select a skill use the skill name.

Build the example package from the checkout root:

```sh
pixi run --locked -e build rattler-build build --recipe docs/examples/recipe/recipe.yaml --output-dir conda-dist -c conda-forge
```

The recipe fixes the example version and build string, so the package file is `conda-dist/noarch/conda-skills-example-0.1.0-0.conda`. You will install this local file; these steps do not depend on the example being available on a public channel. The build downloads Python to build the package. The skill itself has no runtime dependencies. See {doc}`../how-to/package-a-skill` for the recipe and installed layout.

## Create a source environment and project

Starting in the checkout root, install the local package into a new environment, create a project beside it, and enter the project.

::::{tab-set}

:::{tab-item} POSIX

```sh
tutorial_root=$(mktemp -d)
conda create --yes --prefix "$tutorial_root/source-env" ./conda-dist/noarch/conda-skills-example-0.1.0-0.conda
mkdir "$tutorial_root/project"
cd "$tutorial_root/project"
```
:::

:::{tab-item} PowerShell

```powershell
$tutorialRoot = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $tutorialRoot | Out-Null
conda create --yes --prefix "$tutorialRoot/source-env" ./conda-dist/noarch/conda-skills-example-0.1.0-0.conda
New-Item -ItemType Directory -Path "$tutorialRoot/project" | Out-Null
Set-Location "$tutorialRoot/project"
```
:::

::::

You do not need to activate the source environment. The `-p` option selects it independently of the conda executable that runs the plugin:

```sh
conda skill list -p ../source-env
```

The table shows `review-notes`, package `conda-skills-example`, version `0.1.0`, its description, and its source path under `source-env/share/agent-skills/review-notes`. The plugin finds the skill because conda recorded the package's `SKILL.md` during installation. Copying the same folder into the prefix by hand would not create package ownership.

## Link and inspect

From the temporary project, run:

```sh
conda skill install review-notes -p ../source-env
conda skill status
```

The install command reports `Linked review-notes at` followed by the project's absolute `.agents/skills/review-notes` path. Status reports that entry as `linked`. The link points at the complete source directory, so reading `.agents/skills/review-notes/SKILL.md` reads the packaged file.

Running the install command again reuses the matching link:

```sh
conda skill install review-notes -p ../source-env
conda skill status --json
```

The JSON result is an array with one entry. Its `name` is `review-notes`, its `state` is `linked`, and its `target` is the resolved source directory. Absolute paths vary by machine. See {doc}`../reference/json` for every field's definition.

`linked` describes the filesystem, not trust or successful agent-client discovery. Review the source before opening this project in an agent, and use that client's documentation to check its skill-loading behavior.

## Remove the link before the source

```sh
conda skill remove review-notes -p ../source-env
conda skill status
conda skill list -p ../source-env
```

Removal reports `Removed link for review-notes.` Status now says `No skill entries found.` The final list still contains the source skill: removing a link does not uninstall a package.

After unlinking, delete the temporary source environment:

```sh
conda remove --yes --prefix ../source-env --all
```

Leave the temporary project directory before deleting the tutorial directory with your file manager. Only remove the temporary directory created in this tutorial. The built package remains under the checkout's `conda-dist/` and can be reused.

For links in your home directory or the Claude backend, read {doc}`../explanation/scope`. To adapt the example to your own package, continue with {doc}`../how-to/package-a-skill`.
