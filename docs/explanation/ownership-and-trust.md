# Package ownership and trust

Package ownership identifies the installed conda package that recorded a skill header. You still need to assess the publisher and instructions yourself; ownership does not establish safety or guarantee that an agent will follow the instructions correctly.

## What discovery establishes

The plugin reads conda package records in the selected environment and looks for `share/agent-skills/<name>/SKILL.md` in each package's file list. It ignores untracked directories, even if their headers are valid. A pip-only installation does not create the conda ownership record needed for discovery.

For each candidate, the plugin validates the directory name, YAML name and description, and filesystem containment. Duplicate ownership of a skill name in the same environment is an error. See {doc}`../how-to/package-a-skill` for the exact requirements.

The resulting `package` and `version` fields describe the installed package record. The plugin does not verify cryptographic signatures or file hashes, authenticate the publisher, audit supporting scripts, or prove that current files still match their original archive. Companion files are checked for containment, not individually attributed to packages.

## What linking changes

Installation exposes the complete skill directory, including its references and scripts, through a link at a path used by agent clients. The plugin does not execute these files. An agent reading the instructions may later request operations based on them.

Review the instructions and supporting files before linking. Apply your normal package-source policy, inspect changes when updating packages, and use the agent client's own permissions to control what it can read or execute. A source update can change content exposed by an existing link without another `conda skill install` command.

Containment checks prevent a skill directory from redirecting to files outside the permitted filesystem boundaries at discovery time. They do not sandbox later agent actions or protect against concurrent modifications of the source files.

## What status establishes

Status checks the destination filesystem without requiring a source environment. A symlink to a directory containing `SKILL.md` is `linked`; it need not have been created by this plugin or point into a conda environment. Status does not read the header to validate it.

You can therefore inspect links after deleting a source environment, even though discovery is no longer possible. The status table does not establish trust or package ownership.

## Why removal requires the source

The plugin has no persistent record of links it created. To remove a link safely, it rediscovers the selected source skill and checks that the destination symlink resolves to that same source. It can remove a matching link created by another tool, but refuses unrelated entries.

Remove links before uninstalling the source package or deleting its environment. If the source is already gone, automatic removal cannot verify that the link matches it. Inspect the destination and remove the stale symlink manually as described in {doc}`../how-to/troubleshooting`.
