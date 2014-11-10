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

* Make sure `inkscape` is installed and in your path (for updating splash screen)
* Update ALPS version from http://archive.comp-phys.org/software/vistrails/
  in `dist/windows/*.iss` scripts and `dist/mac/make_app`
* Update CHANGELOG with version, branch, hash and release notes
* In `dist/common/` run `./prepare_release.py`, this updates the values
  from CHANGELOG where it is needed.
* Commit changes to git
* Create a new annotated tag, e.g.: `git tag -a v2.1.0`
* Push commits to github

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

With the build environment set up, got to dist/mac and run:

    $ dist/mac/make_app name-of-binary

## Windows

The Windows installer uses [Inno Setup][inno].

Make sure the build environment is set up. The build scripts are in `dist/windows/`.
There are 2 for 32/64 bit and 2 more for versions that include GDAL.

TODO: There seem to be a lot of hardcoded paths in the `.iss` scripts, so this
is probably not very portable. But a script could configure that. Also, the
command to run Inno Setup?
NOTE: the master scripts have been refactored to remove a lot of the redundancy

#Building the release

First run the usersguide buildbot to make sure it is updated on the web. Note
that the sync script is only run nightly.

Buildbot is set up to build 2.1+ releases, give each builder the release
version tag as branch (e.g. branch=v2.1.5) and force build them. Note we need
a different buildbot for 2.1 and 2.2 releases due to changed directory structure.

For 2.1 release:
  http://128.238.102.101:9050/builders/binary-build-mac-2.1
  http://128.238.102.101:9050/builders/binary-build-win32-2.1
  http://128.238.102.101:9050/builders/binary-build-win64-2.1
  http://128.238.102.101:9050/builders/binary-build-win32-gdal-2.1
  http://128.238.102.101:9050/builders/binary-build-win64-gdal-2.1

For 2.2+ release:
  http://128.238.102.101:9050/builders/binary-build-mac-2.2
  http://128.238.102.101:9050/builders/binary-build-win32-2.2
  http://128.238.102.101:9050/builders/binary-build-win64-2.2
  http://128.238.102.101:9050/builders/binary-build-win32-gdal-2.2
  http://128.238.102.101:9050/builders/binary-build-win64-gdal-2.2

http://128.238.102.101:9050/builders/build-src

#Publishing the release
TODO: How to publish PyPI and Anaconda?

##Upload to sourceforge
TODO: make script for this
* Downloading all built binaries from above
* Zip the windows binaries
* Download users guide
* Fetch CHANGELOG and rename to README
* Upload everything to sourceforge in a new release directory.

## Update wiki
Update file sizes from sourceforge in `scripts/create_release_wiki_table.py`.
Run it and use the result to update the vistrails downloads page (and archive page).

##Update "Check For Updates"

If this is a new stable version, log in to vistrails.org and update the version number in:
/srv/wiki/vistrails/downloads/dist/release_version.txt

## Publish to the vistrails wiki news page

## Send email to vistrails-users and vistrails-dev

#Post release steps

Merge changes downstream, e.g., from v2.1 -> v2.2 -> master so that future changes
can be propagated. Before committing each merge, update version in CHANGELOG and
run prepare_release.py so that the splash and CHANGELOG is kept up-to-date.