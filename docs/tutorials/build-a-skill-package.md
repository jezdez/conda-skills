# Build and try a skill package

For a short preview, watch {doc}`../demos`. The steps below include the package setup omitted from the recording.

Give your project a skill for organizing code-review findings. You will build a small package, install it in a separate conda environment, and create a symlink to its skill directory in a temporary project. The example contains instructions and no executable script. You do not need an agent client to follow along, so it can sit this one out.

## Before you start

Start with a checkout of this repository and a conda installation where `conda skill --help` works. If you need to install the plugin, follow {doc}`../how-to/installation` for your usual conda command. Install conda-workspaces for the package-build tooling:

```sh
conda install -n base --yes --override-channels -c conda-forge 'conda>=26.9' 'conda-workspaces>=0.12'
```

If another prefix owns your conda executable, replace `-n base` with `-p /path/to/conda-prefix`. Setting up the locked build environment requires network access.

On Windows, enable Developer Mode or use an account with directory-symlink privileges. Use the PowerShell tab where commands differ. On macOS or Linux, use the POSIX tab. Start in the repository root. The commands create a new temporary directory, so they do not change your existing projects or home-directory skills.

## Read and build the example

Read the complete source skill before building it:

```{literalinclude} ../examples/review-notes/SKILL.md
:language: markdown
```

Its directory name and frontmatter name are both `review-notes`. The conda package name is different: `conda-skills-example`. Commands that select a skill use the skill name.

Build the example package from the checkout root:

```sh
conda workspace install --locked -e build
conda task run -e build build-example
```

The recipe fixes the version and build string, producing `conda-dist/noarch/conda-skills-example-0.1.0-0.conda`. You will install this local file, so you do not need a public channel with the example package. The build downloads Python, but the skill itself has no runtime dependencies. See {doc}`../how-to/package-a-skill` for the recipe and installed layout.

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

Look for `review-notes` from package `conda-skills-example`, version `0.1.0`. The table also shows its description and source path under `source-env/share/agent-skills/review-notes`. The plugin finds it through conda's record of the installed `SKILL.md`. Copying the folder into the prefix by hand would not create package ownership.

## Link and inspect

From the temporary project, run:

```sh
conda skill install review-notes -p ../source-env
conda skill status
```

You should see `Linked review-notes at` followed by the project's absolute `.agents/skills/review-notes` path, then a status entry marked `linked`. The link points at the complete source directory: reading `.agents/skills/review-notes/SKILL.md` reads the packaged file.

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

You should see `Removed link for review-notes.`, followed by `No skill entries found.` The final list still contains the source skill because removing a link does not uninstall its package.

After unlinking, delete the temporary source environment:

```sh
conda remove --yes --prefix ../source-env --all
```

Leave the temporary project directory before deleting the tutorial directory with your file manager. Only remove the temporary directory created in this tutorial. The built package remains under the checkout's `conda-dist/` and can be reused.

For links in your home directory or the Claude backend, read {doc}`../explanation/agent-discovery`. To start your own skill with `conda skill init`, continue with {doc}`../how-to/create-a-skill`, then use {doc}`../how-to/package-a-skill` when you are ready to build it.
