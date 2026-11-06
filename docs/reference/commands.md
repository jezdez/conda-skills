# Command reference

The command is `conda skill`; the installed distribution and plugin entry-point name are `conda-skills`. A subcommand is required. Use `conda skill --help` or `conda skill <command> --help` for parser help.

## Options by command

| Option | `list` | `status` | `install` | `remove` | `init` | `quickstart` |
| --- | --- | --- | --- | --- | --- | --- |
| `-n NAME`, `--name NAME` | Yes | No | Yes | Yes | No | Yes |
| `-p PREFIX`, `--prefix PREFIX` | Yes | No | Yes | Yes | No | Yes |
| `--backend {agents,claude}` | No | Yes | Yes | Yes | No | Prompt |
| `--global` | No | Yes | Yes | Yes | Yes | Yes |
| `--description TEXT` | No | No | No | No | Yes | Prompt |
| `--json` | Yes | Yes | Yes | Yes | Yes | Rejected |
| `--console {classic,json}` | Yes | Yes | Yes | Yes | Yes | Yes |
| `-v`, `--verbose` | Yes | Yes | Yes | Yes | Yes | Yes |
| `-q`, `--quiet` | Yes | Yes | Yes | Yes | Yes | Yes |
| `-h`, `--help` | Yes | Yes | Yes | Yes | Yes | Yes |

Put these options after the subcommand. `-n` and `-p` are mutually exclusive. Without either, conda chooses its default target environment, normally the active environment or base if none is active. A missing source environment is an error; lookup does not create it.

The default backend is `agents`. The default destination root is the current working directory, not a discovered Git or workspace root. `--global` selects the home directory. See {doc}`../explanation/scope` for destination paths and examples.

Commands use conda's JSON setting, including `CONDA_JSON=true`, as well as explicit `--json`. The interactive `quickstart` command rejects JSON before prompting. See {doc}`json` for successful result fields and error handling. Human output uses tables or plain confirmations, with terminal control characters made visible and skill text treated literally.

Conda's shared output helper also provides `--console`, `--verbose` (repeatable), and `--quiet`. These control conda's console and logging configuration. The plugin chooses its result format using conda's JSON setting; use `--json` for its structured results. Verbosity and quiet mode do not replace the command's result with a different schema.

## `list`

```text
conda skill list [-n NAME | -p PREFIX] [--json]
```

Discover package-owned skill headers in the selected source environment, validate them, and return skills sorted by name. This does not inspect project links. Human output has Name, Package, Version, Description, and Path columns; an empty result says `No package-owned skills found.`

Discovery rejects malformed candidates and duplicate ownership rather than silently returning a partial list. Untracked directories are ignored. See {doc}`../how-to/package-a-skill` for validation rules.

## `status`

```text
conda skill status [--backend {agents,claude}] [--global] [--json]
```

Inspect the selected destination directory without resolving a source environment or checking package ownership. Entries are sorted by name. Human output has Name, State, Path, and Target columns; an empty or absent destination says `No skill entries found.`

| State | Meaning |
| --- | --- |
| `linked` | A symlink points to a directory containing a file named `SKILL.md`. |
| `broken` | A symlink does not meet the `linked` condition: for example, the target is missing, is a file, or lacks `SKILL.md`. |
| `unmanaged` | The destination entry is not a symlink. |

Status does not parse frontmatter or validate the contents of a linked directory. A link made by another tool can appear as `linked`; a regular directory is `unmanaged` even if it contains a valid skill.

## `install`

```text
conda skill install SKILL_NAME [-n NAME | -p PREFIX] [--backend {agents,claude}] [--global] [--json]
```

Discover the selected environment's skills and create a directory symlink for `SKILL_NAME`. Use the skill directory name shown by `list`, not the owning package name. Missing destination directories are created. This command does not download or install conda packages.

An existing symlink resolving to the same source is reused. Any other file, directory, or symlink at that destination is a conflict, including a broken link. Client-directory components that redirect through symlinks are rejected. There is no overwrite or force option.

Targets are relative when source and destination are on the same drive, and absolute across Windows drives. If directory symlink creation fails, the command reports an error without falling back to copies. Human success output starts with `Linked` and contains the skill name and link path.

## `remove`

```text
conda skill remove SKILL_NAME [-n NAME | -p PREFIX] [--backend {agents,claude}] [--global] [--json]
```

Discover the named skill in the selected source environment, then unlink only a destination symlink that resolves to that source. This checks the target, not which tool originally made the link. Package files are never deleted. Empty parent directories remain.

An absent destination is a successful no-op, but the source skill must still be discoverable. An unrelated entry or redirected client directory is an error. Human output is `Removed link for SKILL_NAME.` or `No link to remove for SKILL_NAME.`

Remove links before deleting source packages or environments. When ownership can no longer be established, follow the manual recovery procedure in {doc}`../how-to/troubleshooting`.

## `init`

```text
conda skill init NAME [--description TEXT] [--global] [--json]
```

Create `NAME/SKILL.md`, `NAME/build.py`, and `NAME/recipe/recipe.yaml` under the current directory. `--global` uses the home directory instead. Running from the home directory without `--global` is refused. No source environment is needed.

Names follow the same rules as installed skills: at most 64 lowercase ASCII letters, digits, and single separating hyphens. The description must contain non-whitespace text and be at most 1024 characters. Without `--description`, the header contains an authoring placeholder. User text is serialized as YAML data, including quotes, newlines, and control characters.

Any existing destination is a conflict, including an empty directory or a dangling symlink. There is no overwrite option. Filesystem failures can leave a partial skeleton; inspect it before removing it or retrying.

The generated recipe builds a `noarch: generic` package named `agent-skill-NAME`, version `0.1.0`, build `0`. It uses Python 3.11 or newer to copy `SKILL.md` into `share/agent-skills/NAME/`. The generated `build.py` does not package companion files until you add them. No license is assigned. Review the recipe and replace the placeholder instructions before distribution. The command does not build, install, or link the skeleton. See {doc}`../how-to/create-a-skill` for the authoring steps.

JSON output is one object with `name`, the absolute directory `path`, and the absolute `recipe` path. Human output identifies the files and gives the next build command.

## `quickstart`

```text
conda skill quickstart [-n NAME | -p PREFIX] [--global]
```

Run an interactive guide to create a skeleton or link an installed skill. Both stdin and stdout must be terminals. Redirected input or output fails before prompting, with guidance to use `init`, `list`, or `install`. JSON mode is rejected, including when enabled through conda configuration or `CONDA_JSON=true`.

Choose `new` to enter a name and description, select a destination scope, and preview the new directory. Confirmation invokes the same skeleton generator as `init`. This branch does not look up a source environment.

Choose `link` to discover package-owned skills in the environment selected by `-n`, `-p`, or conda's default. Select a skill by its displayed number, review its source path and description, and choose the `agents` or `claude` backend. Review the skill's instructions and supporting files before confirming; package ownership does not establish trust. The guide previews the link destination and calls the same linking operation as `install` after confirmation.

The scope prompt offers `project` and `home`. Choosing `home` without starting the command with `--global` fails without writes. The same guard applies when the current project directory is the home directory. With `--global`, the scope prompt still lets you choose the project. Confirmation defaults to no. Choosing `cancel` at the first prompt, declining confirmation, or interrupting input before confirmation makes no changes.

The guide is deterministic and does not use AI, execute skill content, download packages, or create conda environments. It does not use conda's automatic yes setting in place of confirmation.

## Exit status

Successful operations exit with status zero, including repeated installation of the same link and removal when the destination is already absent. Validation, lookup, filesystem, and argument errors produce a nonzero exit status through conda's error handling. Do not parse human error text as a stable interface.
