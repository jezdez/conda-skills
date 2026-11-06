# Packages, skills, libraries, and client discovery

Using a packaged skill involves several names and locations. For the Polars example, `agent-skill-polars` is a conda package, `polars` is the skill name, and the Polars library is software your code may use. The `conda-skills` plugin connects an installed skill directory to a filesystem location supported by an agent client.

These objects have separate installation and discovery rules. Keeping them separate explains why installing a package does not necessarily make a skill appear in a client, and why linking a skill does not make a Python import work.

## The package distributes files

A conda package has a package name, version, build, dependencies, and an archive containing files. Conda installs those files into an environment and records the package's file list in `conda-meta/`.

A skill package places a header at `share/agent-skills/<skill-name>/SKILL.md` inside that environment. It can include references, scripts, and other files beneath the skill directory. One package can distribute several skills. Its package name does not have to match any skill name, and the `agent-skill-` prefix is a naming convention rather than a discovery requirement.

For example, `agent-skill-polars` version `0.0.8` distributes the skill named `polars`. `conda install` takes the package name; `conda skill install` takes the skill name. The version reported by `conda skill list` comes from the owning conda package record. It is not a Polars library version or a version inferred from the instructions.

## The skill supplies instructions

A skill is a directory of instructions and supporting material. Its `SKILL.md` header names the skill and describes when it should be used. The rest of that file and its companion files tell the agent how to approach work.

The plugin reads and validates the header, checks directory containment, and links the whole directory. It does not interpret the instruction body, execute companion scripts, or decide whether a request in the text is appropriate. The agent client controls how instructions enter a session and which operations require permission.

`conda skill init` creates authoring files. They become discoverable through this plugin only after a conda package records the installed header in the required layout. An arbitrary `SKILL.md` in a checkout or a manually copied directory does not acquire conda package ownership by existing on disk.

## The library is a separate dependency

A skill about Polars can describe Polars APIs without containing the library. `conda skill install polars` creates a symlink; it does not solve an environment or install Python, Polars, or any other tool mentioned by the instructions.

Installing the *package* with conda can bring dependencies, depending on its metadata:

- A `depends` entry requires the named package and its allowed version in the same environment. Conda may install or change that dependency while installing the skill package.
- A `constrains` entry limits a package's version if that package is present. It does not, by itself, cause the constrained package to be installed.
- A library named only in the skill's prose has no effect on conda's solver.

Check the actual package metadata and transaction plan instead of inferring these relationships from the package name. Authors declare runtime requirements and compatibility constraints in their recipes; `conda-skills` does not derive either from the instructions.

These relationships apply within the environment conda solves. If skill packages live in a dedicated `skills` environment while the application runs in another environment, a constraint in the skills environment does not constrain the application's library version. Review the instructions against the application environment yourself. Linking also does not select the Python interpreter, kernel, or shell an agent will use.

## The plugin discovers package-owned headers

`conda skill list` reads conda package records in the selected source environment. It considers the exact path `share/agent-skills/<name>/SKILL.md` only when that path appears in a package's recorded file list. It validates the name and description, rejects duplicate skill names owned by different packages, and checks filesystem containment.

That process differs from searching the environment for every file named `SKILL.md`. Untracked directories are ignored. A pip-only installation does not supply the conda package record this discovery requires. Installing a Python plugin through conda-pypi is also separate from packaging skill headers at the required paths; converting a wheel does not make arbitrary instructions discoverable.

Package ownership identifies the package record associated with the header. Discovery does not verify signatures or compare current files with archive hashes. Companion files are checked for containment, not individually attributed to an owning package. See {doc}`ownership-and-trust` for the limits of this evidence.

## A link exposes the installed directory

After discovery, `conda skill install` creates a directory symlink under the destination root. The `agents` backend uses `.agents/skills/<name>`; `claude` uses `.claude/skills/<name>`.

The source environment and destination root are independent. `-n` or `-p` selects where to find package-owned skills. By default, the current directory is the destination root; `--global` explicitly chooses the home directory. The plugin must be installed in the environment running conda, which can differ from both the source environment and the project's application environment.

For a workspace source, the relationship is:

```text
project/
  conda.toml
  conda.lock
  .conda/envs/skills/share/agent-skills/polars/
    SKILL.md
  .agents/skills/polars -> ../../.conda/envs/skills/share/agent-skills/polars
```

The link exposes live content. Replacing the package at the same path can change the visible instructions; deleting the source can leave the link broken. A link has no independent package version. This is why {doc}`../how-to/update-skills` removes links before package changes and restores them only after review.

## The client performs its own discovery

An agent client decides which directories to search, when to reload them, how to select skills, and whether to display them in a graphical interface. A supported directory convention is only one part of that behavior. Clients can differ by version, project settings, or session state.

`conda skill status` checks destination entries on disk. Its `linked` state means a symlink leads to a directory containing `SKILL.md`; it does not validate the header, establish package ownership, or confirm that any client has read it. A link created by another tool can also appear as `linked`.

To confirm client discovery, consult that client's documentation and inspect its own skill listing or session behavior. The plugin does not query a client API, configure a GUI, start an agent, or report whether a skill was invoked successfully. The setup commands and their filesystem outcomes are covered in {doc}`../how-to/project-skills` and {doc}`../how-to/use-an-installed-skill`.
