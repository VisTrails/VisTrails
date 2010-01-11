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

from xml.auto_gen import XMLDAOListBase
import xml.io

class DAOList(dict):
    def __init__(self):
        self['xml'] = XMLDAOListBase()

    def open_from_xml(self, filename, vtType, tree=None):
        return xml.io.open_from_xml(filename, vtType, self['xml'])

    def save_to_xml(self, obj, filename):
        xml.io.save_to_xml(obj, filename, self['xml'])

    def serialize(self, obj):
        return xml.io.serialize(obj, self['xml'])

    def unserialize(self, str, type):
        return xml.io.unserialize(str, type, self['xml'])
