# Watch the commands

These recordings run the real CLI. They use the same VHS theme, dimensions, and terminal font as conda-workspaces' demos. No agent is launched, and no package is published.

## Install from skill-forge

This recording starts with an installed conda-skills plugin and an empty temporary project. The package transaction is visible: it downloads `agent-skill-polars==0.0.8` from skill-forge, then lists, previews, links, and removes the skill. The recording selects libmamba in its isolated shell; the text below makes that choice explicit.

```{image} ../demos/skill-forge.gif
:alt: Terminal recording of a Polars skill package downloaded from skill-forge, discovered, previewed, linked, and unlinked.
```

Text equivalent, from a new tutorial project:

```sh
conda create --yes --solver libmamba --prefix ../skills --override-channels -c https://prefix.dev/skill-forge "agent-skill-polars==0.0.8"
conda skill list -p ../skills
bat --paging=never --line-range 1:18 ../skills/share/agent-skills/polars/SKILL.md
conda skill install polars -p ../skills
conda skill status
conda skill remove polars -p ../skills
```

This exact version has no runtime dependencies, so the recording only needs the skill-forge channel. The tutorial also supplies conda-forge for more general package use. The 18-line preview keeps the recording short; inspect the complete instructions and supporting files before linking a skill yourself. Bat is optional: an editor works too. Follow {doc}`tutorials/skill-forge` for prerequisites, review steps, backend selection, and cleanup.

## Reproduce project skills

The recording starts with the following manifest already written in a temporary project. Conda-workspaces and conda-skills are installed in the tooling environments; the `skills` environment itself contains only the skill package.

```{literalinclude} ../demos/project-skills.toml
:language: toml
```

```{image} ../demos/project-skills.gif
:alt: Terminal recording showing conda.toml, a multi-platform lock operation, locked installation of the skills environment, and a project skill link.
```

Text equivalent:

```sh
conda workspace lock
conda workspace install --locked -e skills
conda skill list -p .conda/envs/skills
conda skill install polars -p .conda/envs/skills
conda skill status
```

The demo uses `CONDA_SOLVER=libmamba` in its temporary shell. Read and review the skill files before the `install` step; this recording focuses on the lock/install workflow rather than repeating the content review. The lock includes Linux, macOS ARM64, and Windows records, but this recording executes only on macOS. See {doc}`how-to/project-skills` for setup, sharing with teammates, and cleanup; see {doc}`how-to/update-skills` for deliberate changes to the locked versions.

## Recover a broken link

The local example package is installed and linked before recording. Moving that source environment makes the link stale. The recording inspects the link, removes only that symlink, then recreates it against the relocated source.

```{image} ../demos/recover-link.gif
:alt: Terminal recording showing a broken skill link after moving its source, inspection with ls, unlinking that path, and recreation against the moved source.
```

The POSIX commands are:

```sh
mv ../skills ../skills-moved
conda skill status
ls -ld .agents/skills/review-notes
unlink .agents/skills/review-notes
conda skill install review-notes -p ../skills-moved
conda skill status
```

The `mv` is a controlled failure demonstration using a disposable, data-only environment. It is not general advice for moving conda environments, whose executables may embed their original prefix. In a real incident, restore the original source or recreate the environment at its intended path. Use `unlink` only after confirming the exact entry is the stale symlink you intend to remove; never replace it with recursive deletion. See {doc}`how-to/troubleshooting` for recovery options and PowerShell instructions.

## Use an installed skill

The example package has already been built and installed in a temporary source environment before the recording starts. The visible commands list its skills, show the instructions, make the skill available to the project, inspect the link, and remove it. Removing the link leaves the installed package alone.

```{image} ../demos/use-a-skill.gif
:alt: Terminal recording showing list, source review, install, status, and remove for the review-notes skill.
```

Text equivalent, after installing a skill package in `../skills`. The recording configures bat for color and no paging; the flags are explicit here so this works without that setup:

```sh
conda skill list -p ../skills
bat --paging=never --style=plain ../skills/share/agent-skills/review-notes/SKILL.md
conda skill install review-notes -p ../skills
conda skill status
conda skill remove review-notes -p ../skills
```

For a guided exercise that includes building the example package, follow {doc}`tutorials/first-skill`. If your package is already installed, use {doc}`how-to/use-an-installed-skill`.

## Create a skill with the guide

The interactive guide collects a name and description, previews the destination, and asks before writing. The result is a starting point for your instructions and recipe. It does not install a package or make the new skill available to an agent. The authoring is still your job; the paperwork is smaller.

```{image} ../demos/quickstart.gif
:alt: Terminal recording of quickstart creating a review-notes skeleton after name, description, project scope, and confirmation prompts.
```

Text equivalent:

```sh
conda skill quickstart
```

Choose `new`, enter `review-notes` and a description, choose `project`, then confirm. For scripts, the equivalent file-generation command is:

```sh
conda skill init review-notes --description "Summarize the review findings supplied by the user."
```

Continue with {doc}`how-to/create-a-skill`. The recordings show macOS terminal behavior; they do not demonstrate Windows symlink permissions. See {doc}`how-to/troubleshooting` for those requirements.
