###############################################################################
##
## Copyright (C) 2011-2012, NYU-Poly.
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
"""To use this script, run VisTrails with the old version of a package enabled, and choose the Export -> Registry to XML... and save the file.  Then, enable the new version of the package and again export the registry to a second XML file.  Then, run this script with the package identifier, the old registry's filename, and the new registry's filename as arguments."""

import os
import sys
# put the vistrails code on the python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), "vistrails"))

import core.application
from core.modules.module_registry import ModuleRegistry
from db.services.io import open_registry_from_xml

def get_module_name(d):
    if d.namespace:
        return "%s|%s" % (d.namespace, d.name)
    return d.name

def diff_package(pkg_id, reg_fname1, reg_fname2):
    reg1 = open_registry_from_xml(reg_fname1)
    ModuleRegistry.convert(reg1)
    reg2 = open_registry_from_xml(reg_fname2)
    ModuleRegistry.convert(reg2)
    
    pkg1 = reg1.get_package_by_name(pkg_id)
    pkg2 = reg2.get_package_by_name(pkg_id)

    d2_modules_dict = dict(((d2.identifier, d2.name, d2.namespace), d2)
                           for d2 in pkg2.descriptor_list)
    for d1 in pkg1.descriptor_list:
        if reg2.has_descriptor_with_name(pkg_id, d1.name, d1.namespace):
            d2 = reg2.get_descriptor_by_name(pkg_id, d1.name, d1.namespace)
            d1_port_specs = {}
            for ps in d1.port_specs_list:
                d1_port_specs[(ps.name, ps.type)] = ps.sigstring
            d2_port_specs = {}
            for ps in d2.port_specs_list:
                d2_port_specs[(ps.name, ps.type)] = ps.sigstring
            d2_port_specs_set = set(d2_port_specs.keys())
            for ps_id, sig1 in d1_port_specs.iteritems():
                if ps_id not in d2_port_specs:
                    print "added %s port: %s:%s" % \
                        (ps_id[1], get_module_name(d1), ps_id[0])
                    continue
                d2_port_specs_set.discard(ps_id)
                if sig1 != d2_port_specs[ps_id]:
                    print "changed %s port: %s:%s" % \
                        (ps_id[1], get_module_name(d1), ps_id[0])
                    print "  %s -> %s" % (sig1, d2_port_specs[ps_id])
                else:
                    # equal
                    pass
            for ps_id in d2_port_specs_set:
                print "deleted %s port: %s:%s" % \
                    (ps_id[1], get_module_name(d1), ps_id[0])
            del d2_modules_dict[(d1.identifier, d1.name, d1.namespace)]
        else:
            print "deleted module: %s" % get_module_name(d1)
    for d2 in d2_modules_dict.itervalues():
        print "added module: %s" % get_module_name(d2)
    
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: %s %s <pkg_identifer> <old_registry> <new_registry>" % \
            (sys.executable, sys.argv[0])
        sys.exit(71)
    core.application.init()
    diff_package(*sys.argv[1:])
