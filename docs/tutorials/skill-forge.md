# Try your first skill

Try a skill containing instructions for Polars, a Python data library. You will download it, review the instructions, connect it to a project, and remove the link. You do not need Polars installed to practice these steps.

The skill comes from Pavel Zwerschke's [skill-forge channel](https://prefix.dev/channels/skill-forge). A channel is a place conda downloads packages from. You will use conda to get the files and conda-skills to connect them to your project.

## Before you start

Install the plugin in the environment that owns your conda command, usually `base`, as described in {doc}`../how-to/installation`. Do this before activating the tutorial environment, then check `conda skill --help`. You also need network access to download the example.

Use a shell initialized for conda: `conda activate` needs conda's shell integration, not just an executable on `PATH`. If necessary, follow your conda installation's shell initialization instructions and reopen the terminal. In a standard initialized shell, the `conda` shell function continues to call the base conda executable after activation, so the tutorial environment does not need its own plugin installation.

Run `conda env list` and check that `skill-demo` is unused. If that name already exists, choose a new, unused name and substitute it in every creation, activation, and cleanup command below. Do not reuse an existing environment for this tutorial.

On Windows, directory links require Developer Mode or appropriate privileges. Check your organization's policy before enabling them.

Create a new, empty folder named `skill-forge-tutorial` using your file manager. Inside it, create `project` and open your terminal there:

```text
skill-forge-tutorial/
  project/       # run the following commands here
```

## 1. Get the skill

Create and activate the new environment in Bash, zsh, or PowerShell:

```sh
conda create -n skill-demo --override-channels -c https://prefix.dev/skill-forge -c conda-forge "agent-skill-polars==0.0.8"
conda activate skill-demo
```

Review conda's transaction plan before accepting it. This downloads version `0.0.8` of the skill package into `skill-demo`, a conda environment that keeps these packages separate from your other work. Activation makes it the source for the following skill commands. This particular package contains instructions, not the Polars library. Install the library separately for actual data work.

List the installed skill:

```sh
conda skill list
```

You should see skill `polars` from package `agent-skill-polars`, version `0.0.8`. From now on, use the shorter skill name, `polars`, with the `conda skill` commands.

## 2. Read it before using it

List the skill's files and preview its instructions directly:

```sh
conda skill inspect polars
conda skill inspect polars --file SKILL.md
```

Use `--file` with a relative path from the listing to read a supporting text file. If you prefer your editor, `conda skill open polars` requests a file-manager window for the complete directory. It does not launch any packaged file.

Open `SKILL.md` inside the directory shown in the listing's Path column. The environment's location depends on your conda configuration, so use that reported path. This is the text your agent will read. Read the whole file and inspect any supporting files. Its advice and examples may assume tools or workflows different from yours.

Only continue if the instructions fit your project and your agent's permissions. Being available on a package channel is not a reason to trust them automatically.

## 3. Connect it to the project

After reviewing it, run from `project`. These tabs choose where to put the link, not which agent to install:

- `.agents/skills/` is the shared, cross-client convention and the default here. "Agents" is a directory name, not a product. Use it if your coding agent documents support for this path.
- `.claude/skills/` is the Claude-specific location. Choose it when setting up skills for Claude Code's directory convention.

See the [Agent Skills Client Showcase](https://agentskills.io/clients) for supporting agents, then check your agent's documentation for its skill-directory paths. Supporting the file format does not automatically mean it scans `.agents/skills/`. The [integration guide](https://agentskills.io/integrate-skills#where-to-scan) explains the shared directory convention.

::::{tab-set}

:::{tab-item} Shared (.agents/skills/)
:sync: backend-agents

```sh
conda skill link polars
conda skill status
```

You should see a link at `.agents/skills/polars` and a status row marked `linked`. Open `.agents/skills/polars/SKILL.md`: it refers to the installed file in `skill-demo`, without making a second copy.

:::

:::{tab-item} Claude (.claude/skills/)
:sync: backend-claude

```sh
conda skill link polars --backend claude
conda skill status --backend claude
```

You should see a link at `.claude/skills/polars` and a status row marked `linked`. Open `.claude/skills/polars/SKILL.md`: it refers to the installed file in `skill-demo`, without making a second copy.

:::

::::

Open the project in your agent and follow its instructions for loading skills. Conda-skills does not launch the agent or change its settings, and `linked` does not confirm that the agent has read the files. If you are only trying the commands, you can stop at this filesystem check.

## 4. Disconnect it

Use the same directory choice as above:

::::{tab-set}

:::{tab-item} Shared (.agents/skills/)
:sync: backend-agents

```sh
conda skill unlink polars
conda skill status
conda skill list
```

:::

:::{tab-item} Claude (.claude/skills/)
:sync: backend-claude

```sh
conda skill unlink polars --backend claude
conda skill status --backend claude
conda skill list
```

:::

::::

Status should be empty, while the source listing still contains `polars`. Unlinking uses the destination link, independently of the active environment, and does not uninstall the package. If your agent already loaded the instructions, restart or reload it as its documentation requires.

## Clean up the example

After removing the link, deactivate and remove only the environment you created for this tutorial:

```sh
conda deactivate
conda remove -n skill-demo --all
```

Leave the project directory, then delete the tutorial directory using your file manager. Do not remove an environment or project that existed before this tutorial.

## Next steps

When you want to repeat this with another skill or select a source without activating it, use {doc}`../how-to/use-an-installed-skill`. If you would rather write your own instructions, continue with {doc}`../how-to/create-a-skill`. Persistent version pins and workspace sharing can wait until you need them.
