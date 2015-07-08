#!/bin/sh

# This script automatically builds a source package ("sdist") and wheel
# ("bdist_wheel") of VisTrails

cd "$(dirname "$0")/../.."

if [ -z "$1" ]; then
    echo "Usage: $(basename $0) <target_directory> [--no-set-version]" >&2
    exit 1
fi
if [ "$2" != "--no-set-version" ]; then
    if ! python scripts/dist/common/set_version.py setup.py; then
        echo "Setting version number in setup.py failed" >&2
        exit 1
    fi
fi

# Warning: if this path is relative, it is relative to VisTrails's source
# directory, not the directory this script is called from!
DEST_DIR="$1"

SUCCESS=0

# Builds source distribution
if ! python setup.py sdist --dist-dir $DEST_DIR; then
    SUCCESS=1
fi

# Is wheel available?
if python -c "import wheel" >/dev/null 2>&1; then
    # Build the wheel
    if ! python setup.py bdist_wheel --dist-dir $DEST_DIR; then
        SUCCESS=1
    fi
else
    echo "'wheel' is not installed, not building wheel" >&2
fi

exit $SUCCESS
