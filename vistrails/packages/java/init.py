"""Entry point for the Java package.

Here we create the modules for each Java package from the serialized
information we have as XML.
"""

import functools
import hashlib
import os

from vistrails.core import debug
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.system import current_dot_vistrails

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


def no_reentry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if wrapper.running:
            return None
        wrapper.running = True
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.running = False
    wrapper.running = False
    return wrapper


@no_reentry
def initialize():
    """Entry point for this package.

    This function create the VisTrails Modules from the XML files.
    """
    reg = get_module_registry()
    reg.add_module(JavaBaseModule, abstract=True)

    for filename in os.listdir(os.path.join(current_dot_vistrails(), 'Java')):
        if filename[-4:].lower() != '.xml':
            continue
        pkgname = os.path.basename(filename)[:-4]

        if pkgname not in PACKAGES:
            try:
                debug.debug("enabling %r" % pkgname)
                PACKAGES[pkgname] = JavaPackage(pkgname)
                debug.debug("enabled %r" % pkgname)
            except Exception:
                debug.debug("failed to enable %r" % pkgname)
                import traceback
                debug.critical("Got exception while enabling package %s" % pkgname,
                               traceback.format_exc())


def finalize():
    for package in PACKAGES.itervalues():
        package.disable()
    PACKAGES.clear()
