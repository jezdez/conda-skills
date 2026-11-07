# Package a skill

Package each skill with a header at `share/agent-skills/<name>/SKILL.md` so the plugin can find it in conda's installed package records. One package can contain several skills, and its conda package name does not have to match any of their names.

## Choose the installed layout

For a skill called `review-notes`, install:

```text
<prefix>/
  share/
    agent-skills/
      review-notes/
        SKILL.md
```

Optional `references/`, `scripts/`, or other companion files belong inside the skill directory. The plugin links the whole directory but does not execute its scripts. Package companion files with the header so that conda updates and removes them together.

The plugin recognizes only this exact header depth and spelling. A file at `share/agent-skills/group/review-notes/SKILL.md`, or named `skill.md`, is not a candidate.

## Write the header and instructions

Use this complete `SKILL.md` as a starting point:

```{literalinclude} ../examples/review-notes/SKILL.md
:language: markdown
```

Choose a name matching the directory and write a description of when the skill should be used. See {doc}`../reference/skill-format` for the exact naming, header, ownership, and containment requirements. The plugin does not interpret additional metadata or the instruction body, so test the content with each client you intend to support.

Avoid symlinks to files outside the skill directory, even if those files live elsewhere in the same environment. They fail containment checks. Do not have multiple packages install the same skill name into one environment.

## Build a conda package

The example uses rattler-build's recipe format. Its `source.path` is relative to the recipe directory. The build copies the checkout into the build source directory, including the example files and repository license:

```{literalinclude} ../examples/recipe/recipe.yaml
:language: yaml
```

The build script copies the skill to the required prefix-relative path:

```{literalinclude} ../examples/build.py
:language: python
```

The recipe uses Python as a build dependency to copy files. This example contains only portable Markdown with no runtime dependencies, so it uses `noarch: generic`. If your skill contains platform-specific programs or requires tools at runtime, declare and test those requirements in its recipe. The plugin does not infer them from instructions.

The example's license path points to the repository license. Use the license that applies to your own content.

Set up conda-workspaces as described in {doc}`../contributing`. From the checkout root, install the locked build environment and run rattler-build:

```sh
conda workspace install --locked -e build
conda workspace run -e build -- rattler-build build --recipe docs/examples/recipe/recipe.yaml --output-dir conda-dist -c conda-forge
```

The package file is `conda-dist/noarch/conda-skills-example-0.1.0-0.conda`. The recipe's package-contents test checks that the header was packaged. The example uses a fixed build string. For your own package, follow your channel's version and build-number policy.

## Check installed discovery

Install the package into a new disposable prefix using `conda create --prefix <prefix> <artifact>`, then run `conda skill list -p <prefix>` with a conda executable that has the plugin installed. Follow {doc}`../tutorials/build-a-skill-package` for the complete POSIX and PowerShell commands.

Before distributing the package, test that the plugin can discover and validate the installed skill, then check linking, status, and unlinking. A successful build alone does not cover these operations. Review every packaged file, including support scripts, separately from those checks. See {doc}`../explanation/skill-safety` for the limits of package ownership.

## Pin sources for distribution

Review the entire recipe and every source it uses. Pin immutable source revisions or archive URLs and record their checksums. A checksum for `SKILL.md` alone does not cover companion files or build scripts, and a source archive checksum does not identify the resulting conda package.

Keep recipe changes reviewable in the package repository. Consumer lockfile changes belong in the projects using the package. See {doc}`../explanation/skill-safety` for what each kind of pin guarantees.
