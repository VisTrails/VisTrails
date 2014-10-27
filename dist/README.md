# Building the VisTrails binaries

This directory contains the various scripts, templates and extra files to build
the binary releases of VisTrails.

VisTrails is a Python package and as such can be run with a standard
[distribution of the Python interpreter][python] (if the Python libraries it
depends on are also installed). However, we also provide "binary" releases
which contain a Python interpreter and all the requirements, so that it can be
installed and run on a machine without having to go through the manual
installation of all components.

Making a new release has two steps: first, the developers need to update the
source tree for the new version (and add a tag with Git). Then, actual release
packages need to be built from the Git tree for each type.

# Preparing for a new release

* Update release notes in `dist/mac/Input/README` and `dist/windows/Input/releaseNotes.txt`
 * TODO: needs main `CHANGELOG` file
 * TODO: remove these, copy/generate from main `CHANGELOG`
* Update version number and hash with `scripts/update_hash.py`
* Create a new annotated tag, e.g.: `git tag -a v2.1.0`

# Releases

## PyPI

The packages uploaded to [PyPI](pypi) are actually source distributions. They
can be built from the `setup.py`  script with:

    $ python setup.py sdist
    $ python setup.py bdist_wheel

The resulting files are in `dist/`.

## Anaconda

The recipe for building a Conda package is in `dist/conda/`. Packages must be
built for each OS and architecture here, typically `osx-64`, `linux-32` and
`linux-64`. Anaconda also supports Windows, but we didn't build there so far.

TODO: Currently, Conda builds from PyPI. There should be a way to build from a
local tarball.

## Mac

TODO

## Windows

The Windows installer uses [Inno Setup][inno].

TODO: There seem to be a lot of hardcoded paths in the `.iss` scripts, so this
is probably not very portable. But a script could configure that. Also, the
command to run Inno Setup?
