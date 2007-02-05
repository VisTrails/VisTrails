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
""" Module used when running  vistrails uninteractively """
from core import xml_parser
import core.interpreter.default
from core.utils import VistrailsInternalError

################################################################################

class DummyView(object):
    def setModuleActive(self, id):
        pass

    def setModuleComputing(self, id):
        pass
    
    def setModuleSuccess(self, id):
        pass
    
    def setModuleError(self, id, error):
        pass
    
def run(input, workflow):
    """run(input: str, workflow: int or str) -> boolean 
    Run the workflow 'workflow' in the 'input' file and generates 
    Returns False in case of error. workflow can be a tag name or a version.

    """ 
    parser = xml_parser.XMLParser()
    parser.openVistrail(input)
    v = parser.getVistrail()
    if type(workflow) == type("str"):
        version = v.tagMap[workflow]
    elif type(workflow) == type(1):
        version = workflow
    else:
        msg = "Invalid version tag or number"
        raise VistrailsInternalError(msg)
    parser.closeVistrail()
    pip = v.getPipeline(workflow)

    error = False
    view = DummyView()
    interpreter = core.interpreter.default.default_interpreter.get()
    (objs, errors, executed) = interpreter.execute(pip,
                                                   input,
                                                   version,
                                                   view,
                                                   None)
    for obj in objs.itervalues():
        i = obj.id
        if errors.has_key(i):
            error = True
    if error:
        return False
    else:
        return True

def cleanup():
    core.interpreter.cached.CachedInterpreter.cleanup()

################################################################################
#Testing

import unittest
import core.system

class TestConsoleMode(unittest.TestCase):
    def test1(self):
        result = run(core.system.visTrailsRootDirectory() +
            '/tests/resources/dummy.xml',"int chain")
        self.assertEquals(result, True)
    def tearDown(self):
        cleanup()
if __name__ == '__main__':
    unittest.main()
