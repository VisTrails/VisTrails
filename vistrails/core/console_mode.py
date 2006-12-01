""" Module used when running  vistrails uninteractively """
from core import xml_parser
from core import interpreter
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
    pip.resolveAliases()
    (objs, errors, executed) = interpreter.Interpreter().execute(pip,
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

################################################################################
#Testing

import unittest
import core.system

class TestConsoleMode(unittest.TestCase):
    def test1(self):
        result = run(core.system.visTrailsRootDirectory() +
            '/tests/resources/dummy.xml',"int chain")
        self.assertEquals(result, True)

if __name__ == '__main__':
    unittest.main()
