# Sourced by the recordings; all mutations stay in a disposable directory.
DEMO_REPO="$PWD"
export PATH="$DEMO_REPO/.conda/envs/build/bin:$PATH"
# Bypass aliases and the base shell function installed by conda init.
unalias conda 2>/dev/null || true
conda() {
    if [ "$1" = "workspace" ]; then
        "${DEMO_WORKSPACES_CONDA:?Set DEMO_WORKSPACES_CONDA to the conda executable with conda-workspaces installed}" "$@"
    else
        "$DEMO_REPO/.conda/envs/build/bin/python" -m conda "$@"
    fi
}
DEMO_ROOT="$(mktemp -d /tmp/skills-demo.XXXXXX)"
trap 'rm -rf "$DEMO_ROOT"' EXIT
mkdir -p "$DEMO_ROOT/home" "$DEMO_ROOT/project"
export HOME="$DEMO_ROOT/home" USERPROFILE="$DEMO_ROOT/home"
export XDG_CONFIG_HOME="$HOME/.config"
export CONDARC="$DEMO_ROOT/condarc"
printf '{}\n' > "$CONDARC"
export CONDA_NO_PLUGINS=false CONDA_JSON=false
export CONDA_PKGS_DIRS="$DEMO_ROOT/package-cache"
export RATTLER_CACHE_DIR="$DEMO_ROOT/rattler-cache"
export CONDA_NOTIFY_OUTDATED_CONDA=false
export CONDA_SOLVER=libmamba
export PS1='\[\e[1;38;2;67;176;42m\]$\[\e[0m\] '
unset PYTHONPATH NO_COLOR
# Keep the recorded command short without relying on personal bat configuration.
unalias bat 2>/dev/null || true
bat() { command bat --color=always --paging=never --style=plain "$@"; }
if [ "$1" = "installed" ]; then
    conda create --yes --offline --prefix "$DEMO_ROOT/skills" \
        "$DEMO_REPO/conda-dist/noarch/conda-skills-example-0.1.0-0.conda"
fi
if [ "$1" = "workspace" ]; then
    cp "$DEMO_REPO/demos/project-skills.toml" "$DEMO_ROOT/project/conda.toml"
fi
cd "$DEMO_ROOT/project" || return 1
