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

from db.domain import DBAnnotation

class Annotation(DBAnnotation):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAnnotation.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        
    def __copy__(self):
        cp = DBAnnotation.__copy__(self)
        cp.__class__ = Annotation
        return cp

    @staticmethod
    def convert(_annotation):
        _annotation.__class__ = Annotation

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_key(self):
        return self.db_key
    def _set_key(self, key):
        self.db_key = key
    key = property(_get_key, _set_key)

    def _get_value(self):
        return self.db_value
    def _set_value(self, value):
        self.db_value = value
    value = property(_get_value, _set_value)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        rep = "<annotation id=%s key=%s value=%s</annotation>"
        return  rep % (str(self.id), str(self.key), str(self.value))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: Annotation) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
