# Create a skill

Use `conda skill init` to create a skill directory and a buildable conda recipe. It gets the paperwork started. The generated instructions are placeholders, so edit and review them before making the skill available to an agent.

If the command is unavailable, follow the {doc}`installation` guide first.

## Generate the files

From a project directory, run:

```sh
conda skill init review-notes --description "Use when reviewing project notes for missing decisions and follow-up work."
```

The new directory contains:

```text
review-notes/
  SKILL.md
  build.py
  recipe/
    recipe.yaml
```

`SKILL.md` contains YAML frontmatter with the skill name and description, followed by placeholder instructions. `build.py` copies that file into the package. The recipe names the package `agent-skill-review-notes` and starts at version `0.1.0`, build `0`. You need to choose a license for your work because the recipe does not assign one.

The command refuses to replace any existing destination, including an empty directory or broken symlink. It creates files under the current directory and does not select a conda environment. Use `--global` explicitly to create the directory under your home. Running from the home directory without that flag is refused.

For scripts, append `--json` to get one JSON object containing `name`, `path`, and `recipe`. If you omit `--description`, replace the placeholder description as well as the body before use. See {doc}`../reference/skill-format` for name and description rules, including Windows-safe directory names.

## Write and review the instructions

Replace the body of `SKILL.md` with the procedure you want an agent to follow. Describe when the skill applies and how to check the result. Keep examples specific to that task. Check any commands and references yourself. Neither `init` nor package ownership establishes that instructions are safe.

If you add supporting files, update `build.py` to copy them into the same skill directory and add them to the recipe's strict `package_contents` checks. The generated script packages only `SKILL.md`, so the authoring recipe and build script are not exposed as skill content. See {doc}`package-a-skill` for an example with companion files and the containment rules.

Review the package name, version, summary, and license before distribution. The recipe summary uses the validated skill name. Your description is kept out of the summary so it cannot become a rattler-build template expression.

## Build and install deliberately

With `rattler-build` available, run from the new directory:

```sh
rattler-build build --recipe recipe/recipe.yaml -c conda-forge
```

The build produces `agent-skill-review-notes-0.1.0-0.conda` in the output directory reported by rattler-build. It checks that the package contains `share/agent-skills/review-notes/SKILL.md`. Build tooling runs `build.py`, but the plugin itself does not execute skill content.

Install the artifact into a source environment with conda, then check discovery with `conda skill list`. Package-owned discovery will not find the skill until you install the package. Follow {doc}`../tutorials/build-a-skill-package` for the full build, installation, review, and linking sequence.

## Use the interactive guide

Watch the {doc}`../demos` for a recording and text walkthrough of this flow.

```sh
conda skill quickstart
```

Choose `new` to enter the name and description interactively. The guide previews the destination and asks for confirmation before creating the same files as `init`.

Home changes require starting the guide with `--global`. A menu selection alone does not authorize them. For the guide's `link` choice, see {doc}`use-an-installed-skill`.

The guide does not use AI, install packages, or create environments. Both input and output must be terminals, and JSON mode is rejected before prompts. Use the explicit commands for scripts. The first prompt defaults to cancellation and the final confirmation defaults to no.
