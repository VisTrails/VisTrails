# Building the VisTrails binaries

This directory contains the various scripts, templates and extra files to build the binary releases of VisTrails.

VisTrails is a Python package and as such can be run with a standard [distribution of the Python interpreter][python] (if the Python libraries it depends on are also installed). However, we also provide "binary" releases which contain a Python interpreter and all the requirements, so that it can be installed and run on a machine without having to go through the manual installation of all components.

Making a new release has two steps: first, the developers need to update the source tree for the new version (and add a tag with Git). Then, actual release packages need to be built from the Git tree for each type.

# Preparing for a new release

* Make sure `inkscape` is installed and in your path (for updating splash screen)
* Update ALPS version from http://archive.comp-phys.org/software/vistrails/
  in `scripts/dist/windows/*.iss` scripts and `scripts/dist/mac/make_app`
* Update CHANGELOG with version, branch, hash and release notes
* In `scripts/dist/common/` run `./prepare_release.py`, this updates the values
  from CHANGELOG where it is needed.
* Commit changes
* Create a new annotated tag, e.g.: `git tag -a v2.1.0` (we don't currently sign tags)
* Push changes

# Release process

## PyPI

The packages uploaded to [PyPI](pypi) are actually source distributions. They can be built from the `setup.py`  script with:

    $ python setup.py sdist
    $ python setup.py bdist_wheel

The resulting files are in `dist/`.

## Anaconda

The recipe for building a Conda package is in `scripts/dist/conda/`. Packages must be built for each OS and architecture here: `osx-64`, `win-32`, `win-64`, `linux-32` and `linux-64`. Build on Windows is not yet automated.

## Mac

Set up your machine as described in [doc/dist/setup_build_system_mac.txt](doc/dist/setup_build_system_mac.txt)

Build the mac binary with:

    scripts/dist/mac$ ./make_app name-of-binary

## Windows

Set up your machine using as described in [doc/dist/setup_build_system_windows.txt](doc/dist/setup_build_system_windows.txt)

The Windows installer uses [Inno Setup][inno].he build scripts are in `scripts/dist/windows/`. There are one each for 32/64 bit, and 2 more for GDAL versions.  The generated `.exe` is placed in the `.\Output\` directory.

The scripts can be run from the command line using `ISCC.exe`.

Note: The `.iss` scripts are hardcoded for the described system setup, so this is not very portable. You will need to download the required program/libraries, and update this file if you are using different paths.

# Building the release using Buildbot

First run the usersguide builder to make sure it is updated on the web. Note that the sync script is only run nightly.

Buildbot is set up to build 2.1+ releases, give each builder the release version tag as branch (e.g. branch=v2.1.5) and force build them. Note that we need different builders for 2.1 and 2.2 releases due to changed directory structure.

For all releases:

* http://vistrails.poly.edu:9050/builders/build-src

For 2.1 releases:

* http://vistrails.poly.edu:9050/builders/binary-build-mac-2.1
* http://vistrails.poly.edu:9050/builders/binary-build-win32-2.1
* http://vistrails.poly.edu:9050/builders/binary-build-win64-2.1
* http://vistrails.poly.edu:9050/builders/binary-build-win32-gdal-2.1
* http://vistrails.poly.edu:9050/builders/binary-build-win64-gdal-2.1

For 2.2+ releases:

* http://vistrails.poly.edu:9050/builders/binary-build-mac-2.2
* http://vistrails.poly.edu:9050/builders/binary-build-win32-2.2
* http://vistrails.poly.edu:9050/builders/binary-build-win64-2.2
* http://vistrails.poly.edu:9050/builders/binary-build-win32-gdal-2.2
* http://vistrails.poly.edu:9050/builders/binary-build-win64-gdal-2.2

# Testing the release

Windows and mac builds can be tested by running the test suite with the builders:

*  http://vistrails.poly.edu:9050/builders/TestWinBinary
*  http://vistrails.poly.edu:9050/builders/TestMacBinary

# Publishing the release

## PyPI

Upload to PyPI using Twine. Currently the releases are not signed. Ask Remi for access.

## Anaconda

The Conda builds are on the ViDA-NYU organization on Binstar: https://binstar.org/vida-nyu/vistrails. Ask Remi for access.

## Upload to sourceforge

TODO: make script for this

* Downloading all built binaries from above
* Zip the windows binaries
* Download users guide
* Fetch `CHANGELOG` and rename to `README`
* Upload everything to `[SFUSER]@frs.sourceforge.net:/home/frs/project/vistrails/vistrails/v[VER]`

## Upload to GitHub

Create a new Release on GitHub with the changelog and attach the files to it.

## Update wiki

Update file sizes from sourceforge in `scripts/create_release_wiki_table.py`.  Run it and use the result to update the [vistrails downloads page](http://www.vistrails.org/index.php/Downloads) (and archive page).

## Update "Check For Updates"

If this is a new stable version, log in to `vistrails.org` and update the version number in `/srv/wiki/vistrails/downloads/dist/release_version.txt`

## Publish to the [vistrails wiki news page](http://www.vistrails.org/index.php/Main_Page)

## Send email to vistrails-users and vistrails-dev

# Post release steps

Merge changes downstream, e.g., from v2.1 -> v2.2 -> master. Before committing, update version in CHANGELOG and run prepare_release.py so that version, splash, and CHANGELOG is kept up-to-date.
