# Contributing to conda-skills

## Development environment

Work from a local checkout with conda-workspaces. The root `conda.toml` defines the `default`, `py311`, `py314`, `docs`, and `build` environments and their tasks. The resolved dependencies are recorded in `conda.lock`. Install conda from a conda channel, not PyPI.

Bootstrap the tooling, install the locked default environment, and run the full check before changing code:

```sh
conda install -n base --yes --override-channels -c conda-forge 'conda>=26.9' 'conda-workspaces>=0.12'
conda workspace install --locked -e default
conda task run -e default check
```

The `check` task installs the editable plugin in the selected environment and runs pytest, Ruff lint, the formatting check, ty, and zizmor. The tests include real installed-plugin discovery and CLI subprocesses with temporary package records and isolated client homes.

The `default`, `py311`, and `py314` environments combine the `dev` and `test` features. Ruff, ty, prek, and zizmor belong to `dev`, while pytest and coverage belong to `test`. The `docs` and `build` environments contain their own tooling and shared runtime dependencies. Both test and build environments need Hatchling and hatch-vcs for editable installation and release-version tests.

To use the plugin with your usual conda executable, follow `docs/how-to/installation.md`. Those checkout instructions use `conda-pypi` with an explicit target environment, separate from the workspace's check and build environments. Validate installation examples in disposable environments, not a shared base environment.

`--locked` belongs to `conda workspace install`, not `conda task run`. Tasks run named commands from the manifest. To run an arbitrary command in an installed environment, use `conda workspace run -e ENV -- COMMAND`.

## Code changes

Keep registration and parser configuration cheap to import. Put discovery and filesystem behavior in domain modules, and argument dispatch, output, and conda error handling in `cli/`. Use relative imports, modern type annotations, and plain pytest functions. Read `AGENTS.md` for the coding and safety rules.

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

Pytest measures line and branch coverage, including CLI subprocesses. The normal `check` task requires at least 95% combined coverage and writes `coverage.xml` and an HTML report at `htmlcov/index.html`. Generated version metadata is excluded. CI retains a report for each operating system and Python version. For a focused diagnostic run without coverage, use `pytest --no-cov`. Run the complete check before submitting changes.

To install local commit hooks, run `conda task run -e default install-hooks`. Run them explicitly with `conda task run -e default prek`.

The local prek hook runs `check`, including type checking and workflow security, without a second set of tool installations. Run either check alone with `conda task run -e default type-check` or `conda task run -e default check-workflow-security`. Zizmor runs offline and fails on medium-or-higher findings. Lower-severity advice is not blocking, and offline mode does not audit remote action contents. The build environment's `check-workflows` task runs Actionlint for workflow and shell syntax.

The `dev` feature also includes conda-workspaces so the hook can find `conda task` when launched from the workspace environment.

## Documentation changes

The site uses Sphinx, MyST Markdown, `conda-sphinx-theme`, and `sphinx-design`. Keep tutorials, task-oriented guides, reference, and explanations distinct. Use the theme's cards and tabs where they help readers navigate. Ordinary content does not need custom CSS.

```sh
conda workspace install --locked -e docs
conda task run -e docs docs
```

The documentation task checks references and treats warnings as errors (`-W -n`). Review navigation, code blocks, and mobile layout in the rendered pages under `docs/_build/`. Sphinx excludes build output, example sources, and `superpowers` planning directories from page discovery. Pages can still include example sources through literal includes.

Run affected tutorial commands in disposable state: Sphinx does not execute shell examples or check whether an agent can discover skills. The local-build tutorial uses the recipe under `docs/examples/`. Report which operating systems and shell variants you exercised. To update the recordings, follow `demos/README.md`.

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

Python distributions go to `dist/`, and conda artifacts go to `conda-dist/`. Check the built artifacts rather than relying only on editable-install tests. Follow `RELEASING.md` for version checks and release preparation. These commands do not publish packages.

## Review

Explain what changed and why, and report the checks you ran. Use one line per paragraph or bullet in pull request and issue bodies. Note untested platforms and any external prerequisites needed to reproduce a problem. A lockfile covering Linux, macOS ARM64, and Windows does not show that tests ran natively on all three.

Review AI-assisted contributions with the same care as other changes. You remain responsible for their behavior, claims, licensing, and tests. Keep release notes in `CHANGELOG.md` and do not announce an unreleased change as already published.
