#!/usr/bin/env bash
# Uninstall PhysPlot from macOS.
#
#   curl -fsSL https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/main/scripts/uninstall_macos.sh | bash
#
# Removes what scripts/install_macos.sh added: ~/.physplot, ~/Applications/PhysPlot.app
# (and its Finder "Open With" entry) and PhysPlot's saved settings. Your own files in
# ~/Documents/PhysPlot and Python are kept unless you ask for them to go:
#
#   PHYSPLOT_REMOVE_USER_FILES set to 1 to also delete ~/Documents/PhysPlot (your modules)
#   PHYSPLOT_REMOVE_PYTHON     set to 1 to also uninstall Homebrew's Python 3.12-3.14
#                              (Homebrew refuses while other formulae need one) and pip's
#                              cache. A python.org Python needs sudo; the script prints how.
#   PHYSPLOT_HOME              install folder (default: ~/.physplot)
#   PHYSPLOT_APP_DIR           where PhysPlot.app is (default: ~/Applications)
#
# Put the variables before bash, for example: curl ... | PHYSPLOT_REMOVE_PYTHON=1 bash

set -euo pipefail

INSTALL_DIR="${PHYSPLOT_HOME:-$HOME/.physplot}"
APP_DIR="${PHYSPLOT_APP_DIR:-$HOME/Applications}"
APP="$APP_DIR/PhysPlot.app"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"

say() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }
remove() {
    if [[ -e "$1" || -L "$1" ]]; then rm -rf "$1"; say "Removed $1"; fi
}

[[ "$(uname -s)" == "Darwin" ]] || fail "This uninstaller is for macOS. On Windows, use uninstall_windows.ps1."

# Deleting the environment under a running PhysPlot would crash it and lose unsaved work.
# A venv's python shows up as the base interpreter in `ps`, so look for Python processes
# holding files (numpy's and Qt's libraries) from the install folder open instead.
physplot_running() {
    local pids
    pids="$(pgrep -i python 2>/dev/null | paste -sd, -)"
    [[ -n "$pids" ]] || return 1
    lsof -a -p "$pids" -Fn 2>/dev/null | grep -q "^n$INSTALL_DIR/"
}
if physplot_running; then
    fail "PhysPlot is still open. Quit every PhysPlot window (and any PhysPlot command running in a terminal), then run this command again."
fi

say "Removing PhysPlot"
if [[ -d "$APP" && -x "$LSREGISTER" ]]; then
    "$LSREGISTER" -u "$APP" >/dev/null 2>&1 || true
fi
remove "$APP"
remove "$INSTALL_DIR"

say "Removing saved settings"
defaults delete com.physlab.PhysPlot >/dev/null 2>&1 || true
remove "$HOME/Library/Preferences/com.physlab.PhysPlot.plist"
remove "$HOME/Library/Saved Application State/org.physlab.physplot.savedState"

DOCUMENTS="$HOME/Documents/PhysPlot"
if [[ "${PHYSPLOT_REMOVE_USER_FILES:-}" == "1" ]]; then
    remove "$DOCUMENTS"
elif [[ -d "$DOCUMENTS" ]]; then
    say "Kept your files in $DOCUMENTS"
fi

if [[ "${PHYSPLOT_REMOVE_PYTHON:-}" == "1" ]]; then
    if command -v brew >/dev/null 2>&1; then
        for version in 3.12 3.13 3.14; do
            if brew list --formula "python@$version" >/dev/null 2>&1; then
                say "Uninstalling Homebrew python@$version"
                brew uninstall "python@$version" \
                    || printf '  Kept python@%s: other Homebrew formulae need it (brew uses --installed python@%s).\n' "$version" "$version"
            fi
        done
    fi
    remove "$HOME/Library/Caches/pip"
    for framework in /Library/Frameworks/Python.framework/Versions/3.1[2-4]; do
        [[ -d "$framework" ]] || continue
        version="${framework##*/}"
        printf '  Python %s from python.org is installed. To remove it (needs your password):\n' "$version"
        printf '    sudo rm -rf "%s" "/Applications/Python %s"\n' "$framework" "$version"
    done
fi

say "PhysPlot is uninstalled."
if [[ "${PHYSPLOT_REMOVE_PYTHON:-}" != "1" ]]; then
    echo "  Python was kept. To remove it too: curl ... | PHYSPLOT_REMOVE_PYTHON=1 bash"
fi
