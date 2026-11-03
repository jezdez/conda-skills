# conda-skills

Connect conda-packaged agent skills to your coding agent. `conda skill` finds
skills installed in a conda environment and links their complete directories
into a project or your home directory.

This implements the package-manager approach described in Pavel Zwerschke's
[Managing Agent Skills with Your Package Manager](https://pavel.pink/blog/pixi-skills).
It uses conda environments rather than Pixi workspace discovery. It is a separate
implementation, not a wrapper around pixi-skills.

## Try it from this checkout

Requires Pixi for development. The plugin itself requires Python 3.11 or newer
and conda 26.9 or newer, with conda installed from a conda channel rather than PyPI.
No public package release is available yet.

```sh
pixi install --locked
pixi run --locked install
pixi run --locked conda skill --help
```

For normal use, the plugin must be installed in the environment that provides
your `conda` executable. Skills may live in another environment selected with
`-n` or `-p`. Installing this plugin in an arbitrary environment does not make a
different conda executable discover it.

## Link a packaged skill

First install a reviewed skill package through conda using your chosen channel
or local artifact. It must install a folder such as:

```text
<prefix>/share/agent-skills/example/
  SKILL.md
  references/
```

Its `SKILL.md` must be listed in an installed conda package record, have a `name`
matching its folder, and a nonempty text `description`. Untracked folders are not
discovered. The command does not execute skill instructions or verify their
trustworthiness. Read skills before exposing them to an agent.

From the project where you want to use the skill:

```sh
conda skill list -n development
conda skill install example -n development --backend agents
conda skill status --backend agents
conda skill remove example -n development --backend agents
```

Replace `example` with a name from `list`. Without `-n` or `-p`, conda selects its
default environment, normally the active environment or base when none is active.
`install` creates a relative directory symlink. It does not download or install
packages. References and other companion files remain available through the link.

## Destinations and automation

| Backend | Project destination | With `--global` |
| --- | --- | --- |
| `agents` (default) | `.agents/skills/` | `~/.agents/skills/` |
| `claude` | `.claude/skills/` | `~/.claude/skills/` |

Run project commands from the intended project root. Mutating commands run from
your home directory also require `--global`, to avoid accidental global changes.
The shared `agents` path is
used by Codex and current Kilo, among other clients. This plugin does not modify
client configuration or launch clients, and client discovery is not tested here.

Each subcommand accepts `--json`. Successful `list` and `status` output is a JSON
array. `install` returns the skill name and link path. `remove` returns the name
and a boolean `removed`. Errors use conda's JSON error handling and a nonzero exit
status. Put environment options after `list`, `install`, or `remove`:

```sh
conda skill list -p /path/to/environment --json
conda skill install example -p /path/to/environment --global --json
```

The source environment and destination scope are independent. `--global` changes
where links go; it does not select or scan every environment on the machine.

## Conflicts and stale links

Installing the same link twice is harmless. An existing file, directory, or link
to another source is a conflict, even if that link is broken. The plugin will not
overwrite it. Client-directory symlinks that redirect writes are also rejected.

Removal only unlinks a destination matching the named skill in the selected
source environment. Package files remain untouched. This checks the target, not
which tool originally created the link. `status` reports links and unmanaged
entries, including broken links, without claiming they belong to this plugin.

Remove links before deleting the source package or environment. If the source
is already gone, `status` can show the dangling link but automatic removal is
unavailable because package ownership can no longer be established. Inspect and
remove that link manually. Updating a package in the same prefix makes its new
contents available through existing links.

Windows directory symlinks need Developer Mode or suitable privileges. Across
different Windows drives, links use absolute targets because relative paths are
not possible. Failure is reported without falling back to copying files. Moving a
project and its environment independently can break relative links. Inspect and
remove each stale link manually, then reinstall it from the new source environment.

## Development

```sh
pixi run --locked check
pixi run --locked build
```

Tests exercise actual installed `conda skill` commands and filesystem operations
using temporary package records and isolated client homes. The locked environment
covers Linux, macOS ARM64, and Windows, but execution has so far been verified on
macOS ARM64 only. The `check` task runs pytest, Ruff, and ty. The prek configuration
uses that task for Git hooks when you choose to install them in a Git repository.

There is no interactive manager, package solver, activation hook, skill registry,
automatic client discovery, or persistent link database. Manage package versions
with conda and keep linking explicit.

Original code is licensed under Apache-2.0. The blog and pixi-skills are referenced
as prior art; their source code is not bundled.
