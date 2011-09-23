###############################################################################
##
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

from db.domain import DBMachine

class Machine(DBMachine):
    """ Class that stores info for logging a module execution. """

    def __init__(self, *args, **kwargs):
        DBMachine.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMachine.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = Machine
        return cp

    @staticmethod
    def convert(_machine):
        if _machine.__class__ == Machine:
            return
        _machine.__class__ = Machine

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

    def _get_os(self):
        return self.db_os
    def _set_os(self, os):
        self.db_os = os
    os = property(_get_os, _set_os)

    def _get_architecture(self):
        return self.db_architecture
    def _set_architecture(self, architecture):
        self.db_architecture = architecture
    architecture = property(_get_architecture, _set_architecture)

    def _get_processor(self):
        return self.db_processor
    def _set_processor(self, processor):
        self.db_processor = processor
    processor = property(_get_processor, _set_processor)

    def _get_ram(self):
        return self.db_ram
    def _set_ram(self, ram):
        self.db_ram = ram
    ram = property(_get_ram, _set_ram)

    ##########################################################################
    # Properties

    def equals_no_id(self, other):
        return (self.name == other.name and
                self.os == other.os and
                self.architecture == other.architecture and
                self.processor == other.processor and
                self.ram == other.ram)
