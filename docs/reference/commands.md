# Command reference

Run `conda skill` with a subcommand. The installed distribution and plugin entry point are named `conda-skills`. Use `conda skill --help` or `conda skill <command> --help` for help with arguments.

`conda skills` is a native alias for `conda skill`. Both accept the same commands and options. Examples use the singular spelling.

## Options by command

| Option | `list` | `status` | `link` | `unlink` | `init` | `quickstart` |
| --- | --- | --- | --- | --- | --- | --- |
| `-n NAME`, `--name NAME` | Yes | No | Yes | No | No | Yes |
| `-p PREFIX`, `--prefix PREFIX` | Yes | No | Yes | No | No | Yes |
| `--backend {agents,claude}` | No | Yes | Yes | Yes | No | Prompt |
| `--global` | No | Yes | Yes | Yes | Yes | Yes |
| `--force` | No | No | No | Yes | No | No |
| `--description TEXT` | No | No | No | No | Yes | Prompt |
| `--json` | Yes | Yes | Yes | Yes | Yes | Rejected |
| `--console {classic,json}` | Yes | Yes | Yes | Yes | Yes | Yes |
| `-v`, `--verbose` | Yes | Yes | Yes | Yes | Yes | Yes |
| `-q`, `--quiet` | Yes | Yes | Yes | Yes | Yes | Yes |
| `-h`, `--help` | Yes | Yes | Yes | Yes | Yes | Yes |

Put these options after the subcommand. For `list`, `link`, and quickstart's installed-skill branch, `-n` and `-p` are mutually exclusive source overrides. Without either, conda chooses its default target environment, normally the active environment or base if none is active. A missing source environment is an error. Lookup does not create it. `unlink` does not select a source environment.

The default backend is `agents`. The default destination root is the current working directory, not a discovered Git or workspace root. `--global` selects the home directory. See {doc}`../explanation/agent-discovery` for destination paths and examples.

Commands honor conda's JSON setting, including `CONDA_JSON=true`, as well as explicit `--json`. The interactive `quickstart` command rejects JSON before prompting. See {doc}`json` for result fields and error handling. Human output uses tables or plain confirmations, displays terminal control characters visibly, and treats skill text literally.

Conda's shared output helper also provides `--console`, `--verbose` (repeatable), and `--quiet`. These control conda's console and logging configuration. The plugin chooses its result format using conda's JSON setting. Use `--json` for its structured results. Verbosity and quiet mode do not replace the command's result with a different schema.

## `list`

```text
conda skill list [-n NAME | -p PREFIX] [--json]
```

Find and validate package-owned skill headers in the selected source environment, returning skills sorted by name. Project links are not inspected. Human output has Name, Package, Version, Description, and Path columns. An empty result says `No package-owned skills found.`

Malformed candidates and duplicate ownership cause discovery to fail without returning a partial list. Untracked directories are ignored. See {doc}`skill-format` for validation rules.

## `status`

```text
conda skill status [--backend {agents,claude} | --all] [--global] [--json]
```

Inspect the selected destination directory without resolving a source environment or checking package ownership. Entries are sorted by name. Human output has Name, State, Path, and Target columns. An empty or absent destination says `No skill entries found.`

`--all` inspects both existing backend directories (`agents`, then `claude`) in the selected scope and adds a Backend column. It cannot be combined with `--backend`. Use `--all --global` for both home directories. It does not scan other environments or infer which agent has loaded a skill.

| State | Meaning |
| --- | --- |
| `linked` | A symlink points to a directory containing a file named `SKILL.md`. |
| `broken` | A symlink does not meet the `linked` condition: for example, the target is missing, is a file, or lacks `SKILL.md`. |
| `unmanaged` | The destination entry is not a symlink. |

Status does not parse frontmatter or validate the contents of a linked directory. A link made by another tool can appear as `linked`. A regular directory is `unmanaged` even if it contains a valid skill.

## `link`

```text
conda skill link SKILL_NAME [-n NAME | -p PREFIX] [--backend {agents,claude}] [--global] [--json]
```

Discover the selected environment's skills and create a directory symlink for `SKILL_NAME`. Use the skill directory name shown by `list`, not the owning package name. Missing destination directories are created. This command does not download or install conda packages.

An existing symlink resolving to the same source is reused. Any other file, directory, or symlink at that destination is a conflict, including a broken link. Client-directory components that redirect through symlinks are rejected. There is no overwrite or force option.

Targets are relative when source and destination are on the same drive, and absolute across Windows drives. If directory symlink creation fails, the command reports an error without falling back to copies. Human success output starts with `Linked` and contains the skill name and link path.

## `unlink`

```text
conda skill unlink NAME [--backend {agents,claude}] [--global] [--force] [--json]
```

Inspect the named destination symlink and validate that its target matches a recorded conda skill with the same name before removing the link. This is independent of the active environment: the target identifies the source to check, without scanning the environment registry. The tool that originally made the link does not matter. Package files are never deleted, and empty parent directories remain.

An absent destination is a successful no-op without any source lookup. A broken or unverifiable target is refused with guidance to inspect `status`, then use `--force` if removal is intended. `--force` skips target verification and removes only the destination symlink. It never removes a regular file or directory and does not bypass redirected-parent checks. Human output is `Removed link for NAME.` or `No link to remove for NAME.`

Remove links before deleting source packages or environments. If the source is already gone, follow the inspection and forced-unlink procedure in {doc}`../how-to/troubleshooting`.

## `init`

```text
conda skill init NAME [--description TEXT] [--global] [--json]
```

Create `NAME/SKILL.md`, `NAME/build.py`, and `NAME/recipe/recipe.yaml` under the current directory. `--global` uses the home directory instead. Running from the home directory without `--global` is refused. No source environment is needed.

Names follow the same rules as installed skills: at most 64 lowercase ASCII letters, digits, and single separating hyphens. The description must contain non-whitespace text and be at most 1024 characters. Without `--description`, the header contains an authoring placeholder. User text is serialized as YAML data, including quotes, newlines, and control characters.

Any existing destination is a conflict, including an empty directory or a dangling symlink. There is no overwrite option. Filesystem failures can leave a partial skeleton. Inspect it before removing it or retrying.

The generated recipe builds a `noarch: generic` package named `agent-skill-NAME`, version `0.1.0`, build `0`. It uses Python 3.11 or newer to copy `SKILL.md` into `share/agent-skills/NAME/`. The generated `build.py` does not package companion files until you add them. No license is assigned.

Review the recipe and replace the placeholder instructions before distribution. The command does not build, install, or link the skeleton. See {doc}`../how-to/create-a-skill` for the authoring steps.

JSON output is one object with `name`, the absolute directory `path`, and the absolute `recipe` path. Human output identifies the files and gives the next build command.

## `quickstart`

```text
conda skill quickstart [-n NAME | -p PREFIX] [--global]
```

Run an interactive guide to create a skeleton or link installed skills. Both stdin and stdout must be terminals. Redirected input or output fails before prompting, with guidance to use `init`, `list`, or `link`. JSON mode is rejected, including when enabled through conda configuration or `CONDA_JSON=true`.

Choose `new` to enter a name and description, select a destination scope, and preview the new directory. Confirmation invokes the same skeleton generator as `init`. This branch does not look up a source environment.

Choose `link` to discover package-owned skills in the environment selected by `-n`, `-p`, or conda's default. Select one or more displayed numbers separated by spaces or commas, or enter `all`. Nothing is selected by default, and `cancel` exits without writes. Repeated numbers are treated as one selection. Review every selected source path and description, then choose the `agents` or `claude` backend.

Review every selected skill's instructions and supporting files before confirming. Package ownership does not establish trust. The guide previews every destination and checks the whole selection for conflicts before confirmation. It then calls the same linking operation as `link` for each skill. Existing matching links are reused, and unselected links are left alone. This is not a transaction: filesystem changes or failures during linking can leave earlier links in place.

The scope prompt offers `project` (the displayed current directory) and `home`. It defaults to `home` with `--global`, otherwise `project`. You can explicitly choose `project` even with `--global`. Choosing `home` without starting the command with `--global` fails without writes. The same guard applies when the current directory is the home directory. No upward project-root search occurs.

Confirmation defaults to no. Choosing `cancel` at the first prompt, declining confirmation, or interrupting input before confirmation makes no changes.

The guide follows fixed prompts without AI. It does not execute skill content, download packages, or create conda environments. Conda's automatic yes setting does not replace confirmation.

## Exit status

Successful operations exit with status zero, including repeated linking to the same source and unlinking when the destination is already absent. Validation, lookup, filesystem, and argument errors produce a nonzero exit status through conda's error handling. Do not parse human error text as a stable interface.
