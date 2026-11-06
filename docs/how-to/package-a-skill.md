# Package a skill

The plugin finds skills through installed conda packages that record a header at `share/agent-skills/<name>/SKILL.md`. A package can contain one skill or several, and its conda package name does not have to match a skill name.

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

The supplied example is a complete `SKILL.md`:

```{literalinclude} ../examples/review-notes/SKILL.md
:language: markdown
```

The plugin requires:

- A directory name of at most 64 characters matching `[a-z0-9]+(?:-[a-z0-9]+)*`: lowercase ASCII letters and digits, with single hyphens between nonempty segments.
- UTF-8 `SKILL.md` with YAML frontmatter starting on the first line, enclosed by lines containing exactly `---`.
- A YAML mapping whose `name` equals the directory name.
- A string `description` with non-whitespace content and at most 1024 characters.
- A skill root and header that resolve inside the source environment, with companion paths that remain inside the resolved skill root.
- A single owning package record for each discovered skill name in the selected environment.

The plugin does not interpret additional metadata or the instruction body. These checks do not cover every agent's skill format. Test the content with each client you intend to support.

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

The recipe's build dependency supplies Python for copying files. `noarch: generic` is suitable because this example contains only portable Markdown and has no runtime dependencies. If your skill contains platform-specific programs or requires tools at runtime, declare and test those requirements in its recipe; the plugin does not infer them from the instructions. This recipe's license path points to the repository license. Use the license that applies to your own content.

Set up conda-workspaces as described in {doc}`../contributing`. From the checkout root, install the locked build environment and run rattler-build:

```sh
conda workspace install --locked -e build
conda workspace run -e build -- rattler-build build --recipe docs/examples/recipe/recipe.yaml --output-dir conda-dist -c conda-forge
```

The package file is `conda-dist/noarch/conda-skills-example-0.1.0-0.conda`. The recipe's package-contents test checks that the header was packaged. The example uses a fixed build string. For your own package, follow your channel's version and build-number policy.

## Check installed discovery

Install the package into a new disposable prefix using `conda create --prefix <prefix> <artifact>`, then run `conda skill list -p <prefix>` with a conda executable that has the plugin installed. Follow {doc}`../tutorials/first-skill` for the complete POSIX and PowerShell commands.

A successful build does not prove that the plugin can discover and validate the installed skill. Test listing, linking, status, and removal before distributing it. Review every packaged file, including support scripts, separately from those checks. See {doc}`../explanation/ownership-and-trust` for the limits of package ownership.
