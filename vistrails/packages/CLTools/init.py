###############################################################################
##
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
import os
import sys
import json
import tempfile
import subprocess

import core.system
import core.modules.module_registry
from core import debug
from core.modules.vistrails_module import Module, ModuleError, \
    ModuleConnector, NotCacheable, new_module
from core.modules.basic_modules import File
from core.modules.module_utils import FilePool
from cStringIO import StringIO

cl_tools = {}
_file_pool = FilePool()



class CLTools(Module):
    """ CLTools is the base Module.
     We will create a SUDSWebService Module for each method published by 
     the web service.

    """
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        raise core.modules.vistrails_module.IncompleteImplementation

SUFFIX = '.conf'

def add_tool(path):
    # first create classes
    tool_name = os.path.basename(path)
    if not tool_name.endswith(SUFFIX):
        return
    (tool_name, _) = os.path.splitext(tool_name)

    if tool_name in cl_tools:
        core.debug.critical("CLTool already added: %s" % tool_name)
    try:
        conf = json.load(open(path))
    except ValueError as exc:
        core.debug.critical("Could not read CLTool %s" % path, str(exc))
        return
    
    def compute(self):
        """ 1. read inputs
            2. call with inputs
            3. set outputs
        """
        # add all arguments as an unordered list
        args = [self.conf['command']]
        stdin = None
        stdout = None
        setOutput = [] # (name, File) - read string from File and set as output for name
        open_files = []
        kwargs = {}
        for type, name, klass, options in self.conf['args']:
            if "flag" == type:
                args.append(name)
            elif "input" == type:
                if not self.hasInputFromPort(name):
                    continue
                values = self.getInputFromPort(name)
                if 'list' not in options:
                    values = [values]
                for value in values:
                    if "File" == klass:
                        value = str(value.name)
                    # check for flag and append file name
                    if 'flag' in options:
                        args.append(options['flag'])
                    if 'prefix' in options:
                        value = options['prefix'] + str(value)
                    args.append(value)
            elif "output" == type:
                # output must be a filename but we may convert the result to a string
                # create new file
                file = _file_pool.create_file(suffix='.cltoolsfile')
                fname = file.name
                if 'prefix' in options:
                    fname = options['prefix'] + fname
                if 'flag' in options:
                    args.append(options['flag'])
                args.append(fname)
                if "File" == klass:
                    self.setResult(name, file)
                else: # assume String - set to string value after execution
                    setOutput.append((name, file))
        if "stdin" in self.conf:
            name, type = self.conf["stdin"]
            if self.hasInputFromPort(name):
                value = self.getInputFromPort(name)
                if "File" == type:
                    f = open(value.name, 'rb')
                else: # assume String - create temporary file
                    file = _file_pool.create_file(suffix='.cltoolsfile')
                    f = open(file.name, 'w')
                    f.write(str(value))
                    f.close()
                    f = open(file.name)
                open_files.append(f)
                kwargs['stdin'] = f.fileno()
        if "stdout" in self.conf:
            name, type = self.conf["stdout"]
            file = _file_pool.create_file(suffix='.cltoolsfile')
            if "File" == type:
                self.setResult(name, file)
            else: # assume String - set to string value after execution
                setOutput.append((name, file))
            f = open(file.name, 'wb')
            open_files.append(f)
            kwargs['stdout'] = f.fileno()
        if "stderr" in self.conf:
            name, type = self.conf["stderr"]
            file = _file_pool.create_file(suffix='.cltoolsfile')
            if "File" == type:
                self.setResult(name, file)
            else: # assume String - set to string value after execution
                setOutput.append((name, file))
            f = open(file.name, 'wb')
            open_files.append(f)
            kwargs['stderr'] = f.fileno()
            
        print "calling", args
        retcode = subprocess.call(args, **kwargs)
        print "retcode:", retcode

        for f in open_files:
            f.close()

        for name, file in setOutput:
            f = open(file.name)
            self.setResult(name, f.read())
            f.close()

    # create docstring
    d = """This module is a wrapper for the command line tool '%s'""" % \
        conf['command']
    # create module
    M = new_module(CLTools, tool_name,{"compute": compute,
                                           "conf": conf,
                                           "tool_name": tool_name,
                                           "__doc__": d})
    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(M)

    def to_vt_type(s):
        # add recognized types here - default to String
        if "File" == str(s):
            return '(edu.utah.sci.vistrails.basic:File)'
        return '(edu.utah.sci.vistrails.basic:String)'

    # add module ports
    if "stdin" in conf:
        name, type = conf["stdin"]
        reg.add_input_port(M, name, to_vt_type(type))
    if "stdout" in conf:
        name, type = conf["stdout"]
        reg.add_output_port(M, name, to_vt_type(type))
    if "stderr" in conf:
        name, type = conf["stderr"]
        reg.add_output_port(M, name, to_vt_type(type))
    for type, name, klass, options in conf['args']:
        if "input" == type:
            klass = to_vt_type(klass)
            if 'list' in options:
                klass = '(edu.utah.sci.vistrails.basic:List)'
            reg.add_input_port(M, name, klass)
        elif "output" == type:
            reg.add_output_port(M, name, to_vt_type(klass))
    cl_tools[tool_name] = M


def initialize(*args, **keywords):
    # make sure CLTools dir exist
    location = os.path.join(core.system.default_dot_vistrails(),
                                     "CLTools")
    if not os.path.isdir(location):
        try:
            debug.log("Creating CLTools directory...")
            os.mkdir(location)
        except:
            debug.critical(
"""Could not create CLTools directory. Make sure
'%s' does not exist and parent directory is writable""" % location)
            sys.exit(1)

    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(CLTools, **{'hide_descriptor':True})
    for path in os.listdir(location):
        if path.endswith(SUFFIX):
            add_tool(os.path.join(location, path))
        
def finalize():
    _file_pool.cleanup()
