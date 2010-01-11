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

