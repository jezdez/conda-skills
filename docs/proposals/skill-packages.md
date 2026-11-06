# Proposal: package Agent Skills with conda

:::{admonition} Draft for discussion
:class: note

This is a proposal from the conda-skills project, not an accepted conda specification or CEP. It has not been endorsed by the Agent Skills, pixi-skills, or skill-forge maintainers. It does not change current tool behavior. See {doc}`../reference/skill-format` for what conda-skills accepts today.
:::

## Purpose and prior work

Define a small, shared convention so conda tools can find and distribute Agent Skills without requiring a particular agent, package manager frontend, or authoring tool.

The starting point is Pavel Zwerschke's [pixi-skills](https://github.com/pavelzw/pixi-skills), [skill-forge](https://github.com/pavelzw/skill-forge), and [description of packaging skills](https://pavel.pink/blog/pixi-skills#creating-a-skill-package). His post also credits Moritz Wilksch as a coauthor of pixi-skills. This proposal documents that approach and identifies decisions that need agreement across implementations.

The [Agent Skills specification](https://agentskills.io/specification) remains the authority for skill content. This proposal concerns its placement in conda packages, not a competing instruction format.

## Proposed requirements

In this draft, **MUST** describes a requirement for conformance, **SHOULD** a recommendation with possible justified exceptions, and **MAY** an optional choice. These terms apply to the proposal, not to claims about existing packages.

### Installed layout

A package distributing a skill MUST install its header at this exact prefix-relative path:

```text
share/agent-skills/<name>/SKILL.md
```

`<name>` is one directory component. A skill MUST NOT be nested another level below `share/agent-skills/`. It MAY include supporting files and directories below its own root, such as:

```text
share/agent-skills/review-notes/
  SKILL.md
  references/
    review-checklist.md
  scripts/
    check-notes.py
```

The package MUST record the header and every companion file it distributes in its conda file list. Companion paths and symlink targets MUST remain within the skill root, and the skill root MUST resolve within the installed environment. Packages SHOULD avoid symlinks where ordinary files suffice. Installing a skill package MUST NOT automatically copy or link its content into user or project agent directories through installation hooks.

A package MAY contain several skills or combine skills with software. It MUST keep each skill's content in its own root. Two packages MUST NOT claim the same skill root in one environment. Consumers MUST report ambiguous ownership rather than silently choose one package.

### Header and identity

`SKILL.md` MUST be UTF-8 text with Agent Skills YAML frontmatter. Its `name` MUST match the directory name, and its `description` MUST meet the Agent Skills requirements. Additional fields retain their meaning under that specification. Consumers MUST NOT treat fields such as `allowed-tools` as permission granted by package installation.

Package names and skill names are separate identifiers. A single-skill package SHOULD use `agent-skill-<name>`, following skill-forge's convention. Consumers MUST NOT require that package-name prefix to discover a recorded skill. The version associated with a packaged skill is its owning package's version and build, not the version of a library named in its instructions.

Package paths MUST be valid on every platform the package supports. This includes avoiding reserved Windows device names when distributing a platform-independent package. Whether to require one narrower naming profile for every platform remains an open question below.

### Dependencies and portability

Use `noarch: generic` when the payload is platform-independent data and has no platform-specific installation needs. Including executable scripts does not by itself establish portability. Authors MUST declare and test the tools and platforms their packaged content requires.

Conda's existing dependency semantics apply:

- `requirements.run` requires software in the same environment as the skill package.
- `requirements.run_constraints` limits a package's version if it is present, without installing it.
- A library mentioned only in the instruction text has no solver effect.

For example, a Polars skill may declare `polars >=1.38,<2` as a runtime constraint. That only constrains Polars in the environment containing the skill package. It does not constrain a separate application environment or select the interpreter used by an agent.

### Discovery and exposure

A consumer claiming to discover *conda-packaged* skills MUST use installed conda package records to establish ownership of candidate headers. A directory scan alone is insufficient for that claim. Consumers MAY offer a separate mode for untracked local skills, but MUST distinguish those from package-owned skills.

Consumers MUST NOT execute skill instructions or companion scripts merely to discover a skill. They SHOULD preserve the directory structure when making a skill available to an agent so relative references continue to work. Installation of the package and exposure to an agent are separate operations.

Conformance to this layout does not establish publisher identity, archive integrity, instruction safety, or compatibility with an agent. Those are separate checks and policies. Current conda-skills checks companion-file containment but does not attribute every companion file to an individual package record or verify its archive hash.

## Outside this proposal

This proposal does not prescribe agent discovery directories such as `.agents/skills/` or `.claude/skills/`, whether a frontend copies or symlinks content, interactive selection, project configuration, or client reload behavior. It also does not introduce a registry, package metadata field, signing format, schema, or mandatory implementation library.

The source checkout layout is unrestricted. Keeping a recipe beside `SKILL.md` or under `recipe/` does not change the installed package contract. Authoring with `conda skill init` is optional.

## Compatibility and open decisions

These points need review with existing tool and package maintainers before adoption:

| Question | Proposed direction | Existing difference or tradeoff |
|---|---|---|
| Must the header contain a matching name? | Follow the Agent Skills requirement. | Pixi-skills also accepts headers without a name. Existing packages need a compatibility check before this becomes a common requirement. |
| Should names be ASCII-only and Windows-safe everywhere? | Require portability for the package's supported platforms. | Conda-skills currently applies its ASCII pattern and Windows device-name exclusions on every platform. A universal profile would be stricter than platform-local validity. |
| Must every consumer use package records? | Require records for a package-ownership claim. | Some tools discover skills by scanning directories. They could retain that behavior without describing every result as package-owned. |
| Can several packages contribute to one skill root? | Disallow it to keep ownership and updates unambiguous. | This prevents splitting references or scripts into a separate package under the same root. |
| What happens to an invalid skill in a bundle? | Keep this a frontend decision, with a visible diagnostic. | Failing the whole discovery operation and skipping one invalid candidate have different usability tradeoffs. |

Before submitting a CEP, agree on the normative Agent Skills revision or compatibility policy, test the proposal against representative skill-forge packages, and review it with the authors of pixi-skills and other consumers. Record any required migrations rather than treating current conda-skills restrictions as community agreement.

## Reviewing the draft

A useful review starts with a real package: inspect its installed paths and package records, load its header with each relevant tool, and check supporting-file access. Include cases with multiple skills, name mismatches, duplicate owners, and escaping paths. Passing those checks demonstrates specific interoperability, not an agent's acceptance of the instructions.

Discuss changes in the [conda-skills issue tracker](https://github.com/jezdez/conda-skills/issues). This is a working proposal until maintainers agree on a home and adoption process.
