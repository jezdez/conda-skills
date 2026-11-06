# Use an installed skill

Use this guide when a conda environment already contains a skill package and `conda skill --help` works. If you are trying skills for the first time, start with {doc}`../tutorials/skill-forge`.

## Find and review it

List skills in the source environment, using its actual name:

```sh
conda skill list -n skill-env
```

Open the reported `SKILL.md` and any supporting files in your editor. Package ownership tells you where the files came from, not whether their instructions are appropriate. The commands below use `review-notes` as an example name. Substitute a name from your listing.

## Make it available to your project

Run from the project root. Choose the directory convention your client supports:

::::{tab-set}

:::{tab-item} Agents
:sync: backend-agents

```sh
conda skill install review-notes -n skill-env
conda skill status
```

This creates `.agents/skills/review-notes` as a directory symlink. It leaves the package files in `skill-env`. The plugin does not launch your agent or change its configuration, so check that your agent supports this directory convention.

:::

:::{tab-item} Claude
:sync: backend-claude

```sh
conda skill install review-notes -n skill-env --backend claude
conda skill status --backend claude
```

This creates `.claude/skills/review-notes`. Specify the backend on both commands. The plugin does not launch Claude or change its configuration.

:::

::::

To make the skill available through your home directory, pass `--global` explicitly to `install` and `status`. Use `-p /path/to/environment` instead of `-n skill-env` when selecting a source by path. Source selection and destination scope are independent. See {doc}`../explanation/agent-discovery`.

## Use the interactive guide instead

Run `conda skill quickstart -n skill-env` or use `-p /path/to/environment` to select the source. Choose `link`, then enter one or more skill numbers separated by spaces or commas, or `all`. Review every selected source and its supporting files, then choose the backend and scope. The guide previews all destinations and asks for confirmation before linking. It does not remove unselected skills.

To inspect both supported destination directories, run `conda skill status --all`. Add `--global` to inspect both home directories instead. The standard single-directory view remains available with `status` or `status --backend claude`.

Home changes require starting the guide with `--global`. Choosing home in a menu does not replace that flag. The guide needs an interactive terminal and rejects JSON mode. It does not install packages or create environments. Use the explicit commands above in scripts.

## Remove the project link

::::{tab-set}

:::{tab-item} Agents
:sync: backend-agents

```sh
conda skill remove review-notes -n skill-env
```

:::

:::{tab-item} Claude
:sync: backend-claude

```sh
conda skill remove review-notes -n skill-env --backend claude
```

:::

::::

Use the same backend and `--global` setting you used for installation. Removal deletes only a matching symlink, not the package. If the source environment has been removed or moved, follow {doc}`troubleshooting` to inspect and remove a stale link safely.

See {doc}`../reference/commands` for all options, and {doc}`../demos` for a recording of this sequence.
