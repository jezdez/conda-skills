# Changelog

## Unreleased

- Coordinate PyPI and conda publication with signed build provenance, verified CEP 27 publication evidence, and conda builds from the published source archive's exact digest.

The conda recipe's current candidate is `0.1.0`. Python package versions are derived from Git. No public release has been published.

- Discover agent skills through installed conda package records, with header validation, duplicate-ownership detection, and filesystem containment checks.
- Provide `conda skill list`, `status`, `install`, and `remove`, with source-environment selection and explicit project or home-directory destinations.
- Support the `agents` and `claude` backend paths. Reuse matching links, refuse conflicts, and report linked, broken, and unmanaged filesystem entries.
- Render human-readable output and complete JSON results while keeping skill text literal.
- Add a Sphinx/MyST documentation site, a locally buildable example skill package, and contributor and release-preparation guides.
- Add `conda skill init` to create authoring skeletons safely, and an interactive `quickstart` guide that requires explicit confirmation before writes.
- Document conda-pypi installation in the environment owning conda.
- Migrate development and release tooling from Pixi to conda-workspaces, with a root `conda.toml`, generated `conda.lock`, and separate environment installation and task execution.
- Build with Hatchling and hatch-vcs, derive Python package versions from Git, and check release tags against the resolved version and the conda recipe candidate.
