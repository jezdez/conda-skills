# Update, pin, and review skills

A skill link points to the installed directory's current contents. Updating its conda package can change the instructions an agent sees without another `conda skill install`. Remove links before changing the source package, then review the new files before making them available again.

This guide assumes `conda skill --help` works and you already have a skill package installed. Examples use skill `polars` from package `agent-skill-polars`, with `0.0.8` as a known version. Use the package name for conda transactions and the skill name for `conda skill` commands. Other packages may contain several skills with different names.

## Record the current selection

For the workspace in {doc}`project-skills`, run from the project root:

```sh
conda skill list -p .conda/envs/skills
conda list -p .conda/envs/skills agent-skill-polars
conda skill status
```

Record the current package version, build, channel, source directory, and link destinations. Preserve the current `conda.toml` and `conda.lock` together in version control or a separate backup before editing them. If you need a content comparison, save a copy of the installed skill directory outside all client skill directories before replacing it.

For an ordinary named environment, replace `-p .conda/envs/skills` with `-n skill-env`, using your actual environment name. `conda list -n skill-env --explicit` can record the environment's package URLs for recovery; keep exports containing private channel information out of public repositories.

## Disconnect the old content

Stop agent sessions that might use the skill. Removing a link does not erase instructions a running client has already loaded.

```sh
conda skill remove polars -p .conda/envs/skills
conda skill status
```

Use the same source, backend, and destination scope as for installation. For example, append `--backend claude` for `.claude/skills/`, or `--global` for a home link. Repeat this for all skills in the package and all destinations you use. The plugin cannot enumerate links in other projects.

Remove links before uninstalling the source package, even if you intend to replace it immediately. Removal rediscovers the installed skill to verify the destination; it cannot do that after the source disappears or its metadata becomes invalid.

## Update a workspace selection

Edit the dependency in `conda.toml` to the version you have chosen. This example pins the known `0.0.8` release; replace that version with another published version only after assessing the candidate:

```toml
[feature.skills.dependencies]
agent-skill-polars = "==0.0.8"
```

Use the libmamba shell setting described in {doc}`project-skills` for this channel, then generate the candidate lockfile:

```sh
conda workspace lock
git diff -- conda.toml conda.lock
```

The Git command is for projects under version control; otherwise compare with your saved files. `conda workspace lock` runs a fresh solve for all declared environments and platforms, even when the existing lockfile is current. It can change unrelated packages within their constraints. Review the whole diff, not only the skill package entry. A version pin can still allow a different build of that version or changes to its dependencies.

You do not need an update flag on `lock`. Running it again with an unchanged exact version pin does not request a newer skill version. To update the skill version, change that pin first. A range such as `>=0.0.8,<0.1` permits a fresh solve to select a newer matching version; it is not a commitment to `0.0.8`.

Once you accept the proposed package selection:

```sh
conda workspace install --locked -e skills
conda skill list -p .conda/envs/skills
```

The install applies the locked environment on the current platform. Packages outside that locked selection can be removed, so do not use the managed prefix to store ad hoc installations. If `--locked` reports a mismatch, reconcile the manifest and lockfile rather than bypassing the check with `--frozen`.

This separates resolving packages from exposing their instructions. The package selection review happens before installation; the installed-file review below happens before relinking.

## Update an ordinary conda environment

For a source environment named `skill-env`, first remove its link from the project root:

```sh
conda skill remove polars -n skill-env
```

Choose one of the following package operations. To request a particular version, including a downgrade to the known `0.0.8` version:

```sh
conda install -n skill-env --solver libmamba --override-channels -c https://prefix.dev/skill-forge -c conda-forge "agent-skill-polars==0.0.8"
```

To ask conda for a newer version allowed by the environment's constraints:

```sh
conda update -n skill-env --solver libmamba --override-channels -c https://prefix.dev/skill-forge -c conda-forge agent-skill-polars
```

Review conda's transaction plan before accepting it. Updating the package can also change dependencies, and the latest published version may be incompatible with the rest of the environment. Neither command updates a workspace manifest or lockfile; use the workspace workflow for a workspace-managed prefix.

An explicit install request selects a version for that transaction. For a persistent pin in an ordinary environment, add this line to its `conda-meta/pinned` file, preserving any existing pins:

```text
agent-skill-polars ==0.0.8
```

Find the environment's actual prefix with `conda env list`. Future conda solves honor this pin unless you change it or explicitly bypass pins. Change the pin when deliberately changing versions. It does not constrain a different environment or make the installed directory immutable.

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

## Choose the right pin

| Record | What it fixes | What it leaves open |
| --- | --- | --- |
| Exact version in `conda.toml` or `conda-meta/pinned` | The allowed version of one package | Builds, dependencies, local file changes, and whether the instructions are appropriate |
| Version plus build and channel constraints | A narrower package selection | Dependency changes and content review |
| Reviewed `conda.lock` | Resolved package URLs and hashes for the recorded environments and platforms | Publisher approval, local modifications, client behavior, and future artifact availability |
| Recipe source URL plus checksum | The source archive a package build is meant to consume | The rest of the recipe, build dependencies, patches, and final package identity |

If you maintain a skill package, review the entire recipe and every source it uses. Pin immutable source revisions or archive URLs and record their checksums. A checksum for `SKILL.md` alone does not cover companion files or build scripts; a source archive checksum does not identify the resulting conda package. Keep the recipe changes and the consumer lockfile changes reviewable in their respective repositories.

The plugin does not check these pins or hashes itself. Conda and conda-workspaces handle package selection and installation; `conda-skills` validates discovery metadata and filesystem containment. None of these records automatically approves instructions for an agent. See {doc}`../explanation/ownership-and-trust`.

## Roll back a rejected update

If the new content is unacceptable, leave it unlinked. If you already reconnected it, stop affected sessions and remove the links before changing packages again.

For a workspace, restore the previously accepted `conda.toml` and `conda.lock` together, preserving unrelated work, then run:

```sh
conda workspace install --locked -e skills
conda skill list -p .conda/envs/skills
```

Do not run `conda workspace lock` during this rollback: that would produce a new solve instead of restoring the saved selection. The old package artifacts must still be available from their URLs or an appropriate package cache. Restoring the lockfile alone does not restore files in the installed environment.

For an ordinary environment, restore any persistent pin and use `conda install` with the previous version and, where needed, its recorded build and channel. A version-only downgrade may choose different dependencies from the original environment; it is less precise than restoring a complete locked selection.

Review the restored directory before relinking it. Package rollback cannot undo commands an agent already ran, restore changed project data, or clear instructions cached by a client. Handle those separately. If the update left a broken link and normal removal fails, use the inspection procedure in {doc}`troubleshooting`.
