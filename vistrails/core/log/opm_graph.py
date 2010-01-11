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

from db.domain import DBOpmGraph

class OpmGraph(DBOpmGraph):
    """ Class that stores info for generating OPM Provenance. """

    def __init__(self, *args, **kwargs):
        if 'log' in kwargs:
            self.log = kwargs['log']
            del kwargs['log']
        else:
            self.log = None
        if 'workflow' in kwargs:
            self.workflow = kwargs['workflow']
            del kwargs['workflow']
        elif 'pipeline' in kwargs:
            self.workflow = kwargs['pipeline']
            del kwargs['pipeline']
        else:
            self.workflow = None
        if 'registry' in kwargs:
            self.registry = kwargs['registry']
            del kwargs['registry']
        else:
            self.registry = None
        if 'version' in kwargs:
            self.version = kwargs['version']
            del kwargs['version']
        else:
            self.version = None
        DBOpmGraph.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self):
        cp = DBOpmGraph.__copy__(self)
        cp.__class__ = OpmGraph
        cp.log = self.log
        cp.workflow = self.workflow
        cp.version = self.version
        cp.registry = self.registry
        return cp

    @staticmethod
    def convert(_graph):
        if _graph.__class__ == OpmGraph:
            return
        _graph.__class__ = OpmGraph

    ##########################################################################
    # Properties

    # No need to do properties right now...

