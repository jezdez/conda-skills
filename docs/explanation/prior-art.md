# Prior art

Conda-skills was inspired by Pavel Zwerschke's [pixi-skills](https://github.com/pavelzw/pixi-skills) and [skill-forge](https://github.com/pavelzw/skill-forge): distributing agent instructions and their supporting files through existing package managers.

His post, [Managing Agent Skills with Your Package Manager](https://pavel.pink/blog/pixi-skills), describes the approach that this project adapts to conda.

## Bringing the approach to conda

Conda-skills brings this approach to conda's Python stack. It is an independent implementation built on conda's plugin API, environment lookup, and installed package records. It does not bundle pixi-skills source code.

The projects share a useful package layout: a skill lives at `share/agent-skills/NAME/SKILL.md`, with companion files alongside it. The generated conda-skills recipe follows skill-forge's `agent-skill-NAME` naming convention and `noarch: generic` packaging. That shared layout lets authors use the same packaging idea without tying their instructions to one agent's configuration directory.

Conda-skills discovers headers recorded in conda packages, then links the selected directory into `.agents/skills/` or `.claude/skills/`. It requires a matching `name` in the skill header and checks that files remain within their expected directories. Pixi-skills has different discovery and validation rules, including support for headers without a name. A shared package layout does not mean that every skill accepted by one tool is accepted by the other.

## Complementary projects

- **pixi-skills** makes the package-manager approach available to Pixi users.
- **skill-forge** provides examples and recipes for packaging skills.
- **conda-skills** applies the approach to conda environments and the conda Python plugin ecosystem.

See {doc}`../how-to/create-a-skill` for packaging compatibility details, and {doc}`ownership-and-trust` for the separate question of whether to trust a skill's instructions.
