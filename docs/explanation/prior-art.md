# Prior art

Conda-skills was inspired by Pavel Zwerschke's [pixi-skills](https://github.com/pavelzw/pixi-skills) and [skill-forge](https://github.com/pavelzw/skill-forge), which distribute agent instructions and supporting files through existing package managers. His post, [Managing Agent Skills with Your Package Manager](https://pavel.pink/blog/pixi-skills), describes the approach.

## The Agent Skills format

The underlying [Agent Skills specification](https://agentskills.io/specification) was originally developed by Anthropic and released as an open standard. It defines the skill directory, required metadata, instructions, and supporting resources. Its development is hosted in [agentskills/agentskills](https://github.com/agentskills/agentskills).

The format and the distribution method are separate: Agent Skills describes the content, while Pavel's work applies package managers to distributing it. Conda-skills adopts that distribution approach using conda's Python APIs. See {doc}`../reference/skill-format` for the distinction between specification requirements, package layout, and the checks performed here.

## Bringing the approach to conda

Conda-skills is an independent implementation built on conda's plugin API, environment lookup, and installed package records. It does not bundle pixi-skills source code.

The projects share an installed package layout, but their discovery and validation rules differ. See {doc}`agent-discovery` for compatibility details and {doc}`../reference/skill-format` for the requirements conda-skills checks.

The {doc}`../proposals/skill-packages` draft proposes documenting a shared packaging convention. It credits this work as its starting point and leaves unresolved differences for discussion with the maintainers. It is not an official conda specification.

## Complementary projects

- pixi-skills makes the package-manager approach available to Pixi users.
- skill-forge provides examples and recipes for packaging skills.
- conda-skills applies the approach to conda environments and the conda Python plugin ecosystem.

See {doc}`../how-to/create-a-skill` to start writing a skill, and {doc}`skill-safety` for the separate question of whether to trust its instructions.
