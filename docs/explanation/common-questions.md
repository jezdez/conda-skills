# Common questions

## Do I need conda-skills to use Agent Skills?

No. An agent that supports the [Agent Skills format](https://agentskills.io/specification) can read skills without this plugin. Conda-skills manages skills distributed as conda packages and creates links in supported agent directories. You still need to check which directories your agent reads.

See {doc}`agent-discovery` for how package discovery differs from agent discovery.

## Why not copy SKILL.md into my project?

Copying works, especially for a local skill you maintain yourself. Copy any supporting files it needs too. With separate copies, you track their origins and update each copy yourself.

Conda packages record a version and file list. Conda-skills lets several projects use one installed directory without duplicating it. That also means a package update affects every link pointing there. See {doc}`../how-to/update-skills` before updating a shared source.

## Is this another skill format?

No. The instructions use the Agent Skills format. The installed package layout follows the conventions shared with pixi-skills and skill-forge. Conda-skills adds checks for package ownership, required metadata, and filesystem containment, but it is not a complete specification validator.

See {doc}`../reference/skill-format` for the exact checks and {doc}`prior-art` for the projects behind the approach.

## Does it install an agent or the library a skill describes?

Conda-skills does not install or start an agent. A skill about a library can contain instructions without that library's code. Installing its package with conda may install dependencies declared by the package. Creating a skill link installs no additional software.

See {doc}`agent-discovery` for examples of package and library dependencies.

## Does packaging make a skill trustworthy?

No. A package record identifies the package associated with the installed header. It does not establish that the instructions are safe or suitable for your project. Read the skill and its supporting files before making them available to an agent.

See {doc}`skill-safety` for what the checks establish and what remains your decision.

## Why separate package installation from skill linking?

You may want to inspect a package before using it, or use a skill in one project but not another. Conda installs the files in an environment. The `conda skill link` command makes a selected skill available through a project or home-directory link. `conda skill unlink` removes that link and leaves the package installed.

See {doc}`agent-discovery` for how the source environment and destination are chosen independently.

## How do I remove a skill and its package?

Use `conda skill unlink NAME` to remove its project or home-directory link, then `conda remove PACKAGE` in the source environment to uninstall the package. The skill and package names may differ. Repeat unlinking for other destinations that use the package, and review conda's transaction plan before confirming removal.

There is no automatic package removal through `unlink`. Other projects may still use the files, and one package may supply several skills or software. If the source is already gone, inspect the broken link with `status` before removing it with `unlink --force`. Follow {ref}`remove-a-skill-completely` for the full procedure.

## What happens when I update a skill package?

Existing links expose the installed directory's current content. An update can therefore change the instructions available to several projects without another linking command. Stop affected agent sessions and remove their links before updating, then review the new files before reconnecting them. Removing a link does not clear instructions an agent has already loaded.

Follow {doc}`../how-to/update-skills` for updates, pins, and rollback.

## Do I need conda-workspaces?

No. An ordinary conda environment is enough. Conda-workspaces is useful when a team wants a manifest and lockfile describing the same package selection. It is optional for using skills and required only for this repository's contributor tooling.

Start with {doc}`../tutorials/skill-forge` for one skill, or use {doc}`../how-to/project-skills` when you need to share the environment.
