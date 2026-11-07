# Skill package format

This page describes what conda-skills accepts. It does not define every agent's instruction format or establish that a skill is safe to use.

For a proposed shared convention across tools, see {doc}`../proposals/skill-packages`. That draft is not an adopted standard and does not replace this implementation reference.

## Relationship to Agent Skills

The [Agent Skills specification](https://agentskills.io/specification) defines the underlying format: a directory containing `SKILL.md`, YAML frontmatter with `name` and `description`, and Markdown instructions. It also defines optional fields such as `license`, `compatibility`, and `metadata`, and recommends `scripts/`, `references/`, and `assets/` directories for supporting files.

Conda-skills checks required metadata and filesystem containment, but it is not a complete specification validator. It does not validate optional fields or interpret their meaning. In particular, a skill's `allowed-tools` field does not grant permissions through this plugin. The checks below also restrict names to ASCII and reject Windows device names for portability.

The installed path `share/agent-skills/` is a package-distribution convention shared with pixi-skills and skill-forge, not a requirement of the Agent Skills specification. Likewise, `.agents/skills/` and `.claude/skills/` are client discovery conventions. Refer to the specification for authoring rules and your agent's documentation for supported fields and behavior.

## Installed layout and ownership

Each candidate header must be recorded in an installed conda package at:

```text
share/agent-skills/NAME/SKILL.md
```

Untracked directories are ignored. A selected environment must not have multiple package records claiming the same skill name. A package may contain more than one skill.

The skill root and header must resolve inside the source environment. Companion files must remain inside the resolved skill root, including when they are symlinks. The entire directory is linked into the agent's skill directory so relative references to companion files keep working.

## Name

- At most 64 characters, matching `[a-z0-9]+(?:-[a-z0-9]+)*`.
- Lowercase ASCII letters and digits, with single hyphens between nonempty segments.
- No Windows device names: `con`, `prn`, `aux`, `nul`, `com1` through `com9`, or `lpt1` through `lpt9`. This restriction applies on every platform.
- The header's `name` must exactly match its directory name.

## Header

`SKILL.md` is a regular UTF-8 text file no larger than 1 MiB. This read limit is an implementation safeguard, not an Agent Skills specification requirement. YAML frontmatter starts on the first line and is enclosed by lines containing exactly `---`. LF and CRLF line endings are accepted. The parsed YAML must be a mapping containing:

| Field | Requirement |
|---|---|
| `name` | The directory name, with the rules above. |
| `description` | A string containing non-whitespace text, at most 1024 characters. |

Other metadata and the instruction body are not interpreted by this plugin. Agents may impose additional requirements. See {doc}`../how-to/package-a-skill` for authoring and build steps, and {doc}`../explanation/skill-safety` for the limits of validation.
