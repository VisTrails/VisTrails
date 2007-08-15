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

from db.domain import DBAbstraction

class Abstraction(DBAbstraction):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAbstraction.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        
    def __copy__(self):
        cp = DBAbstraction.__copy__(self)
        cp.__class__ = Abstraction
        return cp

    @staticmethod
    def convert(_abstraction):
        _abstraction.__class__ = Abstraction

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

    # FIXME don't allow set access?
    def _get_actions(self):
        return self.db_actions
    def _set_actions(self, actions):
        self.db_actions = actions
    actions = property(_get_actions, _set_actions)
    def add_action(self, action, parent):
        Action.convert(action)
        if action.id < 0:
            action.id = self.idScope.getNewId(action.vtType)
        action.prevId = parent
        action.date = self.getDate()
        action.user = self.getUser()
        for op in action.operations:
            if op.id < 0:
                op.id = self.idScope.getNewId('operation')
        self.addVersion(action)                

    def _get_tags(self):
        return self.db_tags
    def _set_tags(self, tags):
        self.db_tags = tags
    tags = property(_get_tags, _set_tags)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Abstraction
        object. 

        """
        rep = '<abstraction id="%s"/>'
        return  rep % (str(self.id))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: Abstraction) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
