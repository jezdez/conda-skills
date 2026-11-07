# conda-skills coding guidelines

## Project structure

- The distribution and conda entry-point name are `conda-skills`. The Python
  package is `conda_skill`, and the canonical command is `conda skill` with the
  native alias `conda skills`.
- `src/conda_skill/plugin.py` owns registration. `cli/parser.py` owns lightweight
  per-command parser configuration. Neither loads execution or rendering modules.
- `cli/main.py` owns dispatch, source environment and skill selection,
  destination scope, and conda error handling. `cli/list.py`, `cli/status.py`,
  `cli/link.py`, `cli/unlink.py`, `cli/init.py`, and `cli/quickstart.py` own
  command execution and output.
  `cli/output.py` shares terminal escaping and table rendering.
- `cli/inspect.py` displays metadata and safe file previews. `cli/open.py` opens
  only the validated skill directory in the system file manager, never a file.
  File reads stay inside the skill root and must not block on special files or
  dump binary/oversized content. Neither command executes skill instructions.
- `skills.py` owns the frozen installed `Skill` model, shared metadata validation,
  directory loading, and discovery through conda package records.
  `Skill.create_skeleton()` generates authoring files and returns their path.
  It does not construct an installed skill. Quickstart keeps pending authoring
  inputs separate from its frozen `SkillSelection` for an installed skill.
- `links.py` owns backend destinations, linking and unlinking, and
  filesystem status. Status includes unmanaged and broken entries. It must not
  require a valid source environment or claim package ownership.
- Tests mirror these topics: `test_plugin.py`, `test_skills.py`, `test_links.py`,
  and command modules under `tests/cli/`, including `test_link.py` and
  `test_unlink.py`. Cross-command integration tests live in
  `tests/cli/test_dispatch.py`. Shared fixtures belong in `tests/conftest.py`
  or `tests/cli/conftest.py` according to scope.

## Imports and dependencies

- Use relative imports inside the package. Absolute `conda_skill.*` imports
  belong in tests and installed entry points.
- Imports belong at module scope. Reserve lazy imports for the plugin callbacks
  that protect conda startup, or an optional dependency whose absence is supported.
  Use `TYPE_CHECKING` for annotation-only imports.
- Rich is a required dependency. Import its output classes at module scope in
  CLI modules. Do not use optional imports, fallbacks, or imports inside rendering.
- Keep `__init__.py` free of implementation imports. Loading the plugin and
  configuring its parser must not load execution, rendering, discovery, or link
  implementations. Loading the lightweight `cli.parser` is allowed.
- Prefer stdlib, conda APIs, and existing dependencies. Do not add a framework
  or another parser for behavior an existing library handles.
- Declare minimum runtime versions in `pyproject.toml`. Provision dependencies
  through the root `conda.toml`. Conda itself comes from a conda channel, not PyPI,
  so its requirement is declared there and in the conda recipe rather than wheel
  metadata.

## Code structure

- Apply Ponytail Ultra: choose the smallest complete change and question
  additions that have no current use. Split by responsibility, not line count.
- Put behavior on an existing model when it owns the data. `Skill.from_directory`
  loads and validates one candidate. `discover` selects package-owned candidates
  and checks duplicate ownership.
- Prefer frozen dataclasses for related data with its own validation or operations.
  Do not wrap stateless formatting or parser functions in classes.
- Before adding a helper, check existing code, test fixtures, conda APIs, and
  dependencies, then whether an existing model owns the operation.
- Keep related steps together when separating them obscures their order or shared
  state. Extract when the name and inputs clarify the caller, reduce confusing
  nesting, or make substantial logic easier to test. One caller can be enough.
- Review callers and helpers together, including state changes and error handling.
  Explain the specific readability or testing benefit of extraction or inlining.
  Function length and complexity scores alone do not demonstrate improvement.
- Avoid speculative reuse and trivial forwarding wrappers unless an API requires
  them. An underscore marks an internal function, not a reason to inline it.
- Keep argparse, Rich, printing, and exit-status decisions out of domain modules.
- Do not add section-divider comments to organize large files. Use topic-specific
  modules and descriptive names.
- Add concise docstrings for functions and classes. Explain purpose,
  constraints, return values, and failure behavior without narrating the code.

## Typing and formatting

- Use `from __future__ import annotations` and modern annotations such as
  `str | None` and `list[str]`. Support Python 3.11 and newer.
- Use Ruff for linting and formatting, and ty for source type checking.
- Pytest-cov measures branches and subprocess execution in the normal test run.
  Keep combined coverage at or above 95%. Exclude generated version metadata only.
  Review uncovered behavior rather than treating the percentage as proof of correctness.

## Conda integration and safety

- Reuse conda's `PrefixData`, environment lookup, parser helpers, context, and
  error handling. Do not introduce a separate environment resolver or config
  system. Missing-environment lookup must not create directories.
- Environment selection uses `-n`/`--name` or `-p`/`--prefix` on `list`,
  `link`, `inspect`, `open`, and quickstart's installed-skill branch. The default is conda's active
  target environment. `unlink` takes no source-environment flags. Destination
  scope is independent: current directory by default, home with `--global`.
- Home-directory mutations require explicit `--global`. Preserve the existing
  backend paths for `agents` and `claude`.
- Prefer the cross-client `.agents/skills/` convention over adding agent-specific
  backends. Batch quickstart selections remain within one explicit source environment,
  preview every destination, and check conflicts before confirmation. Never remove
  unselected links. `status --all` inspects existing backends only in the chosen scope.
- `init` creates an authoring skeleton, not an installed or trusted skill.
  Never overwrite an existing destination, including a dangling symlink. Serialize
  user-provided metadata safely rather than interpolating it into YAML.
- `quickstart` is a deterministic interactive guide, not an AI agent. Reuse the
  same discovery, skeleton generation, and linking operations as explicit commands.
  Require an interactive terminal and confirmation before writes. Do not install
  packages implicitly. Selecting home in a prompt does not replace `--global`.
- Discover only headers recorded in conda packages. Validate names, frontmatter,
  duplicate ownership, and filesystem containment. Never execute skill content
  or imply that package ownership establishes trustworthiness.
- Linking reuses a matching link and refuses other destinations.
- Unlinking derives the source from the destination symlink target and validates
  that it matches a recorded conda skill. Do not scan the environment registry or
  claim the plugin created the link. An absent destination returns false without
  source lookup. Broken or unverifiable targets require status inspection and
  explicit `--force`, which removes only a symlink, never a file or directory,
  and never bypasses redirected-parent checks. Never delete package files.
- Preserve redirected-directory and escaping-symlink checks. Keep relative links
  where possible and absolute targets across Windows drives. Do not silently
  fall back to copies when symlink creation fails.

## Output

- Rich renders human output in `cli/`: labeled tables, explicit empty states,
  and plain confirmations. Avoid progress displays for short local operations.
- Treat descriptions, names, and paths as literal text. Render terminal control
  characters visibly and prevent Rich markup interpretation.
- `--json` changes only output format. Use `context.json` and emit one complete,
  unstyled JSON value on stdout. Never send structured JSON through Rich.
- The interactive `quickstart` command rejects JSON mode before prompting and
  directs non-interactive users to explicit commands.
- Preserve the result shapes: arrays for `list` and `status`, `name` and `path`
  for `link`, and `name` and boolean `removed` for `unlink`.
- Translate validation and filesystem errors through conda's normal error
  handling. Do not mix confirmations or table output into JSON responses.

## Testing

- Use plain pytest functions, descriptive names, and parametrized cases. Do not
  group tests in classes or use `unittest.mock`, `Mock`, `MagicMock`, or `patch`.
- Use pytest fixtures, real temporary package records and files, and small
  recording closures where needed. Link unit tests construct `Skill` directly.
  Installed CLI tests exercise discovery and linking together.
- Use direct hook and parser assertions for registration tests, following
  conda-global and conda-workspaces. Do not embed Python scripts in strings or
  pass inline programs to `python -c` in tests.
- Keep installed metadata and real plugin-manager discovery checks. Fresh-process
  lazy-import checks execute `test_plugin.py` as a file outside the checkout.
  In-process checks cannot rely on modules staying unloaded during collection.
- CLI subprocesses use the shared runner fixture in `tests/cli/conftest.py` with an isolated
  home and condarc. Remove inherited conda settings and `PYTHONPATH`, and use
  narrow explicit overrides when a test needs them.
- Cover filesystem conflicts and containment, malformed metadata, human output,
  literal terminal text, and complete JSON documents. Prefer behavioral assertions
  over snapshots of table borders or implementation details.
- Include new shared test support files in the source distribution.
  Hatchling's explicit sdist includes in `pyproject.toml` cover `tests/`, including
  its shared `conftest.py` files. Keep build output out of the source distribution.
- Artifact checks execute `scripts/smoke_plugin.py` outside the checkout. The wheel
  check uses a disposable environment and verifies that imports come from it.
- Exercise generated skill recipes through an actual build and installed discovery.
  Checking that template files exist is not sufficient validation.

## Validation and lockfiles

Bootstrap the workspace tooling when needed:

```sh
conda install -n base --yes --override-channels -c conda-forge 'conda>=26.9' 'conda-workspaces>=0.12'
```

The root `conda.toml` defines `default`, `py311`, `py314`, `docs`, and `build`.
Install the selected environment from `conda.lock` before running tasks. Run the
full checks after production or test changes:

```sh
conda workspace install --locked -e default
conda task run -e default check
```

The `check` task installs the editable plugin in the selected environment and runs
pytest, Ruff lint, the formatting check, and ty. Use
`conda task run -e default format` to apply formatting. Validate packaging changes
with:

```sh
conda workspace install --locked -e build
conda task run -e build build
```

- `--locked` belongs to workspace installation, not task execution. Tasks only run
  named manifest tasks. Use `conda workspace run -e ENV -- COMMAND` for arbitrary
  commands in an installed environment.
- Run `conda workspace lock` after dependency or workspace metadata changes and
  keep the generated `conda.lock` with those changes. Do not hand-edit the lockfile.
- Keep runtime dependencies shared. Put lint tools in `dev`, pytest and coverage
  in `test`, and documentation and artifact tools in their own features. Test and
  build environments also need the backend dependencies for editable installation.
- Report checks actually run. Locked Linux, macOS ARM64, and Windows environments
  do not establish native-platform test coverage. Report native runs separately.
- Do not claim CI, publication, or agent-client discovery from local test results.

## Documentation and collaboration

- Keep README commands and names consistent with the implementation. Explain
  source environments, destination scopes, ownership, and trust separately.
- Maintain the Sphinx/MyST site under `docs/` with `conda-sphinx-theme` and
  `sphinx-design`. Organize tutorials, how-to guides, reference, and explanations
  around reader needs. Strict docs builds treat warnings as errors.
- Keep prose factual and concise. Execute tutorial examples. A successful HTML
  build does not prove commands work. Keep unreleased installation paths explicit.
- User installation docs use conda or conda-pypi in the environment owning conda.
  Reserve conda-workspaces commands for contributor workflows and package-build
  tooling.
- Use conda-workspaces for development tooling. Do not add solver, task, or
  workspace-manifest implementations to this plugin.
- Build with Hatchling and hatch-vcs. Derive the Python version from Git and never
  edit the generated `src/conda_skill/_version.py`. The `0.1.0` fallback is for
  development without usable version metadata, not evidence of a release.
- Resolve the conda build version with `python -m hatchling version` directly
  in the build task. The task supplies
  `CONDA_SKILLS_VERSION`, which the recipe requires without a default. Its
  build-local `SETUPTOOLS_SCM_PRETEND_VERSION` supplies that resolved version when
  building copied source without Git. Release workflows use the Hatch CLI and
  a shell comparison with the tag, not a custom release-check script. Dated
  changelog notes are a manual pre-tag checklist item. Do not override the version.
  Follow `RELEASING.md`. Version checks do not authorize tagging or publishing.
- Pull requests run native tests and artifact/docs checks. Stable annotated tags
  on main trigger coordinated PyPI and jezdez/main publication. Release conda
  packages come from the digest-verified published source archive, not a rebuild
  of the checkout. Sign and verify the exact artifacts before upload, preserve
  channel overwrite checks, and publish the GitHub draft after successful uploads.
  Pin actions to full commit SHAs. Do not invent repository or documentation URLs.
  Never tag, push, configure credentials, or publish without explicit authorization.
- Write PR and issue bodies with one line per paragraph or bullet. Keep commit
  subjects concise. Commit, push, or publish only when explicitly requested.
- Preserve unrelated changes. Do not assume the checkout has Git metadata or
  create worktrees for routine edits.
