# Changelog

## Unreleased

## 0.2.2 - 2026-11-07

- Require the full reusable test workflow to succeed before release builds, signing, or publication. Tag pushes no longer start an independent test run that races with publication.
- Make release-download path assertions portable across Windows and POSIX systems.
- Resolve conda recipe versions directly with the Hatch CLI without a separately maintained default. Replace the release-check script with workflow version comparisons and a manual dated-notes checklist.
- Simplify conda publication to build and test, attest, then upload. Remove post-upload polling, repeated inspections, and fresh channel installations while retaining verified signatures, protected uploads, tag identity checks, and overwrite protection.
- Correct the normalized PyPI source URL used for conda release builds.
- Retry transient source-download failures with bounded curl retries and verify the archive against the recorded SHA-256 without querying PyPI metadata.

## 0.2.1 - Cancelled

The tagged release was cancelled before publication to PyPI or Anaconda.org because release builds could start before the tag's full test matrix finished. The public tag and attested draft artifacts are retained unchanged. Version 0.2.2 includes the intended changes with corrected test ordering.

## 0.2.0 - 2026-11-07

- Add `inspect` for packaged skill metadata, file trees, and safe text previews, and `open` for opening the skill directory in the system file manager.
- Highlight inspected source in terminals while preserving Markdown syntax and link destinations. Piped output is plain, and JSON retains the original decoded text.
- Bound skill header and preview reads to 1 MiB, reject special files, and recheck containment before reading.
- Add an inspection demo with a packaged reference file and a beginner overview of skills for conda users.
- Use an explicit temporary source prefix for skill-forge recordings, avoiding collisions with existing named environments.
- Preserve symlink traversal when locating an unlink target's source environment, and report malformed package records as unverifiable sources with explicit recovery guidance.
- Use the active conda environment in the first-use tutorial, with explicit source selection covered as an advanced option.
- BREAKING: Unlinking no longer takes `-n`/`-p`. It checks the destination link against the target environment's package records, independently of the active environment. An absent link returns `removed: false`. Use `--force` only after inspecting broken or unverifiable links. Files, directories, and redirected parents remain protected.
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
