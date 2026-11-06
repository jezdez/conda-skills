# Release preparation

The project is unreleased. Its version is `0.1.0` in `pyproject.toml`. No public package is available, and no public documentation URL is configured. The checks below do not publish anything.

## Prepare the candidate

Review the changes and confirm that `CHANGELOG.md` describes them under Unreleased. Keep the versions in `pyproject.toml` and the plugin's conda recipe in sync. A Git tag does not update either version automatically.

Confirm that the README and installation guide describe the candidate accurately. Do not replace development installation instructions with a public channel or PyPI command until the corresponding release is actually available. The separately versioned example package under `docs/examples/` is a tutorial fixture, not the plugin distribution.

## Validate

From the checkout root, run:

```sh
pixi run --locked check
pixi run --locked -e py311 check
pixi run --locked -e py314 check
pixi run --locked -e docs docs
pixi run --locked -e build build
pixi run --locked -e build check-dist
pixi run --locked -e build test-wheel
pixi run --locked -e build build-conda
pixi run --locked -e build test-example
pixi run --locked -e build check-release 0.1.0
```

`check-release VERSION` compares the bare version argument against the declared metadata and requires a dated changelog heading in the form `## VERSION - YYYY-MM-DD`. Use `0.1.0` for the current candidate, not `v0.1.0`. When preparing a later candidate, update the source metadata first and pass its exact version. This task does not create a tag, upload artifacts, or publish a release.

The current changelog has only an Unreleased section, so it fails that final check. Once a release is authorized and its date selected, add the dated candidate notes and rerun the check. Those notes do not establish that publication succeeded.

Review wheel and source distribution artifacts under `dist/` and conda artifacts under `conda-dist/`. `check-dist` validates Python distribution metadata, `test-wheel` checks the installed wheel, and `build-conda` builds and tests the conda recipe. None of these replaces the source test suite or the first-use tutorial workflow.

Run the tutorial's local example build, install, link, status, and removal sequence in disposable state. Review the rendered documentation after the strict build. Record native platform results separately from lockfile support; a macOS or Linux run does not test Windows symlink behavior.

## One-time publisher setup

After creating the hosted repository, configure these integrations before pushing a release tag:

- Create a GitHub environment named `pypi`, with required reviewers and tag deployment restrictions. Register a PyPI trusted publisher for project `conda-skills`, the actual repository owner/name, workflow `release.yml`, and environment `pypi`. A pending publisher can be used for the first release. No PyPI API token belongs in repository secrets.
- Create a GitHub environment named `anaconda`, with required reviewers and tag deployment restrictions. Store the channel-scoped upload token as its `ANACONDA_API_KEY` secret. It must authorize publishing to the `jezdez` owner. Do not expose it to pull-request jobs.
- Confirm that GitHub Actions has permission to create draft releases. The workflows grant write permissions only to the jobs that need them.

An administrator must perform these setup steps separately from local validation. Repository and documentation hosting still need to be selected and configured.

## Tag-driven publication

The intended package destinations are the `jezdez` channel's `main` label on anaconda.org and PyPI. Neither currently contains conda-skills. The installation guide documents both routes conditionally; it does not establish that publication is configured or complete.

The process follows [conda-cli-mcp](https://github.com/jezdez/conda-cli-mcp/tree/main/.github/workflows). Pushing an authorized stable numeric tag such as `0.1.0` triggers two workflows. Do not prefix the tag with `v`. Both check the exact tag and static version metadata; the Python workflow also runs the test endpoints and strict documentation build.

`release.yml` builds and checks the wheel and source distribution once, tests the installed wheel, and stores those exact artifacts. It creates a draft GitHub release, publishes to PyPI through OIDC after environment approval, then publishes the draft. It does not rebuild between validation and upload.

`publish-conda.yml` builds and tests the noarch package, validates package metadata, and refuses an existing or unverifiable anaconda.org release. After environment approval it uses `pixi upload --no-config anaconda --owner jezdez --channel main`, then verifies indexed metadata and checksums. Its manual trigger accepts an existing stable tag, for completing an unpublished conda release without creating a new source tag.

The workflows are independent: a successful PyPI upload does not prove that the conda upload succeeded. Check both before updating installation claims. If PyPI publication fails, the GitHub release stays a draft. If an upload succeeds but a later verification step fails, inspect the destination before retrying; do not overwrite a released artifact or move its tag.

Pushing a tag is a publication action and requires explicit authorization. Merely adding these workflow files does not configure the external publishers. Do not upload artifacts or announce a public release merely because local preparation checks passed.

Once publication has been authorized and confirmed at the selected destinations, confirm the actual version and date in `CHANGELOG.md`, retain an Unreleased section for later work, and update installation links to the verified locations. Keep validation evidence separate from evidence of publication.
