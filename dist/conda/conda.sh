#!/bin/sh

# This script automatically builds a Conda package

cd "$(dirname "$0")/../.."
VT_DIR="$(pwd)"

# Clears Conda cache
ANACONDA_CACHE="$(dirname "$(which python)")/../conda-bld/src_cache/vistrails.tar.gz"
rm -f "$ANACONDA_CACHE"

if [ -z "$1" ]; then
    echo "Usage: $(basename $0) <target_directory> [version]" >&2
    exit 1
fi
if [ -z "$2" ]; then
    VERSION="$(../get_version.sh)"
else
    VERSION="$2"
fi

DEST_DIR="$1"

TEMP_DIR=$(mktemp -d)

# Builds source distribution
if ! python setup.py sdist --dist-dir $TEMP_DIR; then
    rm -Rf $TEMP_DIR
    exit 1
fi

# Creates symlink
TEMP_FILE="$(echo $TEMP_DIR/*)"
ln -s "$TEMP_FILE" $TEMP_DIR/vistrails.tar.gz

# Copies conda recipe
cp -r dist/conda/vistrails $TEMP_DIR/vistrails

# Changes version in recipe
VERSION_ESCAPED="$(echo "$VERSION" | sed 's/\\/\\\\/g' | sed 's/\//\\\//g')"
sed -i "s/_REPLACE_version_REPLACE_/$VERSION_ESCAPED/g" $TEMP_DIR/vistrails/meta.yaml

# Builds Conda package
cd $TEMP_DIR
OUTPUT_PKG="$(conda build --output vistrails)"
if ! conda build vistrails; then
    rm -Rf $TEMP_DIR
    rm -f "$ANACONDA_CACHE"
    exit 1
fi

# Copies result out
cp "$OUTPUT_PKG" $DEST_DIR/

# Removes temporary directory
rm -Rf $TEMP_DIR

# Clears Conda cache
rm -f "$ANACONDA_CACHE"
