# Contributing to conda-skills

## Development environment

Use conda-workspaces from a local checkout. The root `conda.toml` defines the `default`, `py311`, `py314`, `docs`, and `build` environments and their tasks. The generated `conda.lock` records their resolved dependencies. Conda is provisioned from a conda channel, not PyPI.

Bootstrap the tooling, install the locked default environment, and run the full check before changing code:

```sh
conda install -n base --yes --override-channels -c conda-forge 'conda>=26.9' 'conda-workspaces>=0.12'
conda workspace install --locked -e default
conda task run -e default check
```

The `check` task installs the editable plugin in the selected environment and runs pytest, Ruff lint, the formatting check, and ty. The tests include real installed-plugin discovery and CLI subprocesses with temporary package records and isolated client homes.

The `default`, `py311`, and `py314` environments combine the `dev` and `test` features. Ruff, ty, and prek belong to `dev`; pytest and coverage belong to `test`. The `docs` and `build` environments include only their own tooling and shared runtime dependencies. Hatchling and hatch-vcs are included in both test and build environments because editable installation and release-version tests need them too.

For use with your usual conda executable, follow the checkout instructions in `docs/how-to/installation.md`, which use `conda-pypi` and an explicit target environment. The workspace's check and build environments are separate from that installation. Validate installation examples in disposable environments, not a shared base environment.

`--locked` belongs to `conda workspace install`, not `conda task run`. Tasks run named commands from the manifest. To run an arbitrary command in an installed environment, use `conda workspace run -e ENV -- COMMAND`.

## Code changes

Keep registration and parser configuration cheap to import. Domain modules own discovery and filesystem behavior; `cli/` owns argument dispatch, output, and conda error handling. Use relative imports, modern type annotations, and plain pytest functions. Read `AGENTS.md` for the repository's detailed coding and safety rules.

Test changed behavior, particularly filesystem conflicts, containment, malformed package metadata, and JSON output. Tests must leave a contributor's home and existing conda environments untouched. Link operations must preserve existing user files.

Run checks with the oldest and newest supported Python versions as well as the default environment:

```sh
conda workspace install --locked -e default
conda task run -e default check
conda workspace install --locked -e py311
conda task run -e py311 check
conda workspace install --locked -e py314
conda task run -e py314 check
```

Use `conda task run -e default format` to apply the project's formatter after installing the default environment. When changing dependency or workspace metadata, run `conda workspace lock` and include the regenerated `conda.lock`. Do not edit the lockfile by hand.

Pytest measures line and branch coverage, including CLI subprocesses. The normal `check` task requires at least 95% combined coverage and writes `coverage.xml` and an HTML report at `htmlcov/index.html`. Generated version metadata is excluded. CI retains a report for each operating system and Python version. For a focused diagnostic run without coverage, use `pytest --no-cov`; run the complete check before submitting changes.

To install local commit hooks, run `conda task run -e default install-hooks`. Run them explicitly with `conda task run -e default prek`.

## Documentation changes

The site uses Sphinx, MyST Markdown, `conda-sphinx-theme`, and `sphinx-design`. Keep tutorials, task-oriented guides, reference, and explanations distinct. Use the theme's cards and tabs where they help readers navigate; no custom CSS is needed for ordinary content.

```sh
conda workspace install --locked -e docs
conda task run -e docs docs
```

The documentation task treats warnings as errors and checks references (`-W -n`). Review the rendered pages under `docs/_build/` for navigation, readable code blocks, and mobile layout. The configuration excludes build output, example sources, and `superpowers` planning directories from page discovery. Example sources remain available through literal includes.

Execute affected tutorial commands in disposable state. A successful Sphinx build does not execute shell examples or establish agent-client discovery. The first-use tutorial builds the maintained recipe under `docs/examples/`; report which operating systems and shell variants you actually exercised.

Install the build environment with `conda workspace install --locked -e build`, then run `conda task run -e build test-example`. This builds that recipe and checks the install, list, link, status, and remove workflow in a temporary environment and project.

## Packaging changes

```sh
conda workspace install --locked -e build
conda task run -e build build
conda task run -e build check-dist
conda task run -e build test-wheel
conda task run -e build build-conda
conda task run -e build check-workflows
```

Python distributions go to `dist/`; conda artifacts go to `conda-dist/`. Check the built artifacts rather than relying only on editable-install tests. Follow `RELEASING.md` for version checks and release preparation. These commands do not publish packages.

## Review

Describe the behavior changed, the reason, and the checks actually run. Use one line per paragraph or bullet in pull request and issue bodies. Note untested platforms and any external prerequisites needed to reproduce a problem. A lockfile covering Linux, macOS ARM64, and Windows is not evidence of native test execution on all three.

Review AI-assisted contributions with the same care as other changes. You remain responsible for their behavior, claims, licensing, and tests. Keep release notes in `CHANGELOG.md`; do not announce an unreleased change as already published.
