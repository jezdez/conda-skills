# How agents find skills

Conda installs a skill package into an environment. Conda-skills finds its recorded files and creates a link in your project or home directory. Your agent then decides whether and how to load those instructions.

## From package to skill

For example, package `agent-skill-polars` version `0.0.8` supplies the skill named `polars`. Use the package name with conda's package commands and the skill name with `conda skill install`. The version shown by `conda skill list` comes from the package record, not the library or instruction text.

Conda records installed package files in `conda-meta/`. The plugin looks for recorded headers at `share/agent-skills/<name>/SKILL.md` and checks the name, description, duplicate ownership, and filesystem containment. It ignores untracked directories. One package can supply several skills, and the `agent-skill-` package prefix is a convention rather than a requirement. See {doc}`../reference/skill-format` for the exact rules.

Creating a skeleton with `init` or copying `SKILL.md` into a checkout does not make it discoverable through this plugin. Neither does a pip-only installation. Installing the plugin through conda-pypi is a separate operation from packaging skill headers at the required paths.

## Which environment supplies the files?

Install the plugin in the environment that runs conda, commonly `base`. That conda executable can read skills from another environment without requiring Python or the plugin there. Activating the skill environment is optional.

`list`, `install`, and `remove` select a source with either `-n NAME` or `-p PREFIX`. Without either, conda uses its default target, normally the active environment or base. The source must already exist. These commands do not download packages, create environments, or search all environments.

Removal checks the link against the selected source. Choosing a different environment can cause a conflict even when both environments contain a skill with the same name.

## Where does the agent look?

The [Agent Skills integration guide](https://agentskills.io/integrate-skills#where-to-scan) recommends `.agents/skills/` for cross-client interoperability. The format specification does not mandate discovery paths or guarantee every client scans this location. Conda-skills uses that convention by default and keeps `.claude/skills/` as a compatibility option, rather than maintaining a backend for every agent.

The destination is the current directory unless you choose your home with `--global`. There is no upward search for a Git repository or workspace manifest, so run project commands from the intended project root.

| Backend | Project destination | With `--global` |
| --- | --- | --- |
| `agents` (default) | `<current directory>/.agents/skills/` | `<home>/.agents/skills/` |
| `claude` | `<current directory>/.claude/skills/` | `<home>/.claude/skills/` |

For an installed skill named `review-notes` in environment `development`, these commands use the same source with different destinations:

```sh
conda skill install review-notes -n development
conda skill install review-notes -n development --backend claude
conda skill install review-notes -n development --global
```

Substitute your environment and discovered skill name. `--global` changes only the destination. It does not select base or search other environments. Even when running from your home directory, mutations require explicit `--global`. Read-only `status` can inspect the current directory without it.

A workspace setup might look like this:

```text
project/
  conda.toml
  conda.lock
  .conda/envs/skills/share/agent-skills/polars/
    SKILL.md
  .agents/skills/polars -> ../../.conda/envs/skills/share/agent-skills/polars
```

The whole skill directory is linked, so references and scripts remain beside `SKILL.md`. Conda-skills does not execute them or configure the agent. Each client controls its search paths, reload behavior, skill selection, and permissions. Consult its documentation and check its own skill listing or session behavior. A `linked` status confirms a filesystem link, not that the agent has read or used the skill. See {doc}`skill-safety` for what status and discovery establish.

## A link follows the installed files

Updating a source package changes the content visible through every link to that directory. Removing or renaming the source can break those links. A link has no independent package version, so follow {doc}`../how-to/update-skills` when changing a shared source.

Relative links survive moving the project and source together only if their relative layout stays the same. Across Windows drives, targets are absolute. This describes link behavior, not a guarantee that a relocated conda environment will work. The plugin has no link database or automatic repair. Use {doc}`../how-to/troubleshooting` to inspect and recover stale links.

## Does the skill install its library?

A skill about Polars can contain instructions without the Polars library. Creating a link installs no software and does not select the interpreter, kernel, or shell your agent uses.

Installing the package with conda can bring dependencies. A `depends` entry requires a package in the same environment. A `constrains` entry limits its version if present, without requiring installation. Mentioning a library in the instructions has no effect on conda's solver.

Read the package metadata and transaction plan. Constraints in a dedicated skills environment do not apply to a separate application environment, so check that the instructions fit the software your project actually runs.

## Shared packaging conventions

The generated recipe uses the same installed layout as pixi-skills and skill-forge: `agent-skill-NAME`, `noarch: generic`, and `share/agent-skills/NAME/SKILL.md`. Its strict content test follows skill-forge's example, with a Python build script for portability. Conda-skills keeps the recipe under `recipe/`. Skill-forge's example places it beside `SKILL.md` with a Pixi build manifest. These authoring choices do not change the installed layout or configure a publishing channel.

Conda-skills requires conda package records and a matching header name. Pixi-skills also accepts headers without names, so the tools can discover different skills. See {doc}`prior-art` for their origins and {doc}`../how-to/use-an-installed-skill` for the linking steps.
