# Create a skill

Use `conda skill init` to start a skill directory and a buildable conda recipe. The generated instructions are placeholders. Edit and review them before making the skill available to an agent.

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

`SKILL.md` contains YAML frontmatter with your name and description, followed by placeholder instructions. `build.py` copies that file into the package. The recipe names the package `agent-skill-review-notes` and starts at version `0.1.0`, build `0`. It does not assign a license to your work.

The command refuses to replace any existing destination, including an empty directory or broken symlink. It creates files under the current directory and does not select a conda environment. Use `--global` explicitly to create the directory under your home; running from the home directory without that flag is refused.

For scripts, append `--json` to get one JSON object containing `name`, `path`, and `recipe`. If you omit `--description`, replace the placeholder description as well as the body before use. Names and descriptions follow the {doc}`package-a-skill` validation rules.

Names must also work as Windows directory names. Reserved device names such as `con`, `nul`, `com1`, and `lpt1` are rejected on every platform so generated packages remain portable.

## Write and review the instructions

Replace the body of `SKILL.md` with the procedure you want an agent to follow. Describe when the skill applies and how to check the result. Keep examples specific to that task. Check any commands and references yourself; neither `init` nor package ownership establishes that instructions are safe.

If you add supporting files, update `build.py` to copy them into the same skill directory and add them to the recipe's strict `package_contents` checks. The generated script packages only `SKILL.md`, so the authoring recipe and build script are not exposed as skill content. See {doc}`package-a-skill` for an example with companion files and the containment rules.

Review the package name, version, summary, and license before distribution. The recipe summary is derived from the validated skill name rather than your description, so description text cannot become a rattler-build template expression.

## Build and install deliberately

With `rattler-build` available, run from the new directory:

```sh
rattler-build build --recipe recipe/recipe.yaml -c conda-forge
```

The build produces `agent-skill-review-notes-0.1.0-0.conda` in the output directory reported by rattler-build. It checks that the package contains `share/agent-skills/review-notes/SKILL.md`. Build tooling runs `build.py`; the plugin itself does not execute skill content.

Install the artifact into a source environment with conda, then use `conda skill list` to verify discovery. The {doc}`../tutorials/first-skill` tutorial shows the full build, installation, review, and linking sequence. Until the package is installed, the new authoring directory does not appear in package-owned discovery.

## Package format compatibility

The generated package follows the same layout as [pixi-skills](https://github.com/pavelzw/pixi-skills) and [skill-forge](https://github.com/pavelzw/skill-forge): `agent-skill-NAME`, `noarch: generic`, and `share/agent-skills/NAME/SKILL.md`. Its strict content test follows skill-forge's example. The build uses Python rather than shell-specific `cp` commands so it can run on Windows too.

The authoring directory keeps the recipe under `recipe/`; skill-forge's example places it beside `SKILL.md` and includes a Pixi build manifest. Those authoring choices do not change the installed package layout. This scaffold does not configure a channel or submit a package to skill-forge.

Conda-skills requires a `name` field matching the skill directory. Pixi-skills also accepts headers without a name, so not every skill it discovers meets conda-skills' validation rules. Conda-skills also requires conda package records and checks filesystem containment. This is package-format compatibility, not a claim that both tools discover identical skills or configure every agent the same way.

## Use the interactive guide

```sh
conda skill quickstart
```

Choose `new` to enter the name and description interactively. The guide previews the destination and asks for confirmation before creating the same files as `init`.

Choose `link` to select a skill already installed in a source environment. Use `conda skill quickstart -n skills-env` or `-p /path/to/environment` to select that environment. Review the source path, description, and supporting files, choose a backend and scope, then confirm the destination. Home changes require starting the guide with `--global`; a menu selection alone does not authorize them.

The guide does not use AI, install packages, or create environments. Both input and output must be terminals, and JSON mode is rejected before prompts. Use the explicit commands for scripts. The first prompt defaults to cancellation and the final confirmation defaults to no.
