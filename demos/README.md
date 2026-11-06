# Record the demos

These terminal recordings use [VHS](https://github.com/charmbracelet/vhs) and the shared visual settings from conda-workspaces: JetBrains Mono, Dark+, and a 1200-pixel-wide terminal. Most recordings are 600 pixels tall. Quickstart uses 800 pixels to leave room for its prompts and confirmation. The commands execute against the current checkout, producing real output.

## Record locally

Install VHS, its `ttyd`/browser dependencies, FFmpeg, [bat](https://github.com/sharkdp/bat), and JetBrains Mono using your platform's tools. Recording is tested on macOS, and `setup.sh` requires Bash and a POSIX environment. These tools are not needed to build the documentation from the committed GIFs. The prompt uses conda-workspaces' green accent, and file previews use bat's Visual Studio Dark+ theme. The recording shell supplies color, plain-style, and no-paging flags so the visible command stays short.

From the repository root:

```sh
conda workspace install --locked -e build
conda task run -e build install
conda task run -e build build-example
vhs demos/use-a-skill.tape
vhs demos/quickstart.tape
vhs demos/skill-forge.tape
vhs demos/recover-link.tape
```

The workspace recording also needs a conda executable with conda-workspaces installed. Set its absolute path explicitly so the recording does not inherit an unrelated shell function:

```sh
export DEMO_WORKSPACES_CONDA="$(conda info --base)/bin/conda"
vhs demos/project-skills.tape
```

Check `"$DEMO_WORKSPACES_CONDA" workspace --help` first. This recording setup targets POSIX systems. The guides provide separate PowerShell instructions. Skill-forge and workspace recordings download from the network and select libmamba in their temporary shells. The pinned Polars example is version `0.0.8`.

`setup.sh` creates a fresh temporary home and project, installs the local example package for the first demo, and removes that temporary directory when the recording shell exits. It does not alter your normal home or install packages into base. Build and environment setup are hidden from the recording and described on the demos page.

The recording shell's `conda` command invokes the build environment's Python explicitly for skill and package operations, and `DEMO_WORKSPACES_CONDA` for workspace operations. This overrides inherited aliases and `conda init` functions. Source the setup only in the disposable recording shell.

- `_settings.tape`: shared appearance and timing.
- `use-a-skill.tape`: list, review, install, status, and remove.
- `quickstart.tape`: create authoring files with confirmation.
- `skill-forge.tape`: download a published skill package and create a project link.
- `project-skills.toml` and `project-skills.tape`: declare, lock, install, and link a project's skills.
- `recover-link.tape`: inspect and repair a broken link without deleting package files.
- `*.gif`: generated recordings embedded in the docs.

After recording, watch each GIF, check that commands succeeded, and rebuild the docs. Keep the text equivalents on `docs/demos.md` in sync so readers can follow the instructions without watching a recording.
