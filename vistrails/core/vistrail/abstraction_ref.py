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

from db.domain import DBAbstractionRef

class AbstractionRef(DBAbstractionRef):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAbstractionRef.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        
    def __copy__(self):
        cp = DBAbstractionRef.__copy__(self)
        cp.__class__ = AbstractionRef
        return cp

    @staticmethod
    def convert(_abstraction_ref):
        _abstraction_ref.__class__ = AbstractionRef

    ##########################################################################
    # Properties

    def _get_id(self):
        return self.db_id
    def _set_id(self, id):
        self.db_id = id
    id = property(_get_id, _set_id)

    def _get_abstraction_id(self):
        return self.db_abstraction_id
    def _set_abstraction_id(self, id):
        self.db_abstraction_id = id
    abstraction_id = property(_get_abstraction_id, _set_abstraction_id)

    def _get_version(self):
        return self.db_version
    def _set_version(self, version):
        self.db_version = version
    version = property(_get_version, _set_version)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an 
        AbstractionRef object. 

        """
        rep = '<abstraction_ref id="%s"/>'
        return  rep % (str(self.id))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: AbstractionRef) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

