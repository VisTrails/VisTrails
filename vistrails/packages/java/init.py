"""Entry point for the Java package.

Here we create the modules for each Java package from the serialized
information we have as XML.
"""

import functools
import hashlib
import imp
import os
import sys

import vistrails
from vistrails.core import debug
from vistrails.core.modules.config import ModuleSettings
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

        # Create Java modules
        try:
            creator = ModuleCreator(package_infos, pkg_signature, pkg_version)
            creator.create_all_modules()
        except:
            self.disable()
            raise

        # Add additional modules
        self.load_additional_code()

    def disable(self):
        reg = get_module_registry()
        reg.remove_package(self.package)

    def load_additional_code(self):
        path = os.path.join(current_dot_vistrails(), 'Java')

        if not (
                os.path.isfile(os.path.join(path, self.pkgname + '.py')) or
                os.path.isfile(os.path.join(path,
                                            self.pkgname, '__init__.py'))):
            return

        debug.debug("Loading additional code for %r" % self.pkgname)

        if 'vistrails.java_additions' not in sys.modules:
            additions = imp.new_module('vistrails.java_additions')
            additions.__path__ = [path]
            sys.modules['vistrails.java_additions'] = additions
            vistrails.java_additions = additions

        name = 'vistrails.java_additions.%s' % self.pkgname
        additional_module = __import__(name, globals(), locals())
        additional_module = getattr(additional_module.java_additions,
                                    self.pkgname)

        from vistrails.core.modules.module_registry import _toposort_modules
        reg = get_module_registry()
        pkg = reg._current_package
        reg._current_package = self.package
        try:
            # Copied from module_registry:ModuleRegistry#initialize_package()
            debug.debug('%s' % hasattr(additional_module, '_modules'))
            if hasattr(additional_module, '_modules'):
                modules = additional_module._modules
                if isinstance(modules, dict):
                    module_list = []
                    for namespace, m_list in modules.iteritems():
                        for module in m_list:
                            m_dict = {'namespace': namespace}
                            if isinstance(module, tuple):
                                m_dict.update(module[1])
                                module_list.append((module[0], m_dict))
                            elif '_settings' in module.__dict__:
                                kwargs = module._settings._asdict()
                                kwargs.update(m_dict)
                                module._settings = ModuleSettings(**kwargs)
                                module_list.append(module)
                            else:
                                module_list.append((module, m_dict))
                else:
                    module_list = modules
                modules = _toposort_modules(module_list)
                # We add all modules before adding ports because
                # modules inside package might use each other as ports
                for module in modules:
                    reg.auto_add_module(module)
            #
        finally:
            reg._current_package = pkg


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
