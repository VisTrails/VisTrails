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
from core.utils import VistrailsInternalError, expression

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
    
def run(input, workflow, parameters=''):
    """run(input: str, workflow: int or str) -> boolean 
    Run the workflow 'workflow' in the 'input' file and generates 
    Returns False in case of error. workflow can be a tag name or a version.

    """ 
    elements = parameters.split(",")
    aliases = {}
    parser = xml_parser.XMLParser()
    parser.openVistrail(input)
    v = parser.getVistrail()
    if type(workflow) == type("str"):
        version = v.tagMap[workflow]
    elif type(workflow) == type(1):
        version = workflow
    else:
        msg = "Invalid version tag or number: %s" % workflow
        raise VistrailsInternalError(msg)
    parser.closeVistrail()
    pip = v.getPipeline(workflow)
    for e in elements:
        pos = e.find("=")
        if pos != -1:
            key = e[:pos].strip()
            value = e[pos+1:].strip()
            
            if pip.hasAlias(key):
                ptype = pip.aliases[key][0]
                aliases[key] = (ptype,expression.parseExpression(value))
    error = False
    view = DummyView()
    interpreter = core.interpreter.default.default_interpreter.get()
    (objs, errors, executed) = interpreter.execute(pip,
                                                   input,
                                                   version,
                                                   view,
                                                   aliases)
    for i in objs.iterkeys():
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

import core.packagemanager
import core.system
import sys
import unittest
import core.vistrail

class TestConsoleMode(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        manager = core.packagemanager.get_package_manager()
        if manager.has_package('console_mode_test'):
            return
        old_path = sys.path
        sys.path.append(core.system.visTrailsRootDirectory() +
                        '/tests/resources')
        m = __import__('console_mode_test')
        sys.path = old_path
        d = {'console_mode_test': m}
        manager.add_package('console_mode_test')
        manager.initialize_packages(d)

    def test1(self):
        result = run(core.system.visTrailsRootDirectory() +
                     '/tests/resources/dummy.xml',"int chain")
        self.assertEquals(result, True)

    def test_tuple(self):
        interpreter = core.interpreter.default.default_interpreter.get()
        v = DummyView()
        p = core.vistrail.pipeline.Pipeline()
        shm = core.vistrail.pipeline.shorthand_module
        p.addModule(shm('TestTupleExecution', 0,
                        [('input', [('Float', '2.0'), ('Float', '2.0')])]))
        interpreter.execute(p, 'foo', 1, v, None)

    def test_python_source(self):
        result = run(core.system.visTrailsRootDirectory() +
                     '/tests/resources/pythonsource.xml',"testPortsAndFail")
        self.assertEquals(result, True)

    def test_dynamic_module_error(self):
        result = run(core.system.visTrailsRootDirectory() + 
                     '/tests/resources/dynamic_module_error.xml',"test")
        self.assertEquals(result, False)

if __name__ == '__main__':
    unittest.main()
