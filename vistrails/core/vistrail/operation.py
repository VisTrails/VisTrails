############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

from db.domain import DBAdd, DBChange, DBDelete

class AddOp(DBAdd):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAdd.__init__(self, *args, **kwargs)
    
    def __copy__(self):
        cp = DBAdd.__copy__(self)
        cp.__class__ = AddOp
        return cp

    @staticmethod
    def convert(_add_op):
        _add_op.__class__ = AddOp

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_what(self):
        return self.db_what
    def _set_what(self, what):
        self.db_what = what
    what = property(_get_what, _set_what)

    def _get_objectId(self):
        return self.db_objectId
    def _set_objectId(self, objectId):
        self.db_objectId = objectId
    objectId = property(_get_objectId, _set_objectId)
    
    def _get_parentObjId(self):
        return self.db_parentObjId
    def _set_parentObjId(self, parentObjId):
        self.db_parentObjId = parentObjId
    parentObjId = property(_get_parentObjId, _set_parentObjId)
    
    def _get_parentObjType(self):
        return self.db_parentObjType
    def _set_parentObjType(self, parentObjType):
        self.db_parentObjType = parentObjType
    parentObjType = property(_get_parentObjType, _set_parentObjType)
    
    def _get_data(self):
        return self.db_data
    def _set_data(self, data):
        self.db_data = data
    data = property(_get_data, _set_data)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        rep = "<add id=%s what=%s objectId=%s parentObjId=%s" + \
            "parentObjType=%s>" + data.__str__() + "</add>"
        return rep % (str(self.id), str(self.what), str(self.objectId),
                      str(self.parentObjId), str(self.parentObjType))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: AddOp) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class ChangeOp(DBChange):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBChange.__init__(self, *args, **kwargs)
    
    def __copy__(self):
        cp = DBChange.__copy__(self)
        cp.__class__ = ChangeOp
        return cp

    @staticmethod
    def convert(_change_op):
        _change_op.__class__ = ChangeOp

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_what(self):
        return self.db_what
    def _set_what(self, what):
        self.db_what = what
    what = property(_get_what, _set_what)

    def _get_oldObjId(self):
        return self.db_oldObjId
    def _set_oldObjId(self, oldObjId):
        self.db_oldObjId = oldObjId
    oldObjId = property(_get_oldObjId, _set_oldObjId)

    def _get_newObjId(self):
        return self.db_newObjId
    def _set_newObjId(self, newObjId):
        self.db_newObjId = newObjId
    newObjId = property(_get_newObjId, _set_newObjId)
    
    def _get_parentObjId(self):
        return self.db_parentObjId
    def _set_parentObjId(self, parentObjId):
        self.db_parentObjId = parentObjId
    parentObjId = property(_get_parentObjId, _set_parentObjId)
    
    def _get_parentObjType(self):
        return self.db_parentObjType
    def _set_parentObjType(self, parentObjType):
        self.db_parentObjType = parentObjType
    parentObjType = property(_get_parentObjType, _set_parentObjType)
    
    def _get_data(self):
        return self.db_data
    def _set_data(self, data):
        self.db_data = data
    data = property(_get_data, _set_data)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        rep = "<change id=%s what=%s oldId=%s newId=%s parentObjId=%s" + \
            "parentObjType=%s>" + data.__str__() + "</change>"
        return rep % (str(self.id), str(self.what), str(self.oldObjId),
                      str(self.newObjId), str(self.parentObjId), 
                      str(self.parentObjType))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: ChangeOp) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class DeleteOp(DBDelete):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBDelete.__init__(self, *args, **kwargs)
    
    def __copy__(self):
        cp = DBDelete.__copy__(self)
        cp.__class__ = DeleteOp
        return cp

    @staticmethod
    def convert(_delete_op):
        _delete_op.__class__ = DeleteOp

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_what(self):
        return self.db_what
    def _set_what(self, what):
        self.db_what = what
    what = property(_get_what, _set_what)

    def _get_objectId(self):
        return self.db_objectId
    def _set_objectId(self, objectId):
        self.db_objectId = objectId
    objectId = property(_get_objectId, _set_objectId)
    
    def _get_parentObjId(self):
        return self.db_parentObjId
    def _set_parentObjId(self, parentObjId):
        self.db_parentObjId = parentObjId
    parentObjId = property(_get_parentObjId, _set_parentObjId)
    
    def _get_parentObjType(self):
        return self.db_parentObjType
    def _set_parentObjType(self, parentObjType):
        self.db_parentObjType = parentObjType
    parentObjType = property(_get_parentObjType, _set_parentObjType)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        rep = "<delete id=%s what=%s objectId=%s parentObjId=%s" + \
            "parentObjType=%s/>"
        return rep % (str(self.id), str(self.what), str(self.objectId),
                      str(self.parentObjId), str(self.parentObjType))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: DeleteOp) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
