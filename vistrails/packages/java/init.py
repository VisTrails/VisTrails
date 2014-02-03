"""Entry point for the Java package.

Here we create the modules for each Java package from the serialized
information we have as JSON.
"""

import hashlib
import warnings

from vistrails.core import configuration
from vistrails.core import debug
from vistrails.core.modules.module_registry import get_module_registry

from ._json import has_fast_json
from .module_generator import JavaPackage
from .module_runtime import JavaBaseModule


class JavaConfigurationError(Exception):
    pass


def hashfile(filename, hash=hashlib.sha1()):
    """Computes the hash of a file, given its path.

    Opens the file in binary mode and wraps the appropriate calls to
    hash.update(). hash defaults to MD5.
    """
    block_size = hash.block_size
    with open(filename, 'rb') as f:
        chunk = f.read(block_size)
        while chunk:
            hash.update(chunk)
            if len(chunk) != block_size:
                break
            chunk = f.read(block_size)
    return hash.hexdigest()


PACKAGES = {}


def initialize():
    """Entry point for this package.

    This function create the VisTrails Modules from the JSON files.
    """
    if not has_fast_json:
        warnings.warn("We appear to be using a pure-Python JSON library; this "
                      "is slower")

    reg = get_module_registry()
    reg.add_module(JavaBaseModule, abstract=True)

    package_names = getattr(configuration, 'packages', '')
    package_names = filter(lambda x: x, package_names.split(';'))

    enabled = set()
    for pkgname in package_names:
        enabled.add(pkgname)
        try:
            PACKAGES[pkgname] = JavaPackage(pkgname)
        except Exception, e:
            debug.critical("Got exception while enabling package %s" % pkgname,
                           e)

    for pkgname, package in PACKAGES.items():
        if package not in enabled:
            package.disable()
            del PACKAGES[pkgname]


def finalize():
    for package in PACKAGES.itervalues():
        package.disable()
    PACKAGES = {}
