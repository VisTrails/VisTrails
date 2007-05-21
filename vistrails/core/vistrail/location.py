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

from db.domain import DBLocation

class Location(DBLocation):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBLocation.__init__(self, *args, **kwargs)
        
    def __copy__(self):
        cp = DBLocation.__copy__(self)
        cp.__class__ = Location
        return cp

    ##########################################################################
    # DB Conversion

    @staticmethod
    def convert(_location):
        _location.__class__ = Location

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_x(self):
        return self.db_x
    def _set_x(self, x):
        self.db_x = x
    x = property(_get_x, _set_x)

    def _get_y(self):
        return self.db_y
    def _set_y(self, y):
        self.db_y = y
    y = property(_get_y, _set_y)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        rep = "<location id=%s x=%s y=%s/>"
        return  rep % (str(self.id), str(self.x), str(self.y))

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
    
