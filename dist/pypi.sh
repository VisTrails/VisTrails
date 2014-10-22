#!/bin/sh

# This script automatically builds a source package ("sdist") and wheel
# ("bdist_wheel") of VisTrails

cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
    echo "Usage: $(basename $0) <target_directory>" >&2
    exit 1
fi

DEST_DIR="$1"

# Builds source distribution
python setup.py sdist --dist-dir $DEST_DIR

# Is wheel available?
if python -c "import wheel" >/dev/null 2>&1; then
    # Build the wheel
    python setup.py bdist_wheel --dist-dir $DEST_DIR
else
    echo "'wheel' is not installed, not building wheel" >&2
fi
