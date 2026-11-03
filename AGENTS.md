# conda-skills coding guidelines

## Project structure

- The distribution and conda entry-point name are `conda-skills`. The Python
  package is `conda_skill`, and the command is `conda skill`.
- `src/conda_skill/plugin.py` owns registration and parser configuration for
  `list`, `status`, `install`, and `remove`. Keep registration cheap to import.
- `cli.py` owns command dispatch, conda error handling, and output.
- `skills.py` owns the `Skill` model, single-directory loading and validation,
  and discovery through installed conda package records.
- `links.py` owns backend destinations, link installation and removal, and
  filesystem status. Status includes unmanaged and broken entries; it must not
  require a valid source environment or claim package ownership.
- Tests mirror these topics: `test_plugin.py`, `test_cli.py`, `test_skills.py`,
  and `test_links.py`. Shared fixtures belong in `tests/conftest.py`.

## Imports and dependencies

- Use relative imports inside the package. Absolute `conda_skill.*` imports
  belong in tests and installed entry points.
- Imports belong at module scope. Reserve lazy imports for the plugin callbacks
  that protect conda startup, or a demonstrated optional-dependency boundary.
  Use `TYPE_CHECKING` for annotation-only imports.
- Rich is a required dependency. Import its output classes at module scope in
  `cli.py`; do not use optional imports, fallbacks, or imports inside rendering.
- Keep `__init__.py` free of implementation imports. Loading the plugin and
  configuring its parser must not load CLI, discovery, or link implementations.
- Prefer stdlib, conda APIs, and existing dependencies. Do not add a framework
  or another parser for behavior an existing library handles.
- Declare minimum runtime versions in `pyproject.toml`. Provision dependencies
  through `pixi.toml`; conda itself comes from a conda channel, not PyPI.

## Code structure

- Apply Ponytail Ultra: choose the smallest complete change and question
  additions that have no current use. Split by responsibility, not line count.
- Put behavior on an existing model when it owns the data. `Skill.from_directory`
  loads and validates one candidate; `discover` selects package-owned candidates
  and checks duplicate ownership.
- Before adding a helper, check whether conda or an existing dependency already
  provides it, then whether an existing model owns it. Keep short one-use glue
  inline. Reusable module functions need a clear responsibility and docstring.
- Keep argparse, Rich, printing, and exit-status decisions out of domain modules.
- Do not add section-divider comments to organize large files. Use topic-specific
  modules and descriptive names.
- Add concise docstrings for functions and classes. Explain purpose, important
  constraints, return values, and failure behavior without narrating the code.

## Typing and formatting

- Use `from __future__ import annotations` and modern annotations such as
  `str | None` and `list[str]`. Support Python 3.11 and newer.
- Use Ruff for linting and formatting, and ty for source type checking.

## Conda integration and safety

- Reuse conda's `PrefixData`, environment lookup, parser helpers, context, and
  error handling. Do not introduce a separate environment resolver or config
  system. Missing-environment lookup must not create directories.
- Environment selection uses `-n`/`--name` or `-p`/`--prefix` on `list`,
  `install`, and `remove`. Destination scope is independent: project root by
  default, home with `--global`.
- Home-directory mutations require explicit `--global`. Preserve the existing
  backend paths for `agents` and `claude`.
- Discover only headers recorded in conda packages. Validate names, frontmatter,
  duplicate ownership, and filesystem containment. Never execute skill content
  or imply that package ownership establishes trustworthiness.
- Installation is idempotent for a matching link and refuses other destinations.
  Removal only unlinks a matching destination; it never deletes package files.
- Preserve redirected-directory and escaping-symlink checks. Keep relative links
  where possible and absolute targets across Windows drives. Do not silently
  fall back to copies when symlink creation fails.

## Output

- Rich renders human output in `cli.py`: labeled tables, explicit empty states,
  and plain confirmations. Avoid progress displays for short local operations.
- Treat descriptions, names, and paths as literal text. Render terminal control
  characters visibly and prevent Rich markup interpretation.
- `--json` changes only output format. Use `context.json` and emit one complete,
  unstyled JSON value on stdout. Never send structured JSON through Rich.
- Preserve the result shapes: arrays for `list` and `status`, `name` and `path`
  for `install`, and `name` and boolean `removed` for `remove`.
- Translate validation and filesystem errors through conda's normal error
  handling. Do not mix confirmations or table output into JSON responses.

## Testing

- Use plain pytest functions, descriptive names, and parametrized cases. Do not
  group tests in classes or use `unittest.mock`, `Mock`, `MagicMock`, or `patch`.
- Use pytest fixtures, real temporary package records and files, and small
  recording closures where needed. Link unit tests construct `Skill` directly;
  installed CLI tests exercise discovery and linking together.
- Use direct hook and parser assertions for registration tests, following
  conda-global and conda-workspaces. Do not embed Python scripts in strings or
  pass inline programs to `python -c` in tests.
- Keep installed metadata and real plugin-manager discovery checks. Fresh-process
  lazy-import checks execute `test_plugin.py` as a file outside the checkout;
  in-process checks cannot rely on modules staying unloaded during collection.
- CLI subprocesses use the shared module-local runner fixture with an isolated
  home and condarc. Remove inherited conda settings and `PYTHONPATH`, and use
  narrow explicit overrides when a test needs them.
- Cover filesystem conflicts and containment, malformed metadata, human output,
  literal terminal text, and complete JSON documents. Prefer behavioral assertions
  over snapshots of table borders or implementation details.
- When shared test support files are added, ensure the source distribution
  includes them. `MANIFEST.in` includes `tests/conftest.py` explicitly.

## Validation and lockfiles

Run the full checks after production or test changes:

```sh
pixi run --locked check
```

This installs the editable plugin in the selected environment and runs pytest,
Ruff lint, the formatting check, and ty. Use `pixi run --locked format` to apply
formatting. Validate packaging changes with:

```sh
pixi run --locked build
```

- Run `pixi lock` after dependency or workspace metadata changes and keep the
  updated lockfile with those changes. Do not hand-edit the lockfile.
- Report checks actually run. Locked Linux, macOS ARM64, and Windows environments
  do not establish native-platform test coverage; report native runs separately.
- Do not claim CI, publication, or agent-client discovery from local test results.

## Documentation and collaboration

- Keep README commands and names consistent with the implementation. Explain
  source environments, destination scopes, ownership, and trust separately.
- Keep prose factual and concise. Do not copy conda-workspaces' solver, task,
  manifest, Sphinx, or coverage workflows into this smaller plugin.
- Write PR and issue bodies with one line per paragraph or bullet. Keep commit
  subjects concise. Commit, push, or publish only when explicitly requested.
- Preserve unrelated changes. Do not assume the checkout has Git metadata or
  create worktrees for routine edits.
