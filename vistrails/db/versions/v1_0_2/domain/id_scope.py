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

import copy

class IdScope:
    def __init__(self, beginId=0L, remap=None):
        self.ids = {}
        self.beginId = beginId
        if remap is None:
            self.remap = {}
        else:
            self.remap = remap

    def __copy__(self):
        cp = IdScope(beginId=self.beginId)
        cp.ids = copy.copy(self.ids)
        cp.remap = copy.copy(self.remap)
        return cp

    def __str__(self):
        return str(self.ids)

    def getNewId(self, objType):
        try:
            objType = self.remap[objType]
        except KeyError:
            pass
        try:
            id = self.ids[objType]
            self.ids[objType] += 1
            return id
        except KeyError:
            self.ids[objType] = self.beginId + 1
            return self.beginId

    def updateBeginId(self, objType, beginId):
        try:
            objType = self.remap[objType]
        except KeyError:
            pass
        try:
            if self.ids[objType] <= beginId:
                self.ids[objType] = beginId
        except KeyError:
            self.ids[objType] = beginId
        
    def setBeginId(self, objType, beginId):
        try:
            objType = self.remap[objType]
        except KeyError:
            pass
        self.ids[objType] = beginId
