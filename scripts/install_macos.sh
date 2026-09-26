#!/usr/bin/env bash
# Install or update PhysPlot on macOS.
#
#   curl -fsSL https://raw.githubusercontent.com/MShirazAhmad/PhysPlot/indevelopment/scripts/install_macos.sh | bash
#
# Creates ~/.physplot (Python environment and PhysPlot source) and
# ~/Applications/PhysPlot.app. Run the same command again to update.
# Uninstall: rm -rf ~/.physplot ~/Applications/PhysPlot.app
#
# Optional environment variables:
#   PHYSPLOT_REF      branch or tag to install (default: indevelopment)
#   PHYSPLOT_HOME     install folder (default: ~/.physplot)
#   PHYSPLOT_APP_DIR  where to put PhysPlot.app (default: ~/Applications)
#   PHYSPLOT_SOURCE   install from this local checkout instead of downloading

set -euo pipefail

REPO="MShirazAhmad/PhysPlot"
REF="${PHYSPLOT_REF:-indevelopment}"
INSTALL_DIR="${PHYSPLOT_HOME:-$HOME/.physplot}"
APP_DIR="${PHYSPLOT_APP_DIR:-$HOME/Applications}"
LOCAL_SOURCE="${PHYSPLOT_SOURCE:-}"
VENV="$INSTALL_DIR/venv"
APP="$APP_DIR/PhysPlot.app"

say() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }

[[ "$(uname -s)" == "Darwin" ]] || fail "This installer is for macOS. On Windows, use the PhysPlot installer."
[[ "$INSTALL_DIR" != *" "* ]] || fail "PHYSPLOT_HOME must not contain spaces: $INSTALL_DIR"

# PhysPlot's Figure Editor (FigureForge) supports Python 3.11-3.13.
python_ok() {
    "$1" -c 'import sys; sys.exit(0 if (3, 11) <= sys.version_info[:2] <= (3, 13) else 1)' >/dev/null 2>&1
}

find_python() {
    local candidate path version
    for version in 3.12 3.13 3.11; do
        for candidate in "python$version" "/opt/homebrew/bin/python$version" "/usr/local/bin/python$version" \
            "/Library/Frameworks/Python.framework/Versions/$version/bin/python$version"; do
            path="$(command -v "$candidate" 2>/dev/null)" || continue
            if python_ok "$path"; then
                echo "$path"
                return 0
            fi
        done
    done
    path="$(command -v python3 2>/dev/null)" && python_ok "$path" && { echo "$path"; return 0; }
    return 1
}

say "Looking for Python 3.11-3.13"
if ! PYTHON="$(find_python)"; then
    if command -v brew >/dev/null 2>&1; then
        say "Installing Python 3.12 with Homebrew"
        brew install python@3.12
        PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
    else
        fail "Python 3.11-3.13 is required. Install Python 3.12 from https://www.python.org/downloads/macos/ (or Homebrew), then run this command again."
    fi
fi
python_ok "$PYTHON" || fail "Could not use $PYTHON."
say "Using $PYTHON ($("$PYTHON" -c 'import platform; print(platform.python_version())'))"

mkdir -p "$INSTALL_DIR"
if [[ -n "$LOCAL_SOURCE" ]]; then
    SOURCE="$(cd "$LOCAL_SOURCE" && pwd)"
    say "Installing from local source $SOURCE"
else
    SOURCE="$INSTALL_DIR/src"
    say "Downloading PhysPlot ($REF) from GitHub"
    TMP="$(mktemp -d)"
    trap 'rm -rf "$TMP"' EXIT
    curl -fsSL "https://github.com/$REPO/archive/$REF.tar.gz" -o "$TMP/physplot.tar.gz" \
        || fail "Could not download https://github.com/$REPO/archive/$REF.tar.gz"
    tar -xzf "$TMP/physplot.tar.gz" -C "$TMP"
    rm -rf "$SOURCE"
    mv "$TMP"/PhysPlot-* "$SOURCE"
fi

if [[ -x "$VENV/bin/python" ]] && python_ok "$VENV/bin/python"; then
    say "Updating the PhysPlot environment in $VENV"
else
    say "Creating the PhysPlot environment in $VENV"
    rm -rf "$VENV"
    "$PYTHON" -m venv "$VENV"
fi
say "Installing PhysPlot and its dependencies (about 1 GB the first time; this can take a few minutes)"
"$VENV/bin/python" -m pip install --quiet --upgrade pip
# Editable install, so the bundled config/ folder (transformations, loaders,
# templates) stays next to the code where PhysPlot looks for it.
"$VENV/bin/python" -m pip install --quiet --upgrade -e "$SOURCE"
"$VENV/bin/python" -c "import physplot, physplot_gui" || fail "PhysPlot did not install correctly."

say "Creating $APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>PhysPlot</string>
    <key>CFBundleDisplayName</key><string>PhysPlot</string>
    <key>CFBundleIdentifier</key><string>org.physlab.physplot</string>
    <key>CFBundleExecutable</key><string>PhysPlot</string>
    <key>CFBundleIconFile</key><string>PhysPlot</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleShortVersionString</key><string>$("$VENV/bin/python" -c 'import physplot; print(physplot.__version__)')</string>
    <key>LSMinimumSystemVersion</key><string>11.0</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST
cat > "$APP/Contents/MacOS/PhysPlot" <<LAUNCHER
#!/bin/bash
# Start in Documents so file dialogs open somewhere useful.
cd "\$HOME/Documents" 2>/dev/null || cd "\$HOME"
exec "$VENV/bin/python" -m physplot_gui "\$@"
LAUNCHER
chmod +x "$APP/Contents/MacOS/PhysPlot"
if [[ -f "$SOURCE/installer/icons/PhysPlot.icns" ]]; then
    cp "$SOURCE/installer/icons/PhysPlot.icns" "$APP/Contents/Resources/PhysPlot.icns"
fi
touch "$APP"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
[[ -x "$LSREGISTER" ]] && "$LSREGISTER" -f "$APP" >/dev/null 2>&1 || true

say "PhysPlot is installed."
cat <<DONE

  Open it:        $APP  (or search Spotlight for "PhysPlot")
  Terminal:       $VENV/bin/physplot-gui
  Command line:   $VENV/bin/physplot run-workflow Sequence.py --input data.csv --output out/
  Sample data:    $SOURCE/test_data
  Update:         run the same install command again
  Uninstall:      rm -rf "$INSTALL_DIR" "$APP"

DONE
