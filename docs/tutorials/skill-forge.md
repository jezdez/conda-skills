# Use a skill from skill-forge

Install a published skill, review its instructions, and make it available to a project. This tutorial uses the Polars skill from Pavel Zwerschke's [skill-forge channel](https://prefix.dev/channels/skill-forge). You do not need to write a recipe or build a package.

Skill-forge distributes conda packages. Conda-skills connects their installed files to your agent's skill directory. You do not need Pixi or pixi-skills to follow this tutorial; see {doc}`../explanation/prior-art` for how the projects relate.

## Before you start

You need conda 26.9 or newer with conda-skills installed in the environment that runs conda. Check `conda skill --help`; follow {doc}`../how-to/installation` if it is unavailable. The plugin itself is still unreleased, so use the documented checkout or local-artifact installation until a release is available.

The package download needs network access. On Windows, symlink creation needs Developer Mode or appropriate privileges. Use a new, empty tutorial directory containing a `project` subdirectory, and open your terminal in `project`. The source environment will be created next to it, keeping both apart from your existing projects.

```text
skill-forge-tutorial/
  project/       # run the following commands here
  skills/        # created by conda below
```

## Install the skill package

Run this single-line command in Bash, zsh, or PowerShell:

```sh
conda create --yes --solver libmamba --prefix ../skills --override-channels -c https://prefix.dev/skill-forge -c conda-forge "agent-skill-polars==0.0.8"
```

The example pins a version verified with conda-skills. It installs the skill package, not the Polars Python library. This version has no runtime package dependencies. Other skill packages may have dependencies; read conda's package plan before accepting unfamiliar packages.

The explicit solver avoids an issue observed with conda-rattler-solver 26.10.2 reading this channel's attestation metadata. It does not change your configured solver. See {doc}`../how-to/troubleshooting` if channel loading fails.

List the installed skill:

```sh
conda skill list -p ../skills
```

Look for skill name `polars`, package `agent-skill-polars`, and version `0.0.8`. The package name and skill name are different: use the former with conda's package commands, the latter with `conda skill install`.

## Review the instructions

Open `../skills/share/agent-skills/polars/SKILL.md` in your editor. Read the complete file and inspect its supporting files, not just its description. This skill includes advice and examples for working with Polars; its suggestions may assume tools or workflows different from yours.

The package being available on a channel does not mean you should automatically trust its instructions. Decide whether they fit your project and your agent's permissions. Conda-skills validates metadata and containment; it does not assess the advice.

## Make the skill available

After reviewing it, run from `project`:

```sh
conda skill install polars -p ../skills
conda skill status
```

You should see a link at `.agents/skills/polars` and a status row marked `linked`. Open `.agents/skills/polars/SKILL.md`: it refers to the installed file in `../skills`, without making a second copy.

For Claude's directory convention, use `--backend claude` on both commands. The plugin does not start an agent or modify its configuration. Check that your client reads the chosen directory; `linked` reports a valid filesystem link, not confirmation from the agent.

The optional interactive route is `conda skill quickstart -p ../skills`: choose `link`, select `polars`, choose your backend and project scope, and confirm. It uses the same discovery and linking operations and does not install the package for you.

## Remove the link and clean up

```sh
conda skill remove polars -p ../skills
conda skill status
conda skill list -p ../skills
```

Status should be empty, while the source listing still contains `polars`. Removing a client link does not uninstall its package. If you chose the Claude backend, repeat `--backend claude` for removal and status too.

When finished, remove only the tutorial's source environment:

```sh
conda remove --yes --prefix ../skills --all
```

Leave the project directory, then delete the tutorial directory using your file manager. Do not remove an environment or project that existed before this tutorial.

## Next steps

- {doc}`../how-to/project-skills`: declare and lock a project's skills for teammates.
- {doc}`../how-to/update-skills`: pin, review, update, and restore a skill version.
- {doc}`../explanation/packages-and-discovery`: understand what gets installed and what your agent sees.
- {doc}`first-skill`: build your own example package locally.

The {doc}`../demos` page includes a recording of this workflow. Its shortened preview shows only the beginning of `SKILL.md`; read the whole skill before using it yourself.
