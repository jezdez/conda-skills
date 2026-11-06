# conda-skills

`conda skill` connects conda-packaged agent skills to coding agents. It discovers skills in an installed conda environment and creates directory symlinks under `.agents/skills/` or `.claude/skills/`. Companion files remain available through the same link.

Inspired by Pavel Zwerschke's [pixi-skills](https://github.com/pavelzw/pixi-skills) and [skill-forge](https://github.com/pavelzw/skill-forge), conda-skills brings the same approach to conda's Python stack. See {doc}`explanation/prior-art` for the background and shared conventions.

This is unreleased development software. Python package versions are derived from Git; the conda recipe's current candidate is `0.1.0`. You need Python 3.11 or newer and conda 26.9 or newer. Install the plugin into the environment that runs conda, then select any existing source environment with `-n` or `-p`. Start with {doc}`how-to/installation` if `conda skill --help` is not available.

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} Use a skill from skill-forge
:link: tutorials/skill-forge
:link-type: doc

Install a published skill, review its instructions, and make it available to your project.
:::

:::{grid-item-card} Keep project skills reproducible
:link: how-to/project-skills
:link-type: doc

Declare skill packages in conda.toml, review the lockfile, and reproduce the environment.
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

## See it in action

Watch the {doc}`demos` for skill-forge installation, locked project skills, authoring, and broken-link recovery. Each recording has a text equivalent and links to the relevant tutorial or how-to guide.

```{image} ../demos/skill-forge.gif
:alt: Terminal demo of installing the Polars skill from skill-forge, reviewing its header, linking it to a project, and removing the link.
:target: demos/
```

Already have a skill package? Go straight to {doc}`how-to/use-an-installed-skill`. Writing your own? Start with {doc}`how-to/create-a-skill`.

For a complete authoring exercise, {doc}`tutorials/first-skill` builds the supplied example locally. For ongoing maintenance, see {doc}`how-to/update-skills`. The difference between a package, a skill, its library dependencies, and agent discovery is covered in {doc}`explanation/packages-and-discovery`.

```{toctree}
:hidden:
:caption: Tutorials

tutorials/skill-forge
tutorials/first-skill
```

```{toctree}
:hidden:
:caption: How-to guides

how-to/installation
how-to/use-an-installed-skill
how-to/project-skills
how-to/update-skills
how-to/create-a-skill
how-to/package-a-skill
how-to/troubleshooting
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

explanation/scope
explanation/ownership-and-trust
explanation/packages-and-discovery
explanation/prior-art
```

```{toctree}
:hidden:
:caption: Project

contributing
releasing
changelog
demos
```
