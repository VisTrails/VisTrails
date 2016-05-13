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

from __future__ import division

from auto_gen import DBRegistry as _DBRegistry, DBPackage, DBModuleDescriptor, \
    DBPortSpec
from id_scope import IdScope

class DBRegistry(_DBRegistry):
    def __init__(self, *args, **kwargs):
        _DBRegistry.__init__(self, *args, **kwargs)
        self.idScope = IdScope()

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBRegistry()
        new_obj = _DBRegistry.update_version(old_obj, trans_dict, new_obj)
        new_obj.update_id_scope()
        return new_obj
    
    def update_id_scope(self):
        for package in self.db_packages:
            self.idScope.updateBeginId(DBPackage.vtType, package.db_id+1)
            for descriptor in package.db_module_descriptors:
                self.idScope.updateBeginId(DBModuleDescriptor.vtType,
                                           descriptor.db_id+1)
                for port_spec in descriptor.db_portSpecs:
                    self.idScope.updateBeginId(DBPortSpec.vtType, 
                                               port_spec.db_id+1)


