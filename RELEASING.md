# Release preparation

The project is unreleased. Python package versions are derived from Git by Hatchling and hatch-vcs; the conda recipe's current candidate is `0.1.0`. No public package is available, and no public documentation URL is configured. The checks below do not publish anything.

## Prepare the candidate

Review the changes and confirm that `CHANGELOG.md` describes them under Unreleased. Set `context.version` in `recipe/recipe.yaml` to the intended bare release tag. On a clean tagged checkout, hatch-vcs derives the Python package version from that tag. Other checkouts can have development versions containing a commit identifier and a dirty-tree date.

`pyproject.toml` declares a dynamic version and a `0.1.0` fallback for development builds without usable version metadata. The fallback does not establish a release, and an untagged Git checkout can still resolve to a different development version. Do not edit the generated `src/conda_skill/_version.py` file.

Local conda builds copy the checkout without relying on Git metadata. The recipe sets `SETUPTOOLS_SCM_PRETEND_VERSION` to `context.version` for those development builds. Release builds instead use the exact published PyPI source archive and its recorded SHA-256, without overriding the version stored in that archive. Do not use a version override to bypass the release check.

Confirm that the README and installation guide describe the candidate accurately. Do not replace development installation instructions with a public channel or PyPI command until the corresponding release is actually available. The separately versioned example package under `docs/examples/` is a tutorial fixture, not the plugin distribution.

## Validate

Bootstrap the tooling as described in `CONTRIBUTING.md`, then run from the checkout root. Install each environment from `conda.lock` before running its tasks:

```sh
conda workspace install --locked -e default
conda task run -e default check
conda workspace install --locked -e py311
conda task run -e py311 check
conda workspace install --locked -e py314
conda task run -e py314 check
conda workspace install --locked -e docs
conda task run -e docs docs
conda workspace install --locked -e build
conda task run -e build build
conda task run -e build check-dist
conda task run -e build test-wheel
conda task run -e build build-conda
conda task run -e build test-example
conda task run -e build check-release 0.1.0
```

`check-release VERSION` compares the bare version argument against Hatchling's resolved package version and the recipe candidate, and requires a dated changelog heading in the form `## VERSION - YYYY-MM-DD`. Use `0.1.0` for the current candidate, not `v0.1.0`. Run the final check on the clean release-tag checkout after tagging has been separately authorized. Before that, a development-version mismatch is expected. This task does not create a tag, upload artifacts, or publish a release.

The current changelog has only an Unreleased section, so it cannot pass that final check even if the versions agree. Once a release is authorized and its date selected, add the dated candidate notes before tagging. Those notes do not establish that publication succeeded.

Review wheel and source distribution artifacts under `dist/` and conda artifacts under `conda-dist/`. `check-dist` validates Python distribution metadata, `test-wheel` checks the installed wheel, and `build-conda` builds and tests the conda recipe. None of these replaces the source test suite or the first-use tutorial workflow.

Run the tutorial's local example build, install, link, status, and removal sequence in disposable state. Review the rendered documentation after the strict build. Record native platform results separately from lockfile support; a macOS or Linux run does not test Windows symlink behavior.

## One-time publisher setup

The public repository is [jezdez/conda-skills](https://github.com/jezdez/conda-skills). Its `pypi` and `anaconda` environments require approval from `jezdez` and restrict deployments to tags matching `*.*.*`; the workflows further require canonical numeric versions. Self-approval is allowed, following the other personally maintained plugins. Immutable GitHub releases are enabled.

Complete or verify these integrations before pushing a release tag:

- Register a PyPI trusted publisher for project `conda-skills`, owner `jezdez`, repository `conda-skills`, workflow `release.yml`, and environment `pypi`. Use a pending publisher for the first release. No PyPI API token belongs in repository secrets.
- Store a channel-scoped upload token as `ANACONDA_API_KEY` in the `anaconda` environment. It must authorize publishing to the `jezdez` owner. Do not expose it to pull-request jobs.
- Confirm that GitHub Actions has permission to create draft releases. The workflows grant write permissions only to the jobs that need them.
- Verify that the environment restrictions and immutable-release setting remain enabled. A named environment alone does not provide approval rules.

An administrator must perform these setup steps separately from local validation. Documentation is built by the separate Docs workflow and deployed from `main` to [GitHub Pages](https://jezdez.github.io/conda-skills/); package publication is not required to update the site.

This public repository is eligible for GitHub artifact attestations. The workflows verify bundles with `gh attestation verify` and never skip signing on failure. Public Sigstore and PyPI attestations disclose signing identities and artifact metadata through public transparency records; they are not private or encrypted evidence.

## Tag-driven publication

The intended package destinations are the `jezdez` channel's `main` label on anaconda.org and PyPI. Neither currently contains conda-skills. The installation guide documents both routes conditionally; it does not establish that publication is configured or complete.

The process combines [conda-advise's release sequence](https://github.com/jezdez/conda-advise/blob/main/.github/workflows/release.yml) with [conda-sigstore's attestation steps](https://github.com/conda-incubator/conda-sigstore/blob/main/.github/workflows/conda.yml). Push an authorized annotated tag such as `0.1.0` on a commit reachable from `main`. Do not prefix the tag with `v` or use leading zeroes. Review native CI results before tagging. The release workflow reruns Python 3.11/3.14 tests and the strict docs build on Linux; it does not query historical CI runs or repeat the complete platform matrix.

`release.yml` checks the tag, resolved Python version, recipe candidate, and dated release notes. It reruns tests and the strict docs build, then builds the wheel and source archive once. Twine checks distribution metadata; a short shell check requires exactly the expected wheel and source filenames. The workflow tests the installed wheel and records the source archive digest with `sha256sum`. A separate job records GitHub build provenance for those artifacts before creating the draft release. PyPI publication uses OIDC and explicitly enables PEP 740 publication attestations.

After PyPI succeeds, `release.yml` calls `publish-conda.yml` with the version and source digest. It sets `CONDA_SKILLS_SOURCE_SHA256`, which selects the published-source branch of `recipe/recipe.yaml`. Rattler-build downloads the archive from the recipe's PyPI URL, verifies its SHA-256, and builds/tests the noarch package once. Local builds without this variable continue to use the checkout. The same stored conda artifact is used for signing, verification, and upload; there is no independent tag-triggered publisher.

The conda artifact receives two attestations: SLSA build provenance and a CEP 27 publication statement naming `https://conda.anaconda.org/jezdez`. Before upload, the workflow verifies the publication bundle against the exact package digest, repository, reusable signer workflow, source commit, tag, and GitHub OIDC issuer, then checks the claimed target channel. It retains the verified `.sigstore.json` bundle as a workflow artifact; the bundle is not uploaded to Anaconda.org.

The upload job still refuses existing or unverifiable Anaconda.org releases, disables uploader configuration and force overrides, and checks the published distribution and channel index against the local artifact. It then installs that exact package in a fresh environment and runs the installed-plugin smoke test. Only after conda verification succeeds does the parent workflow publish the GitHub draft.

Attestations identify who built or published particular bytes. They do not establish package safety, authorize a signer for a channel, produce an SBOM, or enable automatic verification in users' conda installations.

## Verify and recover

Download the original artifact and its retained bundle, then verify it with a current GitHub CLI. For conda publication evidence, substitute the actual filename, version, and release commit:

```sh
gh attestation verify conda-skills-VERSION-BUILD.conda \
  --repo jezdez/conda-skills \
  --bundle conda-skills-VERSION-BUILD.conda.sigstore.json \
  --signer-workflow jezdez/conda-skills/.github/workflows/publish-conda.yml \
  --source-digest COMMIT_SHA \
  --source-ref refs/tags/VERSION \
  --cert-oidc-issuer https://token.actions.githubusercontent.com \
  --predicate-type https://schemas.conda.org/attestations-publish-1.schema.json \
  --deny-self-hosted-runners --format json
```

Inspect the verified statement's `predicate.targetChannel` and require `https://conda.anaconda.org/jezdez`. To verify build provenance, omit `--bundle` and `--predicate-type`; GitHub then retrieves the SLSA attestation for the artifact. Use `release.yml` as the signer workflow for the wheel and source archive. PyPI's provenance endpoint exposes the separate PEP 740 publication evidence for each Python distribution. Retain artifacts and bundles together for verification after workflow artifacts expire.

Publication across services is not atomic. A PyPI success followed by a conda failure leaves a public Python package and a draft GitHub release. Inspect the completed jobs and both indexes before retrying:

- If a build or signing step failed before any upload, correct the failure and use the original release commit and artifacts.
- If PyPI partially uploaded, compare the existing files and digests before completing it. A generic `skip-existing` setting would not verify their bytes and is deliberately absent.
- If the conda upload succeeded but verification failed, inspect its filename, build, digest, size, and channel label. The normal uploader refuses an existing release; do not rerun it blindly or add force flags.
- If only GitHub finalization failed, confirm both package publications and their evidence, then finalize the existing draft without rebuilding or re-uploading packages.

Never move a released tag or replace a published artifact. Recovery actions that publish or change a release require explicit authorization.

Pushing a tag is a publication action and requires explicit authorization. Merely adding these workflow files does not configure the external publishers. Do not upload artifacts or announce a public release merely because local preparation checks passed.

Once publication has been authorized and confirmed at the selected destinations, confirm the actual version and date in `CHANGELOG.md`, retain an Unreleased section for later work, and update installation links to the verified locations. Keep validation evidence separate from evidence of publication.
