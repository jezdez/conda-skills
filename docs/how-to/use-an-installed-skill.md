# Use an installed skill

Use this guide when a conda environment already contains a skill package and `conda skill --help` works. If you are trying skills for the first time, start with {doc}`../tutorials/skill-forge`.

## Find and review it

With the environment containing your skill packages active, list its skills:

```sh
conda skill list
```

Open `SKILL.md` in the reported directory and inspect any supporting files in your editor. Package ownership tells you where the files came from, not whether their instructions are appropriate. The commands below use `review-notes` as an example name. Substitute a name from your listing.

You can inspect the files without finding their paths yourself:

```sh
conda skill inspect review-notes
conda skill inspect review-notes --file SKILL.md
```

The first command lists the skill's metadata and file tree. Use a relative path from the tree with `--file` to read a supporting text file. Binary and oversized files are not printed. To examine the whole directory in your usual tools:

```sh
conda skill open review-notes
```

This opens the directory in the system file manager, not an individual packaged script or document. It requires a graphical desktop. Both commands use the active source environment by default and accept `-n`/`-p` overrides.

## Make it available to your project

Run from the project root. The tabs select the link's destination directory:

- `.agents/skills/` is the shared convention used by multiple clients, not an agent named "Agents". It is the default destination and requires your client to support that path.
- `.claude/skills/` is the Claude-specific convention, selected with `--backend claude`.

See the [Agent Skills Client Showcase](https://agentskills.io/clients) for supporting agents, then choose the path your agent documents. Format support does not guarantee that it scans `.agents/skills/`. The [integration guide](https://agentskills.io/integrate-skills#where-to-scan) explains that convention, and {doc}`../explanation/agent-discovery` describes how conda-skills uses it.

::::{tab-set}

:::{tab-item} Shared (.agents/skills/)
:sync: backend-agents

```sh
conda skill link review-notes
conda skill status
```

This creates `.agents/skills/review-notes` as a directory symlink. It leaves the package files in the active environment. The plugin does not launch your agent or change its configuration, so check that your agent supports this directory convention.

:::

:::{tab-item} Claude (.claude/skills/)
:sync: backend-claude

```sh
conda skill link review-notes --backend claude
conda skill status --backend claude
```

This creates `.claude/skills/review-notes`. Specify the backend on both commands. The plugin does not launch Claude or change its configuration.

:::

::::

To make the skill available through your home directory, pass `--global` explicitly to `link` and `status`. Source selection and destination scope are independent. See {doc}`../explanation/agent-discovery`.

## Use the interactive guide instead

Run `conda skill quickstart` with your skill environment active. Choose `link`, then enter one or more skill numbers separated by spaces or commas, or `all`. Review every selected source and its supporting files, then choose the backend and scope. The guide previews all destinations and asks for confirmation before linking. It does not remove unselected skills.

To inspect both supported destination directories, run `conda skill status --all`. Add `--global` to inspect both home directories instead. The standard single-directory view remains available with `status` or `status --backend claude`.

Home changes require starting the guide with `--global`. Choosing home in a menu does not replace that flag. The guide needs an interactive terminal and rejects JSON mode. It does not install packages or create environments. Use the explicit commands above in scripts.

## Remove the project link

::::{tab-set}

:::{tab-item} Shared (.agents/skills/)
:sync: backend-agents

```sh
conda skill unlink review-notes
```

:::

:::{tab-item} Claude (.claude/skills/)
:sync: backend-claude

```sh
conda skill unlink review-notes --backend claude
```

:::

::::

Use the same backend and `--global` setting you used for linking. You do not need to activate the original environment: unlinking checks the destination symlink's target against conda package records and deletes only the link, not the package. If the target cannot be verified, follow {doc}`troubleshooting` to inspect it before using `--force`. An absent destination succeeds without looking up a source.

(remove-a-skill-completely)=
## Remove a skill completely

Unlink the skill from the projects and home directories where you use it, then uninstall its package with conda. These are separate operations because a package can supply several skills or software, and other projects may still link to its files.

First, use `conda skill list` in the source environment to find the package name. Do not infer it from the skill name. For the tutorial's `polars` skill, the owning package is `agent-skill-polars`:

```sh
conda skill list
conda skill unlink polars
conda remove agent-skill-polars
```

Run `unlink` from each project's root with the backend originally used. Add `--global` for a home-directory link and `--backend claude` for the Claude directory. Stop or reload affected agent sessions according to the client's instructions, since removing a link does not clear instructions already loaded.

`conda remove` acts on the active environment. If the source package is in another environment, target it explicitly:

```sh
conda remove -n skills agent-skill-polars
```

Substitute the actual source environment and package. Review conda's transaction plan before confirming, especially if the package supplies other skills or has dependents. Conda-skills does not track all project links, and uninstalling the package does not clean them up automatically. There is no `unlink --remove` option.

If the package is already gone, inspect each affected destination with `conda skill status`. After confirming it is the stale symlink you intend to remove:

```sh
conda skill unlink polars --force
```

Use the original backend and scope. `--force` skips source verification only. It still refuses regular files, directories, and redirected parent paths, and it never removes package files. See {doc}`troubleshooting` for further inspection steps.

These conda commands work the same way in PowerShell and POSIX shells. Creating a directory link on Windows requires Developer Mode or suitable privileges. Do not substitute recursive filesystem deletion for unlinking.

## Advanced: select a separate source

To keep skill packages in another environment without activating it, override the source on `list` and `link`. For an existing environment named `skill-env`, run:

```sh
conda skill list -n skill-env
```

Review the files at the reported path, then link the chosen skill:

```sh
conda skill link review-notes -n skill-env
```

Use `-p /path/to/environment` instead of `-n skill-env` to select by path. The same overrides work for quickstart's installed-skill branch. Keep the plugin in the environment that owns conda. The separate source does not need its own plugin or Python installation. Unlinking still uses only the destination name, backend, and scope, with no source override.

See {doc}`../reference/commands` for all options, and {doc}`../demos` for a recording of this sequence.
