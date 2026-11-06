# conda-skills

## What is a skill?

A skill is a set of instructions for an AI coding agent. It usually lives in a text file called `SKILL.md`, sometimes with examples, reference material, or scripts alongside it. A skill might explain how to work with a particular library or carry out a code review.

The open [Agent Skills specification](https://agentskills.io/specification) defines the format: a directory with `SKILL.md`, metadata, and instructions.

Your agent reads those instructions to help with a task. Installing a skill does not change the agent's model or install the library it describes unless the package declares that dependency.

Conda-skills lets you get skills through conda packages and make them available to your agent. You choose which instructions to use in each project.

Inspired by Pavel Zwerschke's [pixi-skills](https://github.com/pavelzw/pixi-skills) and [skill-forge](https://github.com/pavelzw/skill-forge), this project brings the same approach to conda's Python stack. See {doc}`explanation/prior-art` for the background.

## Why use conda-skills?

Copying a skill into one project is straightforward. Keeping track of where it came from, which version you use, and how to share that setup takes more work.

Conda manages the skill's package and version. You choose which projects can use it. Several projects can link to the same installed files, and teams can record package versions in a shared environment definition. Updating that package changes the content visible through those links, so review updates before making them available again.

If you already use conda, this keeps skill distribution in your existing tooling. For a single local skill you maintain yourself, copying the files may be enough.

See {doc}`explanation/common-questions` for how this compares with copying files, what gets installed, and whether you need conda-workspaces.

## Start with one skill

The {doc}`tutorials/skill-forge` tutorial walks through one example: instructions for working with the Polars data library. You will:

1. Install the skill package in a separate conda environment.
2. Read its instructions and decide whether to use them.
3. Make it available to a project, then remove it again.

You need conda and an agent that supports a skill-directory convention. If `conda skill --help` is not available yet, follow {doc}`how-to/installation` first. No recipe writing or workspace configuration is needed for the tutorial.

```{button-ref} tutorials/skill-forge
:color: primary
:shadow:

Try your first skill
```

Read a skill before using it. Conda-skills checks the package layout, but you decide whether the instructions are appropriate for your work.

## What the commands do

| Command | What it does |
|---|---|
| `conda install` or `conda create` | Downloads a package into a conda environment. |
| `conda skill install` | Creates a directory link so your agent can find an installed skill. |

The link points to the installed files instead of making another copy. `conda skill remove` removes that link and leaves the package alone. Conda-skills does not launch your agent or change its configuration. The tutorial explains how to choose its skill directory.

## Watch first, if you prefer

```{image} ../demos/skill-forge.gif
:alt: Terminal demo of installing a Polars skill package, reviewing its header, making it available to a project, and removing its link.
:target: demos/
```

Prefer written instructions? Every recording on the {doc}`demos` page has a text equivalent.

## After the first tutorial

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Write your own instructions
:link: how-to/create-a-skill
:link-type: doc

Create starter files with `conda skill init`, or use the interactive guide.
:::

:::{grid-item-card} Share skills with a team
:link: how-to/project-skills
:link-type: doc

Keep package versions in a workspace manifest and lockfile when your project needs them.
:::

::::

For ongoing use, see {doc}`how-to/update-skills`, {doc}`reference/commands`, or {doc}`how-to/troubleshooting`. The explanations cover {doc}`explanation/agent-discovery` and {doc}`explanation/skill-safety` when you need those details.

```{toctree}
:hidden:
:caption: Start here

how-to/installation
tutorials/skill-forge
demos
```

```{toctree}
:hidden:
:caption: Use and maintain skills

how-to/use-an-installed-skill
how-to/troubleshooting
how-to/update-skills
how-to/project-skills
```

```{toctree}
:hidden:
:caption: Write and package skills

how-to/create-a-skill
how-to/package-a-skill
tutorials/build-a-skill-package
```

```{toctree}
:hidden:
:caption: Reference

reference/commands
reference/json
reference/skill-format
```

```{toctree}
:hidden:
:caption: Explanation

explanation/common-questions
explanation/skill-safety
explanation/agent-discovery
explanation/prior-art
```

```{toctree}
:hidden:
:caption: Contributing

contributing
releasing
changelog
```

```{toctree}
:hidden:
:caption: Proposals

proposals/skill-packages
```
