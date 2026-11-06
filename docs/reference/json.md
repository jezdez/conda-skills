# JSON output

Use `--json` with any non-interactive command, or enable conda's JSON setting, including `CONDA_JSON=true`. Discovery, validation, and filesystem behavior stay the same. The interactive `quickstart` guide rejects JSON mode before prompting. Use the explicit commands in scripts.

A successful command writes one complete, unstyled JSON value to stdout. Paths are strings in the operating system's path format. Parse the document with a JSON parser, and do not depend on indentation, key order, or escaping style. Empty `list` and `status` results are `[]`.

The examples use absolute POSIX paths. Your paths depend on the selected environment and destination root.

## `list`

```sh
conda skill list -p /path/to/source-env --json
```

The result is an array sorted by skill name. Each object has:

| Field | Type | Meaning |
| --- | --- | --- |
| `name` | string | Skill directory name. |
| `description` | string | Validated description from the header. |
| `path` | string | Absolute path to the skill directory in the source prefix. |
| `package` | string | Owning conda package name. |
| `version` | string | Owning package version. |

```json
[
  {
    "name": "review-notes",
    "description": "Use when turning supplied code-review findings into a concise handoff for the author.",
    "path": "/path/to/source-env/share/agent-skills/review-notes",
    "package": "conda-skills-example",
    "version": "0.1.0"
  }
]
```

## `status`

```sh
conda skill status --json
```

The result is an array sorted by destination entry name. The command does not require a source environment.

| Field | Type | Meaning |
| --- | --- | --- |
| `name` | string | Destination entry name. |
| `state` | string | `linked`, `broken`, or `unmanaged`, as defined in the command reference. |
| `path` | string | Absolute destination entry path. |
| `target` | string | Resolved symlink target, or an empty string for an unmanaged entry. |

```json
[
  {
    "name": "review-notes",
    "state": "linked",
    "path": "/path/to/project/.agents/skills/review-notes",
    "target": "/path/to/source-env/share/agent-skills/review-notes"
  }
]
```

A broken link still has a target string, even if the target does not exist. A `linked` state does not confirm package ownership, valid frontmatter, trust, or that an agent has loaded the skill.

With `status --all --json`, the result remains one array. Each entry adds a string `backend` field (`agents` or `claude`). Entries are grouped in that backend order and sorted by name within each group. The default single-backend output is unchanged. An error inspecting either directory fails the command before it emits a partial array. `--global` selects home scope for both directories, without a source environment lookup.

## `install`

```sh
conda skill install review-notes -p /path/to/source-env --json
```

The result is an object with string fields `name` and `path`, whether the command creates a link or reuses an existing matching link.

```json
{"name": "review-notes", "path": "/path/to/project/.agents/skills/review-notes"}
```

## `remove`

```sh
conda skill remove review-notes -p /path/to/source-env --json
```

The result is an object with string `name` and boolean `removed`. `true` means the matching link was removed, while `false` means the destination was absent. Both outcomes require a valid, discoverable source skill.

```json
{"name": "review-notes", "removed": true}
```

## `init`

```sh
conda skill init review-notes --description "Review supplied notes" --json
```

The result is an object with string fields `name`, `path`, and `recipe`. The path points to the new authoring skeleton. The `recipe` field is the absolute path to its conda recipe. The skeleton is not yet an installed skill or a client link.

```json
{"name": "review-notes", "path": "/path/to/project/review-notes", "recipe": "/path/to/project/review-notes/recipe/recipe.yaml"}
```

## Errors and literal text

Check the exit status before parsing a response as a successful result. On failure, the process exits nonzero and conda emits its normal error response. There is no plugin-specific error schema. Conda's fields can vary with the error type and conda version.

Descriptions and paths remain literal data. JSON escapes control characters according to JSON syntax, but decoded strings may still contain those characters. Escape decoded values appropriately if you later print them to a terminal or insert them into HTML. Human-mode terminal escaping is not applied to JSON data.
