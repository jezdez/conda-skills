# Use an installed skill

Use this guide when a conda environment already contains a skill package and `conda skill --help` works. If you need a complete exercise with a local example package, start with {doc}`../tutorials/first-skill`.

## Find and review it

List skills in the source environment, using its actual name:

```sh
conda skill list -n skill-env
```

Open the reported `SKILL.md` and any supporting files in your editor. Package ownership tells you where the files came from, not whether their instructions are appropriate. The commands below use `review-notes` as an example name; substitute a name from your listing.

## Make it available to your project

Run from the project root:

```sh
conda skill install review-notes -n skill-env
conda skill status
```

This creates `.agents/skills/review-notes` as a directory symlink. It leaves the package files in `skill-env`. The plugin does not launch your agent or change its configuration; check that your agent supports this directory convention.

For Claude's directory convention, specify the backend on both commands:

```sh
conda skill install review-notes -n skill-env --backend claude
conda skill status --backend claude
```

To make the skill available through your home directory, pass `--global` explicitly to `install` and `status`. Use `-p /path/to/environment` instead of `-n skill-env` when selecting a source by path. Source selection and destination scope are independent; see {doc}`../explanation/scope`.

## Remove the project link

```sh
conda skill remove review-notes -n skill-env
```

Use the same backend and `--global` setting you used for installation. Removal deletes only a matching symlink, not the package. If the source environment has been removed or moved, follow {doc}`troubleshooting` to inspect and remove a stale link safely.

See {doc}`../reference/commands` for all options, and {doc}`../demos` for a recording of this sequence.
