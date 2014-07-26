###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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
import os
import re
from itertools import chain

from vistrails.core import debug
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.sub_module import read_vistrail, new_abstraction, \
    get_abstraction_dependencies, save_abstraction
import vistrails.core.modules.module_registry
from vistrails.core.system import vistrails_version, get_vistrails_directory
from vistrails.core.utils import InvalidPipeline

name = 'My SubWorkflows'
version = '1.6'
identifier = 'local.abstractions'

my_vistrails = {}

def initialize(*args, **kwargs):
    import vistrails.core.packagemanager
    manager = vistrails.core.packagemanager.get_package_manager()

    reg = vistrails.core.modules.module_registry.get_module_registry()
    abs_vistrails = my_vistrails
    last_count = len(my_vistrails) + 1

    missing_depends = {}
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
                        cannot_load[abs_name] = (abs_vistrail, "Missing package dependency: %s" % package)
                        break
                else:
                    for descriptor_info in inter_depends:
                        if not reg.has_descriptor_with_name(*descriptor_info):
                            add_abstraction = False
                            new_vistrails[abs_name] = abs_info
                            missing_depends[abs_name] = "Missing module '%s:%s'"\
                                                        % (descriptor_info[0],
                                                           descriptor_info[1])
                            break
            if add_abstraction:
                abstraction = None
                try:
                    abstraction = \
                        new_abstraction(abs_name, abs_vistrail, abs_fname)
                except InvalidPipeline, e:
                    # handle_invalid_pipeline will raise it's own InvalidPipeline
                    # exception if it fails
                    try:
                        import vistrails.core.vistrail.controller
                        module_version = abs_vistrail.get_latest_version()
                        # Use a "dummy" controller to handle the upgrade
                        controller = vistrails.core.vistrail.controller.VistrailController(abs_vistrail)
                        (new_version, new_pipeline) = \
                            controller.handle_invalid_pipeline(e, long(module_version), 
                                                               abs_vistrail, False, True)
                        del controller
                        save_abstraction(abs_vistrail, abs_fname)
                        abstraction = new_abstraction(abs_name, abs_vistrail, abs_fname,
                                                      new_version, new_pipeline)
                    except Exception, _e:
                        cannot_load[abs_name] = (abs_vistrail, _e)
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
        debug.critical("Cannot load subworkflow '%s'" % abs_name)
        if e:
            debug.critical("- %s" % e)
    for abs_name in abs_vistrails:
        if abs_name in missing_depends:
            debug.critical("Cannot load subworkflow '%s'" % abs_name,
                           missing_depends[abs_name])
        else:
            debug.critical("Cannot load subworkflow '%s'" % abs_name)

def package_dependencies():
    import vistrails.core.packagemanager
    manager = vistrails.core.packagemanager.get_package_manager()

    reg = vistrails.core.modules.module_registry.get_module_registry()
    conf = get_vistrails_configuration()

    abstraction_dir = get_vistrails_directory("subworkflowsDir")
    if abstraction_dir is None:
        debug.log("Subworkflows directory unset, cannot add any abstractions")
        return []
    p = re.compile(r".*\.xml")
    all_packages = set()
    for abstraction in os.listdir(abstraction_dir):
        if p.match(abstraction):
            abs_fname = os.path.join(abstraction_dir, abstraction)
            try:
                vistrail = read_vistrail(abs_fname)
                dependencies = get_abstraction_dependencies(vistrail)
            except vistrails.core.modules.module_registry.MissingPackage, e:
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
                my_vistrails[abstraction[:-4]] = \
                    (vistrail, abs_fname, inter_depends)
            else:
                debug.critical(("Subworkflow '%s' is missing packages it " +
                                "depends on") % abstraction)
    # print 'all_packages:', all_packages
    return list(all_packages)
