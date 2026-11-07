# Changelog

## Unreleased

- Use an explicit temporary source prefix for skill-forge recordings, avoiding collisions with existing named environments.
- Preserve symlink traversal when locating an unlink target's source environment, and report malformed package records as unverifiable sources with explicit recovery guidance.
- Use the active conda environment in the first-use tutorial, with explicit source selection covered as an advanced option.
- BREAKING: Make `conda skill unlink` destination-based and remove its `-n`/`-p` options. Verify the existing symlink's target against conda package records, return `removed: false` for an absent destination without source lookup, and allow reviewed broken or unverifiable symlinks to be removed with `--force` while preserving file, directory, and redirected-parent protections.
- Make quickstart's default scope follow `--global`, show the current-directory destination, and explain source-selection and unlink requirements in command guidance.
- BREAKING: Rename `conda skill install` to `conda skill link` and `conda skill remove` to `conda skill unlink`, with no aliases for the old subcommands. The native `conda skills` alias remains available. Package installation and removal commands are unchanged.
- Fix secret forwarding to the reusable Anaconda publisher.
- Report the failing stage and exit status during post-upload verification, with escaped package metadata when available.
- Retire the one-off 0.1.0 recovery and diagnostic workflows after verified publication.

## 0.1.0 - 2026-11-07

Initial release.

- Discover agent skills through installed conda package records, with header validation, duplicate-ownership detection, and filesystem containment checks.
- Provide `conda skill list`, `status`, `install`, and `remove`, with source-environment selection and explicit project or home-directory destinations.
- Support the `agents` and `claude` backend paths. Reuse matching links, refuse conflicts, and report linked, broken, and unmanaged filesystem entries.
- Render human-readable output and complete JSON results while keeping skill text literal.
- Add a Sphinx/MyST documentation site, a locally buildable example skill package, and contributor and release-preparation guides.
- Add `conda skill init` to create authoring skeletons safely, and an interactive `quickstart` guide that requires explicit confirmation before writes.
- Accept `conda skills` as a native alias for `conda skill`.
- Select multiple installed skills in quickstart, preview all destinations, and reject conflicts before confirmation without removing unselected links.
- Inspect both supported destinations in the chosen scope with `conda skill status --all`.
- Document conda-pypi installation in the environment owning conda.
- Migrate development and release tooling from Pixi to conda-workspaces, with a root `conda.toml`, generated `conda.lock`, and separate environment installation and task execution.
- Build with Hatchling and hatch-vcs, derive Python package versions from Git, and check release tags against the resolved version and the conda recipe candidate.
- Coordinate PyPI and conda publication with signed build provenance, verified CEP 27 publication evidence, and conda builds from the published source archive's exact digest.
- Use the patched PyPI publishing action v1.14.3 for trusted publishing and attestations.
