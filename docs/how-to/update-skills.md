# Update or roll back a skill

If you are getting started, follow {doc}`../tutorials/skill-forge` first. You do not need pins or lockfiles to try a skill.

A skill link points to the installed directory's current contents. Updating its conda package can change the instructions an agent sees without another `conda skill install`. Remove links before changing the source package, then review the new files before making them available again.

This guide assumes `conda skill --help` works and you have a skill package installed. Examples use skill `polars` from package `agent-skill-polars`, with `0.0.8` as a known version. Use the package name for conda transactions and the skill name for `conda skill` commands. Other packages may contain several skills with different names.

## Record the current selection

For the workspace in {doc}`project-skills`, run from the project root:

```sh
conda skill list -p .conda/envs/skills
conda list -p .conda/envs/skills agent-skill-polars
conda skill status
```

Record the current package version, build, channel, source directory, and link destinations. Preserve the current `conda.toml` and `conda.lock` together in version control or a separate backup before editing them. If you need a content comparison, save a copy of the installed skill directory outside all client skill directories before replacing it.

For an ordinary named environment, replace `-p .conda/envs/skills` with `-n skill-env`, using your actual environment name. `conda list -n skill-env --explicit` can record the environment's package URLs for recovery. Keep exports containing private channel information out of public repositories.

## Disconnect the old content

Stop agent sessions that might use the skill. Removing a link does not erase instructions a running client has already loaded.

```sh
conda skill remove polars -p .conda/envs/skills
conda skill status
```

Use the same source, backend, and destination scope as for installation. For example, append `--backend claude` for `.claude/skills/`, or `--global` for a home link. Repeat this for all skills in the package and all destinations you use. The plugin cannot enumerate links in other projects.

Remove links before uninstalling the source package, even if you intend to replace it immediately. Removal rediscovers the installed skill to verify the destination, which it cannot do after the source disappears or its metadata becomes invalid.

## Update a workspace selection

Edit the dependency in `conda.toml` to the version you have chosen. This example pins the known `0.0.8` release. Replace that version with another published version only after assessing the candidate:

```toml
[feature.skills.dependencies]
agent-skill-polars = "==0.0.8"
```

Generate the candidate lockfile:

```sh
conda workspace lock
git diff -- conda.toml conda.lock
```

The Git command is for projects under version control. Otherwise, compare with your saved files.

`conda workspace lock` runs a fresh solve for all declared environments and platforms, even when the existing lockfile is current. It can change unrelated packages within their constraints. Review the whole diff, not only the skill package entry. A version pin can still allow a different build of that version or changes to its dependencies.

`lock` needs no update flag. To request a newer skill version, change the exact version pin before running it again. A range such as `>=0.0.8,<0.1` permits a fresh solve to select a newer matching version and does not pin `0.0.8`.

Once you accept the proposed package selection:

```sh
conda workspace install --locked -e skills
conda skill list -p .conda/envs/skills
```

The install applies the locked environment on the current platform. Packages outside that locked selection can be removed, so do not use the managed prefix to store ad hoc installations. If `--locked` reports a mismatch, reconcile the manifest and lockfile rather than bypassing the check with `--frozen`.

Review the package selection before installation and the installed files before relinking.

## Update an ordinary conda environment

For a source environment named `skill-env`, first remove its link from the project root:

```sh
conda skill remove polars -n skill-env
```

To request a particular version, including a downgrade to the known `0.0.8` version:

```sh
conda install -n skill-env --override-channels -c https://prefix.dev/skill-forge -c conda-forge "agent-skill-polars==0.0.8"
```

To ask conda for a newer version allowed by the environment's constraints:

```sh
conda update -n skill-env --override-channels -c https://prefix.dev/skill-forge -c conda-forge agent-skill-polars
```

Review conda's transaction plan before accepting it. Updating the package can also change dependencies, and the latest published version may be incompatible with the rest of the environment. Neither command updates a workspace manifest or lockfile, so use the workspace workflow for a workspace-managed prefix.

An explicit install request selects a version for that transaction. For a persistent pin in an ordinary environment, add this line to its `conda-meta/pinned` file, preserving any existing pins:

```text
agent-skill-polars ==0.0.8
```

Find the environment's actual prefix with `conda env list`. Future conda solves honor this pin unless you change it or explicitly bypass pins. Change it when changing versions. The pin does not constrain a different environment or make the installed directory immutable.

## Review the replacement and reconnect

List the skills again to confirm their names and installed package versions. Open the reported source directory in your editor and compare it with the saved copy if available.

- Read the complete `SKILL.md`, including changes to when the skill is selected and what it tells the agent to do.
- Inspect all companion files, including added files and scripts. A harmless-looking header does not describe everything exposed by the directory link.
- Review new commands, network endpoints, credential requests, and package-install instructions. Check whether they fit your project's permissions and data policy.
- Read the package's dependencies and constraints, and check that its guidance fits the library versions and tools your project actually runs.

For a workspace source, reconnect only after accepting those changes:

```sh
conda skill install polars -p .conda/envs/skills
conda skill status
```

For an ordinary environment, use `-n skill-env`. Restore any backend and home-scope options you intentionally used. Reload or restart the client according to its documentation and check its own skill view where available. `linked` is a filesystem result, not evidence that the client loaded the new version.

For the distinction between version pins, lockfile hashes, and source checksums, see {doc}`../explanation/skill-safety`. Package authors should also follow {doc}`package-a-skill` when changing recipe sources.

## Roll back a rejected update

If the new content is unacceptable, leave it unlinked. If you already reconnected it, stop affected sessions and remove the links before changing packages again.

For a workspace, restore the previously accepted `conda.toml` and `conda.lock` together, preserving unrelated work, then run:

```sh
conda workspace install --locked -e skills
conda skill list -p .conda/envs/skills
```

Do not run `conda workspace lock` during this rollback: that would produce a new solve instead of restoring the saved selection. The old package artifacts must still be available from their URLs or an appropriate package cache. Restoring the lockfile alone does not restore files in the installed environment.

For an ordinary environment, restore any persistent pin and use `conda install` with the previous version and, where needed, its recorded build and channel. A version-only downgrade may choose different dependencies from the original environment, making it less precise than restoring a complete locked selection.

Review the restored directory before relinking it. Package rollback cannot undo commands an agent already ran, restore changed project data, or clear instructions cached by a client. Handle those separately. If the update left a broken link and normal removal fails, use the inspection procedure in {doc}`troubleshooting`.
