# Source environments and destination scope

The conda executable, packaged skills, and agent links can live in separate places. With `conda skill`, you choose a source environment for the skills and a destination for their links independently of the environment that runs conda and the plugin.

## The environment running conda

Conda loads plugins through the Python entry points installed in its own environment, commonly base. Installing `conda-skills` elsewhere does not register it with that executable. Follow {doc}`../how-to/installation` to install it in the right environment.

Activating a source environment is optional. A base conda installation with the plugin can read skills from a separate prefix without installing Python or the plugin into that prefix.

## The source environment

`list`, `install`, and `remove` take either `-n NAME` or `-p PREFIX`. They use conda's environment lookup and package records. With neither option, conda chooses its default target environment, normally the active environment or base when no environment is active.

The selected environment must already exist. The commands do not solve requirements, download packages, scan all environments, or create a missing environment. Use conda's package commands for those operations.

The source prefix supplies the package-owned skill and the target checked during removal. If you select a different prefix when removing a link, it can cause a conflict even if both prefixes contain a skill with the same name.

## The destination

The destination root is the current working directory unless `--global` selects the user's home directory. There is no upward search for a Git repository or workspace manifest. Run project-scoped commands from the project root you intend to change.

| Backend | Default destination | With `--global` |
| --- | --- | --- |
| `agents` | `<current directory>/.agents/skills/` | `<home>/.agents/skills/` |
| `claude` | `<current directory>/.claude/skills/` | `<home>/.claude/skills/` |

`agents` is the default. The link's final component is the skill name. Your client must support these paths; the plugin does not configure or launch clients.

For a skill already listed in an environment named `development`, these commands select the same source but different destinations:

```sh
conda skill install review-notes -n development
conda skill install review-notes -n development --backend claude
conda skill install review-notes -n development --global
```

Replace `development` and `review-notes` with your source environment and discovered skill if they differ. `--global` changes only the destination. It does not select base, install the plugin globally, or search every environment.

Running `install` or `remove` directly from your home directory still requires explicit `--global`. This prevents an accidental home-directory mutation when you intended to run from a project. Read-only `status` can inspect the current directory without that flag.

## Link lifetime

Links expose the current files at their targets. Update a source package in the same prefix and existing links expose the new content too. Removing or renaming the skill directory can break those links.

Relative targets let you move a project and source environment together if you keep their relative layout. Moving them independently can break the links. The plugin uses absolute targets across Windows drives. It has no persistent link database or automatic repair. Use `status` to inspect destinations and {doc}`../how-to/troubleshooting` to recover stale links.
