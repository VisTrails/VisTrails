############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

import os
import re
from itertools import chain

from core import debug
from core.configuration import get_vistrails_configuration
from core.modules.vistrails_module import Module, ModuleError
from core.modules.sub_module import read_vistrail, new_abstraction, \
    get_abstraction_dependencies
import core.modules.module_registry
from core.system import vistrails_version

name = 'My SubWorkflows'
version = '1.6'
identifier = 'local.abstractions'

vistrails = {}

def initialize(*args, **kwargs):
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()

    reg = core.modules.module_registry.get_module_registry()
#     conf = get_vistrails_configuration()
#     if conf.check("userPackageDirectory"):
#         if conf.check('userPackageDirectory'):
#             abstraction_dir = os.path.join(conf.userPackageDirectory,
#                                            'abstractions')

#     abs_fnames = []
#     p = re.compile(r".*\.vt")
#     for abstraction in os.listdir(abstraction_dir):
#         if p.match(abstraction):
#             abs_fnames.append(os.path.join(abstraction_dir, abstraction))
    abs_vistrails = vistrails
    last_count = len(vistrails) + 1

    cannot_load = {}
    while len(abs_vistrails) > 0 and len(abs_vistrails) < last_count:
        new_vistrails = {}
        for (abs_name, abs_info) in abs_vistrails.iteritems():
            (abs_vistrail, abs_fname, abs_depends) = abs_info
            packages = get_abstraction_dependencies(abs_vistrail)
            add_abstraction = True
            for package, inter_depends in packages.iteritems():
                if package != identifier:
                    if not manager.has_package(package):
                        add_abstraction = False
                        cannot_load[abs_name] = abs_vistrail
                        break
                else:
                    for descriptor_info in inter_depends:
                        if not reg.has_descriptor_with_name(*descriptor_info):
                            add_abstraction = False
                            new_vistrails[abs_name] = abs_info
                            break
            if add_abstraction:
                abstraction = None
                try:
                    abstraction = \
                        new_abstraction(abs_name, abs_vistrail, abs_fname)
                except Exception, e:
                    cannot_load[abs_name] = (abs_vistrail, e)
                if abstraction is not None:
                    options = {'namespace': abstraction.uuid,
                               'hide_namespace': True,
                               'version': str(abstraction.internal_version)}
                    reg.auto_add_module((abstraction, options))
                    reg.auto_add_ports(abstraction)
                    # print "Added subworkflow", abs_name, abstraction.uuid
                elif abs_name not in cannot_load:
                    cannot_load[abs_name] = (abs_vistrail, '')
        last_count = len(abs_vistrails)
        abs_vistrails = new_vistrails

    for abs_name, (_, e) in cannot_load.iteritems():
        debug.critical("Cannot load abstraction '%s'" % abs_name)
        if e:
            debug.critical("- %s" % e)
    for abs_name in abs_vistrails:
        debug.critical("Cannot load abstraction '%s'" % abs_name)

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()

    reg = core.modules.module_registry.get_module_registry()
    conf = get_vistrails_configuration()
    if conf.check("abstractionsDirectory"):
        abstraction_dir = conf.abstractionsDirectory
    p = re.compile(r".*\.xml")
    all_packages = set()
    for abstraction in os.listdir(abstraction_dir):
        if p.match(abstraction):
            abs_fname = os.path.join(abstraction_dir, abstraction)
            try:
                vistrail = read_vistrail(abs_fname)
                dependencies = get_abstraction_dependencies(vistrail)
            except core.modules.module_registry.MissingPackage, e:
                dependencies = {e._identifier: set()}
            add_abstraction = True
            inter_depends = []
            for package, depends in dependencies.iteritems():
                if package != identifier:
                    if not manager.has_package(package):
                        add_abstraction = False
                        break
                else:
                    inter_depends.append(depends)
            if add_abstraction:
                # print 'adding', abstraction[:-4]
                all_packages.update(p for p in dependencies.iterkeys()
                                    if p != identifier)
                vistrails[abstraction[:-4]] = \
                    (vistrail, abs_fname, inter_depends)
            else:
                debug.critical(("Abstraction '%s' is missing packages it " +
                                "depends on") % abstraction)
    # print 'all_packages:', all_packages
    return list(all_packages)
