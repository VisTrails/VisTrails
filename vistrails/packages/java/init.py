"""Entry point for the Java package.

Here we create the modules for each Java package from the serialized
information we have as XML.
"""

import functools
import hashlib
import os

from vistrails.core import debug
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.package import Package
from vistrails.core.system import current_dot_vistrails, \
    get_elementtree_library

from . import identifiers
from .module_generator import ModuleCreator
from .module_runtime import JavaBaseModule
from .structs import PackageInfos


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


class JavaPackage(object):
    def __init__(self, pkgname):
        self.pkgname = pkgname

        debug.log("Creating Java package for %s" % pkgname)

        ElementTree = get_elementtree_library()

        # Find the XML file
        xmlfile = os.path.join(current_dot_vistrails(),
                                'Java',
                                pkgname + '.xml')
        tree = ElementTree.parse(xmlfile)
        package_infos = PackageInfos.from_xml(tree.getroot())

        # This is copied from SUDS
        pkg_signature = 'Java#%s' % pkgname
        pkg_version = '1'
        reg = get_module_registry()
        if pkg_signature in reg.packages:
            reg.remove_package(reg.packages[pkg_signature])
        package_id = reg.idScope.getNewId(Package.vtType)
        package = Package(id=package_id,
                          load_configuration=False,
                          name='Java#' + pkgname,
                          identifier=pkg_signature,
                          version='1')
        java_package = reg.get_package_by_name(identifiers.identifier)
        package._module = java_package.module
        package._init_module = java_package.init_module
        self.package = package
        reg.add_package(package)
        reg.signals.emit_new_package(pkg_signature)
        #
        package.prefix = ''
        package.codepath = 'java'

        try:
            creator = ModuleCreator(package_infos, pkg_signature, pkg_version)
            creator.create_all_modules()
        except:
            self.disable()
            raise

    def disable(self):
        reg = get_module_registry()
        reg.remove_package(self.package)


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
