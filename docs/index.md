# conda-skills

`conda skill` connects conda-packaged agent skills to coding agents. It discovers skills in an installed conda environment and creates directory symlinks under `.agents/skills/` or `.claude/skills/`. Companion files remain available through the same link.

This is unreleased development software with source version `0.1.0`. You need Python 3.11 or newer and conda 26.9 or newer. Install the plugin into the environment that runs conda, then select any existing source environment with `-n` or `-p`. Start with {doc}`how-to/installation` if `conda skill --help` is not available.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Set up a skill for your agent
:link: tutorials/first-skill
:link-type: doc

Build the supplied example locally, inspect it, create a project link, and remove it.
:::

:::{grid-item-card} Package a skill
:link: how-to/package-a-skill
:link-type: doc

Use a complete SKILL.md and conda recipe to make your skill discoverable.
:::

:::{grid-item-card} Look up commands
:link: reference/commands
:link-type: doc

Find command options, defaults, filesystem behavior, and links to JSON schemas.
:::

:::{grid-item-card} Understand ownership and trust
:link: explanation/ownership-and-trust
:link-type: doc

Learn what package records establish and what you must review yourself.
:::

::::

Installing a link does not install a package, launch an agent, or change client configuration. Use conda to manage source packages. Review their instructions and supporting files before exposing them to an agent.

```{toctree}
:hidden:
:caption: Tutorial

tutorials/first-skill
```

```{toctree}
:hidden:
:caption: How-to guides

how-to/installation
how-to/create-a-skill
how-to/package-a-skill
how-to/troubleshooting
```

```{toctree}
:hidden:
:caption: Reference

reference/commands
reference/json
```

```{toctree}
:hidden:
:caption: Explanation

explanation/scope
explanation/ownership-and-trust
```

```{toctree}
:hidden:
:caption: Project

contributing
releasing
changelog
```
