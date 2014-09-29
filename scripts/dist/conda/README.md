# What is this

This is the recipe used to build the Conda package for VisTrails.

Note that these are binary packages, and so they have to be built for every
platform (and architecture).

# How to build

The build gets a tarball from PyPI, so a source package should be uploaded
there first. **You do not need the rest of the VisTrails source to build the
package, just the `vistrails` directory alongside this README**.

* Update the version, URL and md5 in meta.yaml
* Run `conda build vistrails`
* Run `binstar upload anaconda/conda-bld/<system>/vistrails-<version>.tar.bz2`

# Full procedure for Linux with Vagrant

```
# Install Anaconda
./Anaconda-2.0.1-*.sh

# Install patchelf
sudo aptitude install build-essential git autoconf autoreconf
git clone https://github.com/NixOS/patchelf.git
cd patchelf/
./bootstrap.sh
./configure
make
sudo make install
cd

# This will need an X server (or use xvfb?)
export DISPLAY=:0

# Build VisTrails
vi vistrails/meta.yaml # Update version, url, md5
conda build vistrails

# Upload binary
binstar upload anaconda/conda-bld/linux-32/vistrails-2.1.4-np18py27_0.tar.bz2
```
