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

from version import SearchCompiler
from visual import VisualQuery

class CombinedSearch(VisualQuery):
    def __init__(self, search_str=None, pipeline=None, versions_to_check=None):
        VisualQuery.__init__(self, pipeline, versions_to_check)
        self.search_str = search_str

    def run(self, vistrail, name):
        VisualQuery.run(self, vistrail, name)
        self.search_stmt = SearchCompiler(self.search_str).searchStmt

    def match(self, vistrail, action):
        if self.queryPipeline is not None and \
                len(self.queryPipeline.modules) > 0:
            if action.timestep in self.versionDict:
                return self.search_stmt.match(vistrail, action)
            return False
        else:
            return self.search_stmt.match(vistrail, action)

    def matchModule(self, version_id, module):
        if self.queryPipeline is not None and \
                len(self.queryPipeline.modules) > 0:
            return VisualQuery.matchModule(self, version_id, module)
        return True

