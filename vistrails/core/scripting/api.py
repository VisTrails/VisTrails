###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
""" This file exposes an api for calling modules as functions in scripts
"""

from __future__ import division

from vistrails.core.api import initialize, do_enable_package, NoSuchPackage
from vistrails.core.modules.basic_modules import create_constant
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.vistrails_module import ModuleConnector
from vistrails.core.packagemanager import get_package_manager


class ModuleFunction(object):
    """Wrapper for a module that can be executed as a function
    """
    def __init__(self, descriptor):
        self.descriptor = descriptor

    def __call__(self, outputs, **kwargs):
        """ executes a module directly

            outputs: A string or list with name(s) of outputs to set
        """
        if isinstance(outputs, basestring):
            outputs = (outputs,)
        instance = self.descriptor.module()
        for port in kwargs:
            mc = ModuleConnector(create_constant(kwargs[port]), 'value')
            instance.set_input_port(port, mc)
        for port in outputs:
            instance.enable_output_port(port)
        instance.compute()
        result = [instance.get_output(port) for port in outputs]
        return result[0] if len(result)==1 else result


class ModuleNamespace(object):
    def __init__(self, identifier, namespace=''):
        self.identifier = identifier
        self._namespace = namespace
        self._namespaces = {}

    def __getattr__(self, name):
        if name in self._namespaces:
            return self._namespaces[name]
        else:
            return self[name]

    def __getitem__(self, name):
        name = name.rsplit('|', 1)
        if len(name) == 2:
            if self._namespace:
                namespace = self._namespace + '|' + name[0]
            else:
                namespace = name[0]
            name = name[1]
        else:
            name, = name
            namespace = self._namespace
        reg = get_module_registry()
        descr = reg.get_descriptor_by_name(self.identifier,
                                           name,
                                           namespace)
        # todo return executable object here
        return ModuleFunction(descr)

    def __repr__(self):
        return "<Namespace %s of package %s>" % (self._namespace,
                                                 self.identifier)


class Package(ModuleNamespace):
    """Wrapper for an enabled package.

    You can get modules as executable functions using either the
    ``pkg['namespace|module']`` or ``pkg.namespace.module`` syntax.
    """
    def __init__(self, identifier):
        """Gets a package by identifier, enabling it if necessary.
        """
        initialize()
        pm = get_package_manager()
        pkg = pm.identifier_is_available(identifier)
        self._package = pkg
        # Copied from VistrailController#try_to_enable_package()
        dep_graph = pm.build_dependency_graph([identifier])
        deps = pm.get_ordered_dependencies(dep_graph)
        for pkg_id in deps:
            if not do_enable_package(pm, pkg_id):
                raise NoSuchPackage("Package %r not found" % pkg_id)
        self.identifier = identifier
        ModuleNamespace.__init__(self, pkg.identifier)
        self._namespaces = {}

        # Builds namespaces
        for mod, namespaces in self._package.descriptors.iterkeys():
            if not namespaces:
                continue
            ns = self
            fullname = None
            for name in namespaces.split('|'):
                if fullname is not None:
                    fullname += '|' + name
                else:
                    fullname = name
                if name not in ns._namespaces:
                    ns_ = ns._namespaces[name] = ModuleNamespace(
                            self.identifier,
                            fullname)
                    ns = ns_
                else:
                    ns = ns._namespaces[name]

