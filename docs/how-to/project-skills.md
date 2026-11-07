# Share skills with conda-workspaces

Use conda-workspaces when teammates need the same skill package versions. The manifest declares the packages, and the lockfile records the resolved builds. Each person installs that environment, reviews the skill files, and creates their own project links.

For linking a skill without a shared environment definition, {doc}`use-an-installed-skill` is enough. This guide assumes `conda skill --help` works. See {doc}`installation` for setup.

## Add a skills environment

Install conda-workspaces in the environment that runs conda, usually `base`:

```sh
conda install -n base --override-channels -c conda-forge "conda>=26.9" "conda-workspaces>=0.12"
```

Run the remaining commands from the project root. Create `conda.toml` there, or merge this configuration into the existing manifest without replacing its other dependencies:

```toml
[workspace]
name = "polars-project"
channels = ["https://prefix.dev/skill-forge", "conda-forge"]
platforms = ["linux-64", "osx-arm64", "win-64"]

[feature.skills.dependencies]
agent-skill-polars = "==0.0.8"

[environments]
skills = ["skills"]
```

This pins the skill package, not the Polars library. Adjust the platforms for your team. If your manifest has shared dependencies that you do not want in this environment, use `skills = { features = ["skills"], no-default-feature = true }` instead.

## Lock, install, and review

```sh
conda workspace lock
```

Review the generated `conda.lock`, including package URLs, versions, builds, and hashes. Then install the selection for your current platform:

```sh
conda workspace install --locked -e skills
conda skill list -p .conda/envs/skills
```

The listing should show skill `polars` from package `agent-skill-polars`. Open `.conda/envs/skills/share/agent-skills/polars/SKILL.md` and inspect its supporting files. Decide whether those instructions fit your project and agent permissions before continuing. Package hashes identify files but do not approve their instructions.

The paths above use conda-workspaces' default environment directory. If you customize `workspace.envs-dir`, adjust the source path accordingly. You do not need to activate this environment or install the plugin inside it.

## Create the project link

After reviewing the files:

```sh
conda skill link polars -p .conda/envs/skills
conda skill status
```

This creates `.agents/skills/polars`. Add `--backend claude` to both commands for `.claude/skills/polars`. Consult your agent's documentation for supported paths and reload behavior. The `linked` result reports filesystem status, not confirmation that the agent loaded the skill.

The current directory determines the project destination. `-p` selects only the source environment. Home-directory changes still require explicit `--global`, as described in {doc}`../explanation/agent-discovery`. Windows directory symlinks require Developer Mode or appropriate privileges.

## Share and maintain it

Commit `conda.toml` and the reviewed `conda.lock`, not `.conda/`. Teammates run `conda workspace install --locked -e skills`, review the installed content, and create their links. A tracked symlink does not install its target environment.

Do not regenerate the lockfile during routine setup: that requests a fresh solve. Use {doc}`update-skills` for planned version changes and rollback. Updating a source package changes the content visible through existing links, so unlink it before updating and review the replacement before reconnecting.

Remove the project link before deleting or changing its source:

```sh
conda skill unlink polars
```

Repeat with the backend and scope originally used. Unlinking identifies the source from the destination symlink, so it needs no source override. To stop installing the package, remove its dependency from the manifest, regenerate and review the lockfile, then install the locked environment. If the source has already gone, use {doc}`troubleshooting` to inspect and remove the stale link safely.

See {doc}`../demos` for the recorded workflow and {doc}`../explanation/agent-discovery` for the distinction between skill packages and the libraries your code runs.
