# Sourced by the recordings; all mutations stay in a disposable directory.
DEMO_REPO="$PWD"
export PATH="$DEMO_REPO/.conda/envs/build/bin:$PATH"
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
export PS1='$ '
unset PYTHONPATH
if [ "$1" = "installed" ]; then
    conda create --yes --offline --prefix "$DEMO_ROOT/skills" \
        "$DEMO_REPO/conda-dist/noarch/conda-skills-example-0.1.0-0.conda"
fi
cd "$DEMO_ROOT/project" || return 1
