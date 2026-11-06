# Skill package format

This page describes what conda-skills accepts. It does not define every agent's instruction format or establish that a skill is safe to use.

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

`SKILL.md` is UTF-8 text. YAML frontmatter starts on the first line and is enclosed by lines containing exactly `---`. LF and CRLF line endings are accepted. The parsed YAML must be a mapping containing:

| Field | Requirement |
|---|---|
| `name` | The directory name, with the rules above. |
| `description` | A string containing non-whitespace text, at most 1024 characters. |

Other metadata and the instruction body are not interpreted by this plugin. Agents may impose additional requirements. See {doc}`../how-to/package-a-skill` for authoring and build steps, and {doc}`../explanation/ownership-and-trust` for the limits of validation.
