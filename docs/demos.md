# Watch the commands

These recordings run the real CLI. They use the same VHS theme, dimensions, and terminal font as conda-workspaces' demos. No agent is launched, and no package is published.

## Use an installed skill

The example package has already been built and installed in a temporary source environment before the recording starts. The visible commands list its skills, show the instructions, make the skill available to the project, inspect the link, and remove it. Removing the link leaves the installed package alone.

```{image} ../demos/use-a-skill.gif
:alt: Terminal recording showing list, source review, install, status, and remove for the review-notes skill.
```

Text equivalent, after installing a skill package in `../skills`:

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
