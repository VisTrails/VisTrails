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

from db.domain import DBTag

class Tag(DBTag):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBTag.__init__(self, *args, **kwargs)
        
    def __copy__(self):
        cp = DBTag.__copy__(self)
        cp.__class__ = Tag
        return cp

    @staticmethod
    def convert(_tag):
        _tag.__class__ = Tag
    
    ##########################################################################
    # Properties

    def _get_name(self):
        return self.db_name
    def _set_name(self, name):
        self.db_name = name
    name = property(_get_name, _set_name)

    def _get_time(self):
        return self.db_time
    def _set_time(self, time):
        self.db_time = time
    time = property(_get_time, _set_time)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of a Tag
        object. 

        """
        rep = "<tag name=%s time=%s />"
        return  rep % (str(self.name), str(self.time))

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
