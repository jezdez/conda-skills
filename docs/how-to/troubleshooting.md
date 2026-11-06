# Troubleshooting

## Skill-forge metadata fails to load

With conda-rattler-solver 26.10.2, channel loading may fail with `Object of type bytes is not JSON serializable` while processing `attestations_sha256`. This happens before conda-skills runs. A verified workaround is to use libmamba for the affected package command:

```sh
conda create --solver libmamba --prefix ../skills --override-channels -c https://prefix.dev/skill-forge -c conda-forge "agent-skill-polars==0.0.8"
```

For `conda workspace lock`, which has no solver flag, select libmamba for the current invocation in Bash or zsh:

```sh
CONDA_SOLVER=libmamba conda workspace lock
```

In PowerShell, set `$env:CONDA_SOLVER = "libmamba"` for the command and restore its previous value afterward. This workaround changes neither package ownership checks nor signature verification policy. Do not disable plugins or verification to bypass an integrity failure.

## `conda skill` is not recognized

Check `conda --version` and the environment that provides the executable. The plugin needs conda 26.9 or newer and Python 3.11 or newer, and must be installed in that same environment.

Follow {doc}`installation`, then run `conda skill --help`. Check whether `CONDA_NO_PLUGINS` or your invocation's `--no-plugins` option disables external plugins. Installing the plugin in a skill source environment or a conda-workspaces development environment does not register it with base conda.

## `conda pypi` is not recognized or an editable install fails

Install `conda-pypi` 0.12 or newer from conda-forge into the environment that runs conda, as shown in {doc}`installation`. Check `conda pypi install --help` for `-n`, `-p`, and `-e`. Older versions had environment-selection bugs; keep the explicit target on both prerequisite and editable-install commands.

Run `conda pypi install -n base -e .` from the checkout root, substituting the actual conda-owning prefix with `-p` when needed. Editable installs do not resolve runtime dependencies, so install the guide's `rich` and `ruamel.yaml` prerequisites too. A missing public `conda-skills` package is expected before the first release; use the checkout or a local conda artifact meanwhile.

## `list` finds no skills

Use `conda skill list -p <source-prefix>` to make the source explicit. Check that the intended package was installed in that prefix with `conda list -p <source-prefix>`.

Conda's package record must contain the exact path `share/agent-skills/<name>/SKILL.md`. A manually copied directory or pip-only installation is not enough. Compare your installed layout and recipe with {doc}`package-a-skill`. To inspect project links instead of source skills, use `status` rather than `list`.

Discovery fails if a package contains malformed frontmatter, two packages claim the same skill, or a skill path escapes its environment. Correct or replace the source package through conda before retrying.

## Installation refuses an existing destination

Run `conda skill status` with the same `--backend` and `--global` settings used for installation. A regular file or directory, a link to a different source, and a broken link all block installation. There is no force flag.

If the entry belongs to another tool, manage it through that tool or choose a different project or backend. Review and preserve an existing directory's contents before removing it. The plugin reuses a link to the same resolved source without replacing it.

## A link is broken after moving or deleting its source

`conda skill status` works without the source environment and reports the destination and resolved target. Check whether the source package was removed, the environment moved, or the project moved independently of a relative target. A target directory lacking `SKILL.md` is also reported as broken.

If the original package-owned source still exists, remove its matching link with `conda skill remove <name> -p <original-prefix>` before changing the source. If ownership is no longer available, automatic removal cannot proceed. Inspect and remove only the stale symlink, then install from a valid source environment again.

For the tutorial's project-local `review-notes` link, inspect first:

::::{tab-set}

:::{tab-item} POSIX

```sh
ls -ld .agents/skills/review-notes
readlink .agents/skills/review-notes
```

After confirming that this is the stale symlink you intend to remove:

```sh
unlink .agents/skills/review-notes
```
:::

:::{tab-item} PowerShell

```powershell
Get-Item -Force -LiteralPath .agents/skills/review-notes | Format-List FullName,LinkType,Target
```

After confirming that the entry is the stale directory symbolic link you intend to remove, use Command Prompt's directory-link removal without `/s`:

```powershell
cmd /c rmdir .agents\skills\review-notes
```
:::

::::

Adapt the exact path for your backend and scope. Do not add a trailing separator or use recursive deletion: the operation should remove the link itself, not traverse its target. If inspection shows a real directory, stop and preserve its contents. After cleanup, `conda skill install <name> -p <new-prefix>` can create a new link. Substitute an actual discovered skill name and source prefix for the placeholders.

## A client directory is redirected

The plugin rejects symlinked or redirected components such as `.agents` or `.agents/skills`. This check applies to status as well as mutations. Inspect the directory structure outside the plugin and use a destination whose client directories are real directories under the intended root. Do not remove shared client-directory links without understanding the other tools that use them.

## Windows cannot create a symlink

Enable Developer Mode or obtain directory-symlink privileges according to your system policy. The plugin reports the operating-system error and does not silently copy the skill. Source and destination on different drives use an absolute target, so moving that source later requires relinking.

## Removal fails or leaves files behind

Use the same source prefix, backend, and scope as installation. The source skill must still be package-owned, and the destination must be a symlink to that source. If the link is already absent, removal succeeds without changing anything, provided the plugin can still discover the source skill.

Removal leaves source package files and empty `.agents/skills/` or `.claude/skills/` directories intact. To remove the package too, uninstall it with conda after removing its links.

## Output is JSON unexpectedly

The plugin follows conda's configured JSON mode, including `CONDA_JSON=true`. Check that setting and your conda configuration if you expected a table. In scripts, check the command's exit status and parse the entire JSON document; errors use conda's error response rather than the plugin's success shape.
