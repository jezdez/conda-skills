# Manage project skills with conda-workspaces

Keep the skill packages for a project in a dedicated workspace environment, record their resolved packages in `conda.lock`, and expose only the skills you have reviewed. This guide uses `agent-skill-polars` version `0.0.8` from skill-forge, which contains the skill named `polars`.

## Prepare the tools

Install `conda-skills` in the environment that owns your conda executable, usually `base`, following {doc}`installation`. Until the plugin's first public release, use its local-package or conda-pypi checkout instructions. The availability of a skill package on skill-forge does not imply that `conda-skills` is published there.

Install conda-workspaces in that same conda-owning environment:

```sh
conda install -n base --override-channels -c conda-forge "conda>=26.9" "conda-workspaces>=0.12"
conda workspace --help
conda skill --help
```

If conda belongs to a different environment, replace `-n base` with `-p` followed by its actual prefix. The workspace's `skills` environment will hold skill packages; it does not need its own copy of either plugin or conda. You do not need to activate it.

Choose a project directory where you can create links. On Windows, directory symlinks require Developer Mode or suitable privileges. Check your agent client's documentation for support of `.agents/skills/` or `.claude/skills/` and its reload behavior.

## Declare the skill package

Run the remaining commands from the project root. For this example, the project root is also the workspace root, containing `conda.toml`:

```toml
[workspace]
name = "polars-project"
channels = ["https://prefix.dev/skill-forge", "conda-forge"]
platforms = ["linux-64", "osx-arm64", "win-64"]

[feature.skills.dependencies]
agent-skill-polars = "==0.0.8"

[environments]
skills = ["skills"]
```

If the project already has a manifest, merge the feature and environment into it rather than replacing the file. Retain its existing dependencies and required channels. An environment includes the default feature unless you explicitly exclude it, so an existing top-level `[dependencies]` table also contributes packages to `skills`.

To keep those default dependencies out of a skills-only environment, use this environment definition instead:

```toml
[environments]
skills = { features = ["skills"], no-default-feature = true }
```

The three platforms target Linux x86-64, Apple Silicon macOS, and Windows x86-64. Adjust them to your team's machines; Intel macOS uses `osx-64`. Solving for a platform does not test the skill or its supporting programs on that platform.

`==0.0.8` pins the skill package's version. It does not pin a Polars library version or a particular package build. See {doc}`update-skills` for the difference between version pins and a lockfile.

## Resolve and install the environment

Use libmamba for this example. The Rattler solver can fail on the channel's attestation metadata with `Object of type bytes is not JSON serializable`. In a dedicated shell, select libmamba for workspace operations without changing your saved conda configuration:

::::{tab-set}

:::{tab-item} POSIX

```sh
export CONDA_SOLVER=libmamba
```

:::

:::{tab-item} PowerShell

```powershell
$env:CONDA_SOLVER = "libmamba"
```

:::

::::

The setting lasts for this shell session and its child processes. Close the dedicated shell when finished. From the project root, generate the lockfile:

```sh
conda workspace lock
```

This solves the declared environments for their platforms and writes `conda.lock` without installing them. Inspect the lockfile before proceeding. Check package URLs, versions, builds, hashes, and dependencies, including any packages added beyond `agent-skill-polars`. The channel list determines where conda looks for packages; it is not a publisher approval list.

Then install the locked selection for your current platform:

```sh
conda workspace install --locked -e skills
conda skill list -p .conda/envs/skills
```

The default workspace environment path is `.conda/envs/skills`. If the manifest changes `workspace.envs-dir`, use the corresponding path in every `conda skill` command. `--locked` requires a lockfile that satisfies the manifest; it fails rather than silently replacing a missing or stale lockfile.

The skill listing should identify `polars`, its owning package `agent-skill-polars`, version `0.0.8`, and its installed directory. This is package discovery, before any project link exists. If the package appears in `conda list -p .conda/envs/skills` but the skill is missing, check {doc}`troubleshooting` and {doc}`../reference/skill-format`.

## Review the files and create the project link

Open `.conda/envs/skills/share/agent-skills/polars/SKILL.md` in your editor. Read the full instructions and inspect every companion file in that directory, including references and scripts. Assess any requested commands, network access, credentials, and extra installations against the work you intend the agent to do. Do not run a script merely to inspect it.

After accepting the content, run from the project root:

```sh
conda skill install polars -p .conda/envs/skills
conda skill status
```

The result is a directory symlink at `.agents/skills/polars`, pointing into the workspace environment. The `linked` state confirms the filesystem entry exists and leads to a directory containing `SKILL.md`. It does not show that an agent loaded or used the skill.

For a client using Claude's directory convention, use the same backend on installation and status:

```sh
conda skill install polars -p .conda/envs/skills --backend claude
conda skill status --backend claude
```

This uses `.claude/skills/polars`. Choose the backend your client supports; installing both is unnecessary unless you use both locations. Open the project in the client and follow its documented reload procedure. Neither command changes the client's configuration or starts an agent session.

The `-p` option selects the source environment. It does not select the project directory. Running these commands from another directory changes both the meaning of the relative source path and the default link destination. Home-directory links require explicit `--global`; see {doc}`../explanation/scope`.

## Share the setup

Keep `conda.toml` and the reviewed `conda.lock` in version control. Each collaborator installs the locked environment, reviews the installed content, and creates the appropriate local link. Do not commit the `.conda/` environment directory. Decide separately whether your repository tracks client links; a tracked link does not provision its target, and each checkout still needs the environment.

Use `conda workspace install --locked -e skills` for routine reproduction. Do not regenerate the lock on every setup: a fresh solve can select different builds or dependency versions within the manifest constraints. Follow {doc}`update-skills` when deliberately changing the selection.

Installing or linking the skill does not choose the environment in which an agent runs Python. Put your application's Polars library dependency in the environment used for your code, and configure the client to run that environment's tools. Package dependencies and library compatibility are explained in {doc}`../explanation/packages-and-discovery`.

## Remove the setup

Before removing the package, deleting the environment, or moving it independently of the project, remove the project link while its source still exists:

```sh
conda skill remove polars -p .conda/envs/skills
conda skill status
```

Use `--backend claude` if that was the destination. Repeat removal in any other projects or home scope that use this source, with explicit `--global` for home links. There is no central registry of all links.

To stop installing this package, remove its dependency from `conda.toml`, regenerate and review `conda.lock`, then run `conda workspace install --locked -e skills`. Retain the environment definition if you still need other skill packages. If you only remove the project link, the package remains installed and available for later review and relinking.

If the source has already gone, `conda skill status` still works, but normal removal cannot rediscover the original skill. Follow {doc}`troubleshooting` to inspect and remove the stale symlink without deleting unrelated files.
