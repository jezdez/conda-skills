# Changelog

## Unreleased

The source version is `0.1.0`. No public release has been published.

- Discover agent skills through installed conda package records, with header validation, duplicate-ownership detection, and filesystem containment checks.
- Provide `conda skill list`, `status`, `install`, and `remove`, with source-environment selection and explicit project or home-directory destinations.
- Support the `agents` and `claude` backend paths. Reuse matching links, refuse conflicts, and report linked, broken, and unmanaged filesystem entries.
- Render human-readable output and complete JSON results while keeping skill text literal.
- Add a Sphinx/MyST documentation site, a locally buildable example skill package, and contributor and release-preparation guides.
- Add `conda skill init` to create authoring skeletons safely, and an interactive `quickstart` guide that requires explicit confirmation before writes.
- Document conda-pypi installation in the environment owning conda.
