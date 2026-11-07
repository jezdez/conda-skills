# Skill safety

Package ownership identifies the installed conda package that recorded a skill header. You still need to assess the publisher and instructions yourself. Ownership does not establish safety or guarantee that an agent will follow the instructions correctly.

## Package and file checks

The plugin reads conda package records in the selected environment and looks for `share/agent-skills/<name>/SKILL.md` in each package's file list. It ignores untracked directories, even if their headers are valid. A pip-only installation does not create the conda ownership record needed for discovery.

For each candidate, the plugin validates the directory name, YAML name and description, and filesystem containment. Duplicate ownership of a skill name in the same environment is an error. See {doc}`../reference/skill-format` for the exact requirements.

The resulting `package` and `version` fields describe the installed package record. The plugin does not verify cryptographic signatures or file hashes, authenticate the publisher, audit supporting scripts, or prove that current files still match their original archive. Companion files are checked for containment, not individually attributed to packages.

## What linking changes

Linking exposes the complete skill directory, including its references and scripts, through a link at a path used by agent clients. The plugin does not execute these files. An agent reading the instructions may later request operations based on them.

Review the instructions and supporting files before linking. Apply your normal package-source policy, inspect changes when updating packages, and use the agent client's own permissions to control what it can read or execute. A source update can change content exposed by an existing link without another `conda skill link` command.

During discovery, containment checks reject skill roots outside the source environment and companion paths outside the skill root. They do not sandbox later agent actions or protect against concurrent modifications of the source files.

## What status checks

Status checks the destination filesystem without requiring a source environment. A symlink to a directory containing `SKILL.md` is `linked`, even if it was not created by this plugin or does not point into a conda environment. Status does not read the header to validate it.

You can therefore inspect links after deleting a source environment, even though discovery is no longer possible. The status table does not establish trust or package ownership.

## What unlinking verifies

The plugin has no persistent record of links it created. Unlinking inspects the destination symlink's target and validates that it matches a recorded conda skill with the requested name. It does not depend on the active environment or scan the environment registry. A link created by another tool can pass these checks, so the plugin cannot identify which tool created it. An absent destination succeeds without source lookup.

Remove links before uninstalling the source package or deleting its environment. A broken or unverifiable target is refused with guidance to inspect `status` before using `--force`. Forced unlinking removes only the symlink, never package files, a regular file, or a directory. It does not bypass redirected-parent checks. Follow {doc}`../how-to/troubleshooting` before removing a stale link.

## Pins and hashes

| Record | What it fixes | What it leaves open |
| --- | --- | --- |
| Exact version in `conda.toml` or `conda-meta/pinned` | The allowed version of one package | Builds, dependencies, local file changes, and whether the instructions are appropriate |
| Version plus build and channel constraints | A narrower package selection | Dependency changes and content review |
| Reviewed `conda.lock` | Resolved package URLs and hashes for the recorded environments and platforms | Publisher approval, local modifications, client behavior, and future artifact availability |
| Recipe source URL plus checksum | The source archive a package build is meant to consume | The rest of the recipe, build dependencies, patches, and final package identity |

Conda and conda-workspaces apply these records during package selection and installation. Conda-skills does not check them itself, and none automatically approves instructions for an agent. Use {doc}`../how-to/update-skills` to change installed versions and {doc}`../how-to/package-a-skill` to pin a package's source.
