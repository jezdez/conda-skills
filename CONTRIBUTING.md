# Contributing to conda-skills

## Development environment

Use [Pixi](https://pixi.sh) from a local checkout. The environments and tasks are defined in `pixi.toml`; `pixi.lock` records their dependencies. Conda is provisioned from a conda channel, not PyPI.

Run the full default check before changing code:

```sh
pixi run --locked check
```

This installs the editable plugin in the selected environment and runs pytest, Ruff lint, the formatting check, and ty. The tests include real installed-plugin discovery and CLI subprocesses with temporary package records and isolated client homes.

For use with your usual conda executable, follow the checkout instructions in `docs/how-to/installation.md`, which use `conda-pypi` and an explicit target environment. Pixi's check and build environments are separate from that installation. Validate installation examples in disposable environments, not a shared base environment.

## Code changes

Keep registration and parser configuration cheap to import. Domain modules own discovery and filesystem behavior; `cli/` owns argument dispatch, output, and conda error handling. Use relative imports, modern type annotations, and plain pytest functions. Read `AGENTS.md` for the repository's detailed coding and safety rules.

Test changed behavior, particularly filesystem conflicts, containment, malformed package metadata, and JSON output. Tests must leave a contributor's home and existing conda environments untouched. Link operations must preserve existing user files.

Run checks with the oldest and newest supported Python versions as well as the default environment:

```sh
pixi run --locked check
pixi run --locked -e py311 check
pixi run --locked -e py314 check
```

Use `pixi run --locked format` to apply the project's formatter. When changing dependency or workspace metadata, run `pixi lock` and include the regenerated lockfile. Do not edit the lockfile by hand.

To install local commit hooks, run `pixi run --locked install-hooks`. Run them explicitly with `pixi run --locked prek`.

## Documentation changes

The site uses Sphinx, MyST Markdown, `conda-sphinx-theme`, and `sphinx-design`. Keep tutorials, task-oriented guides, reference, and explanations distinct. Use the theme's cards and tabs where they help readers navigate; no custom CSS is needed for ordinary content.

```sh
pixi run --locked -e docs docs
```

The documentation task treats warnings as errors and checks references (`-W -n`). Review the rendered pages under `docs/_build/` for navigation, readable code blocks, and mobile layout. The configuration excludes build output, example sources, and `superpowers` planning directories from page discovery. Example sources remain available through literal includes.

Execute affected tutorial commands in disposable state. A successful Sphinx build does not execute shell examples or establish agent-client discovery. The first-use tutorial builds the maintained recipe under `docs/examples/`; report which operating systems and shell variants you actually exercised.

`pixi run --locked -e build test-example` builds that recipe and checks the install, list, link, status, and remove workflow in a temporary environment and project.

## Packaging changes

```sh
pixi run --locked -e build build
pixi run --locked -e build check-dist
pixi run --locked -e build test-wheel
pixi run --locked -e build build-conda
pixi run --locked -e build check-workflows
```

Python distributions go to `dist/`; conda artifacts go to `conda-dist/`. Check the built artifacts rather than relying only on editable-install tests. Follow `RELEASING.md` for version checks and release preparation. These commands do not publish packages.

## Review

Describe the behavior changed, the reason, and the checks actually run. Use one line per paragraph or bullet in pull request and issue bodies. Note untested platforms and any external prerequisites needed to reproduce a problem. A lockfile covering Linux, macOS ARM64, and Windows is not evidence of native test execution on all three.

Review AI-assisted contributions with the same care as other changes. You remain responsible for their behavior, claims, licensing, and tests. Keep release notes in `CHANGELOG.md`; do not announce an unreleased change as already published.
