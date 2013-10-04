###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
""" Contains classes for persisting running executions to disk
    
"""

#from vistrails.core import debug, configuration

from uuid import uuid1

import datetime
import getpass
import json
import unittest

_running_workflows = dict()
_current_workflow = None

def start_job(workflow):
    """ start_job(workflow: Workflow) -> None
    
    """
    global _current_workflow
    _current_workflow = workflow

def finish_job():
    """ finish_job() -> None
    
        Finishes the running workflow
    """
    global _current_workflow
    _current_workflow = None

def add_job(id, params, finished=False):
    """ add_job(id: str, params: dict) -> uuid
    
        Adds a module to the current running workflow
    """
    if not _current_workflow:
        raise Exception("No workflow running!")
    _current_workflow.modules[id] = Module(id, params, finished)

def get_job(id):
    """ get_job(id: str) -> Module
    
        Checks if a module exists using its id and returns it
    """
    if not _current_workflow:
        raise Exception("No workflow running!")
    return _current_workflow.modules.get(id, None)
    pass

class Workflow:
    """ Represents a running workflow
        Modules can register their state
        It can be saved to disk
    """
    def __init__(self, vistrail, version, id=None, user=None, start=None,
                 modules=[]):
        """ __init__(vistrail: str, version: str/int, id: str, user: str,
                     start: str, modules: list) -> None

            vistrail - the vistrail url
            version - workflow version
            id - persistent identifier
            user - who started the job
            start - start time
            finished - is it finished or running?
        
        """
        self.vistrail = vistrail
        self.version = version
        self.id = id if id else str(uuid1())
        self.user = getpass.getuser()
        self.start = start if start else str(datetime.datetime.now())
        self.modules = modules if modules else {}
        wf = dict()

    def to_dict(self):
        wf = dict()
        wf['vistrail'] = self.vistrail
        wf['version'] = self.version
        wf['id'] = self.id
        wf['user'] = self.user
        wf['start'] = self.start
        modules = dict()
        for module in self.modules.itervalues():
            modules[module.id] = module.to_dict()
        wf['modules'] = modules
        return wf

    @staticmethod
    def from_dict(wf):
        modules = {}
        for id, module in wf['modules'].iteritems():
            modules[id] = Module.from_dict(module)
        return Workflow(wf['vistrail'], wf['version'], wf['id'], wf['user'],
                        wf['start'], modules)

    def __eq__(self, other):
        if self.vistrail != other.vistrail: return False
        if self.version != other.version: return False
        if self.id != other.id: return False
        if self.user != other.user: return False
        if self.start != other.start: return False
        if len(self.modules) != len(other.modules): return False
        if self.modules != other.modules: return False
        return True

class Module:
    """ Represents a running module
        
    """
    def __init__(self, id, parameters, start=None, finished=False):
        """ __init__(id: str, parameters: dict, start: str, finished: bool)

            id - persistent identifier
            parameters - either output values or job parameters
            start - start time
            finished - is it finished or running?
        
        """
        self.id = id
        self.parameters = parameters
        self.start = start if start else str(datetime.datetime.now())
        self.finished = finished

    def to_dict(self):
        m = dict()
        m['id'] = self.id
        m['parameters'] = self.parameters
        m['start'] = self.start
        m['finished'] = self.finished
        return m

    @staticmethod
    def from_dict(m):
        return Module(m['id'], m['parameters'], m['start'], m['finished'])

    def __eq__(self, other):
        if self.id != other.id: return False
        if self.parameters != other.parameters: return False
        if self.start != other.start: return False
        if self.finished != other.finished: return False
        return True
        
def __serialize__():
    jobs = dict()
    for id, workflow in _running_workflows.items():
        jobs[id] = workflow.to_dict()
    return json.dumps(jobs)

def __unserialize__(s):
    global _running_jobs
    jobs = json.loads(s)
    for id, workflow in jobs.iteritems():
        _running_workflows[id] = Workflow.from_dict(workflow)

##############################################################################
# Testing


class TestJob(unittest.TestCase):

    def test_job(self):
        global _running_workflows
        global _current_workflow
        module1 = Module('someid34', {'a':3, 'b':'7'})
        module2 = Module('81', {'a':6}, "a_string_date", True)
        # test module to/from dict
        module3 = Module.from_dict(module2.to_dict())
        self.assertEqual(module2, module3)
        
        workflow1 = Workflow('a.vt', 26)
        workflow2 = Workflow('b.vt', 'tagname', 'myid', 'tommy', "start_time",
                            {module1.id: module1, module2.id: module2})
        # test workflow to/from dict
        workflow3 = Workflow.from_dict(workflow2.to_dict())
        self.assertEqual(workflow2, workflow3)

        # test start/finish job
        start_job(workflow2)
        self.assertEqual(workflow2, _current_workflow)
        finish_job()
        self.assertEqual(None, _current_workflow)
        
        # test serialization
        _running_workflows[workflow1.id] = workflow1
        _running_workflows[workflow2.id] = workflow2
        serialized = __serialize__()
        _running_workflows = dict()
        __unserialize__(serialized)
        self.assertIn(workflow1.id, _running_workflows)
        self.assertIn(workflow2.id, _running_workflows)
        self.assertEqual(workflow1, _running_workflows[workflow1.id])
        self.assertEqual(workflow2, _running_workflows[workflow2.id])
        _running_workflows = dict()

if __name__ == '__main__':
    unittest.main()
