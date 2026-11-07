# Try your first skill

Try a skill containing instructions for Polars, a Python data library. You will download it, review the instructions, connect it to a project, and remove the link. You do not need Polars installed to practice these steps.

The skill comes from Pavel Zwerschke's [skill-forge channel](https://prefix.dev/channels/skill-forge). A channel is a place conda downloads packages from. You will use conda to get the files and conda-skills to connect them to your project.

## Before you start

Run `conda skill --help`. If the command is unavailable, follow {doc}`../how-to/installation` before continuing. You also need network access to download the example.

On Windows, directory links require Developer Mode or appropriate privileges. Check your organization's policy before enabling them.

Create a new, empty folder named `skill-forge-tutorial` using your file manager. Inside it, create `project` and open your terminal there. Conda will create a separate `skills` folder next to it:

```text
skill-forge-tutorial/
  project/       # run the following commands here
  skills/        # created by conda below
```

## 1. Get the skill

Run this single-line command in Bash, zsh, or PowerShell:

```sh
conda create --yes --prefix ../skills --override-channels -c https://prefix.dev/skill-forge -c conda-forge "agent-skill-polars==0.0.8"
```

This downloads version `0.0.8` of the skill package into `../skills`. That folder is a conda environment: a place to keep installed packages separate from your project. This particular package contains instructions, not the Polars library.

List the installed skill:

```sh
conda skill list -p ../skills
```

You should see skill `polars` from package `agent-skill-polars`, version `0.0.8`. From now on, use the shorter skill name, `polars`, with the `conda skill` commands.

## 2. Read it before using it

Open `../skills/share/agent-skills/polars/SKILL.md` in your editor. This is the text your agent will read. Read the whole file and inspect any supporting files. Its advice and examples may assume tools or workflows different from yours.

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
conda skill install polars -p ../skills
conda skill status
```

You should see a link at `.agents/skills/polars` and a status row marked `linked`. Open `.agents/skills/polars/SKILL.md`: it refers to the installed file in `../skills`, without making a second copy.

:::

:::{tab-item} Claude (.claude/skills/)
:sync: backend-claude

```sh
conda skill install polars -p ../skills --backend claude
conda skill status --backend claude
```

You should see a link at `.claude/skills/polars` and a status row marked `linked`. Open `.claude/skills/polars/SKILL.md`: it refers to the installed file in `../skills`, without making a second copy.

:::

::::

Open the project in your agent and follow its instructions for loading skills. Conda-skills does not launch the agent or change its settings, and `linked` does not confirm that the agent has read the files. If you are only trying the commands, you can stop at this filesystem check.

## 4. Disconnect it

Use the same directory choice as above:

::::{tab-set}

:::{tab-item} Shared (.agents/skills/)
:sync: backend-agents

```sh
conda skill remove polars -p ../skills
conda skill status
conda skill list -p ../skills
```

:::

:::{tab-item} Claude (.claude/skills/)
:sync: backend-claude

```sh
conda skill remove polars -p ../skills --backend claude
conda skill status --backend claude
conda skill list -p ../skills
```

:::

::::

Status should be empty, while the source listing still contains `polars`. Removing the link does not uninstall the package. If your agent already loaded the instructions, restart or reload it as its documentation requires.

## Clean up the example

When finished, remove only the tutorial's source environment:

```sh
conda remove --yes --prefix ../skills --all
```

Leave the project directory, then delete the tutorial directory using your file manager. Do not remove an environment or project that existed before this tutorial.

## Next steps

When you want to repeat this with another skill, use {doc}`../how-to/use-an-installed-skill`. If you would rather write your own instructions, continue with {doc}`../how-to/create-a-skill`. Version pinning and workspace sharing can wait until you need them.
