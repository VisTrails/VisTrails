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

from db.domain import DBPluginData

class PluginData(DBPluginData):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBPluginData.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        
    def __copy__(self):
        return PluginData.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPluginData.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = PluginData
        return cp

    ##########################################################################
    # DB Conversion

    @staticmethod
    def convert(_plugin_data):
        _plugin_data.__class__ = PluginData

    ##########################################################################
    # Properties

    id = DBPluginData.db_id
    data = DBPluginData.db_data

    ##########################################################################
    # Operators

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.data == other.data

################################################################################
# Testing

import unittest
import copy
import random
from db.domain import IdScope

class TestPluginData(unittest.TestCase):

    def create_data(self, id=1, data=""):
        return PluginData(id=id, data=data)

    def test_create(self):
        self.create_data(2, "testing the data field")

    def test_serialization(self):
        import core.db.io
        p_data1 = self.create_data()
        xml_str = core.db.io.serialize(p_data1)
        p_data2 = core.db.io.unserialize(xml_str, PluginData)
        self.assertEquals(p_data1, p_data2)
        self.assertEquals(p_data1.id, p_data2.id)

