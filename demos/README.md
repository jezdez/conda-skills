# Demo recordings

These terminal recordings use [VHS](https://github.com/charmbracelet/vhs) and the shared visual settings from conda-workspaces: JetBrains Mono, Dark+, and a 1200 by 600 terminal. The commands execute against the current checkout; the recordings are not animated mock output.

## Record locally

Install VHS, its `ttyd`/browser dependencies, FFmpeg, [bat](https://github.com/sharkdp/bat), and JetBrains Mono using your platform's tools. Recording is tested on macOS; `setup.sh` requires Bash and a POSIX environment. These tools are not needed to build the documentation from the committed GIFs. The prompt uses conda-workspaces' green accent; file previews use bat's Visual Studio Dark+ theme. The recording shell supplies color, plain-style, and no-paging flags so the visible command stays short.

From the repository root:

```sh
conda workspace install --locked -e build
conda task run -e build install
conda task run -e build build-example
vhs demos/use-a-skill.tape
vhs demos/quickstart.tape
```

`setup.sh` creates a fresh temporary home and project, installs the local example package for the first demo, and removes that temporary directory when the recording shell exits. It does not alter your normal home or install packages into base. Build and environment setup are hidden from the recording and described on the demos page.

The recording shell's `conda` command invokes the build environment's Python explicitly. This overrides any inherited alias or `conda init` function, so the demo does not accidentally use base's conda. Source the setup only in the disposable recording shell.

- `_settings.tape`: shared appearance and timing.
- `use-a-skill.tape`: list, review, install, status, and remove.
- `quickstart.tape`: create authoring files with confirmation.
- `*.gif`: generated recordings embedded in the docs.

After recording, watch each GIF, check that commands succeeded, and rebuild the docs. Keep the text equivalents on `docs/demos.md` in sync. Screenshots and animations supplement the written instructions; they do not replace them.
