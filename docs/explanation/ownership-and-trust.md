# Package ownership and trust

Package ownership tells you which installed conda package recorded a skill header. It does not tell you whether the instructions are safe, the publisher is trustworthy, or an agent will follow them correctly.

## What discovery establishes

The plugin reads installed conda package records in the selected environment. A candidate must have `share/agent-skills/<name>/SKILL.md` in a package's file list. Untracked directories are ignored, even when their headers are otherwise valid. Packages installed only through pip do not establish this conda ownership record.

For each candidate, the plugin validates the directory name, YAML name and description, and filesystem containment. Duplicate ownership of a skill name in the same environment is an error. See {doc}`../how-to/package-a-skill` for the exact requirements.

The resulting `package` and `version` fields describe the installed package record. The plugin does not verify cryptographic signatures or file hashes, authenticate the publisher, audit supporting scripts, or prove that current files still match their original archive. Companion files are checked for containment, not individually attributed to packages.

## What linking changes

Installation links the complete skill directory at a path used by agent clients, including any references and scripts supplied with the skill. The plugin does not execute these files, but an agent reading the instructions may later request operations based on them.

Review the instructions and supporting files before linking. Apply your normal package-source policy, inspect changes when updating packages, and use the agent client's own permissions to control what it can read or execute. A source update can change content exposed by an existing link without another `conda skill install` command.

Containment checks prevent a skill directory from redirecting to files outside the permitted filesystem boundaries at discovery time. They do not sandbox later agent actions or protect against concurrent modifications of the source files.

## What status establishes

Status checks the destination filesystem without requiring a source environment. A symlink to a directory containing `SKILL.md` is `linked`; it need not have been created by this plugin or point into a conda environment. Status does not read the header to validate it.

You can inspect links even after deleting a source environment, when discovery is no longer possible. The status table does not establish whether skills are trusted or package-owned.

## Why removal requires the source

The plugin has no persistent record of links it created. To remove a link safely, it rediscovers the selected source skill and checks that the destination symlink resolves to that same source. It can remove a matching link created by another tool, but refuses unrelated entries.

Remove links before uninstalling the source package or deleting its environment. If the source is already gone, automatic removal cannot verify that the link matches it. Inspect the destination and remove the stale symlink manually as described in {doc}`../how-to/troubleshooting`.
