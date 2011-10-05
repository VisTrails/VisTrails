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
## THIS SOFTWARE IS PROVIDED B Y THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
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
import time

import core.system
import core.modules.module_registry
from core import debug
from core.modules.vistrails_module import Module, ModuleError, new_module
from core.modules.basic_modules import File
from core.modules.module_utils import FilePool

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

SUFFIX = '.clt'
TEMPSUFFIX = '.cltoolsfile'

def add_tool(path):
    # first create classes
    tool_name = os.path.basename(path)
    if not tool_name.endswith(SUFFIX):
        return
    (tool_name, _) = os.path.splitext(tool_name)

    if tool_name in cl_tools:
        debug.critical("Package CLTools already added: '%s'" % tool_name)
    try:
        conf = json.load(open(path))
    except ValueError as exc:
        debug.critical("Package CLTools could not parse '%s'" % path, str(exc))
        return
    def compute(self):
        """ 1. read inputs
            2. call with inputs
            3. set outputs
        """
        # add all arguments as an unordered list
        args = [self.conf['command']]
        file_std = 'options' in self.conf and 'std_using_files' in self.conf['options']
        setOutput = [] # (name, File) - set File contents as output for name
        open_files = []
        stdin = None
        kwargs = {}
        for type, name, klass, options in self.conf['args']:
            type = type.lower()
            klass = klass.lower()
            if "constant" == type:
                args.append(name)
            elif "input" == type:
                # handle multiple inputs
                values = self.forceGetInputListFromPort(name)
                if values and 'list' == klass:
                    values = values[0]
                    klass = options['type'].lower() \
                      if 'type' in options else 'string'
                for value in values:
                    if 'flag' == klass:
                        if value and 'flag' in options:
                            value = options['flag']
                        else:
                            continue
                    elif 'file' == klass:
                        value = str(value.name)
                    # check for flag and append file name
                    if not 'flag' == klass and 'flag' in options:
                        args.append(options['flag'])
                    if 'prefix' in options:
                        value = options['prefix'] + str(value)
                    args.append(value)
            elif "output" == type:
                # output must be a filename but we may convert the result to a string
                # create new file
                file = _file_pool.create_file(suffix=TEMPSUFFIX)
                fname = file.name
                if 'prefix' in options:
                    fname = options['prefix'] + fname
                if 'flag' in options:
                    args.append(options['flag'])
                args.append(fname)
                if "file" == klass:
                    self.setResult(name, file)
                else: # assume String - set to string value after execution
                    setOutput.append((name, file))
        if "stdin" in self.conf:
            name, type, options = self.conf["stdin"]
            type = type.lower()
            if self.hasInputFromPort(name):
                value = self.getInputFromPort(name)
                if "file" == type:
                    if file_std:
                        f = open(value.name, 'rb')
                        data = f.read()
                        stdin = ''
                        while data:
                            stdin += data
                            data = f.read()
                        f.close()
                    else:
                        f = open(value.name, 'rb')
                else: # assume String
                    if file_std:
                        file = _file_pool.create_file(suffix=TEMPSUFFIX)
                        f = open(file.name, 'w')
                        f.write(str(value))
                        f.close()
                        f = open(file.name)
                    else:
                        stdin = value
                if file_std:
                    open_files.append(f)
                    kwargs['stdin'] = f.fileno()
                else:
                    kwargs['stdin'] = subprocess.PIPE
        if "stdout" in self.conf:
            if file_std:
                name, type, options = self.conf["stdout"]
                type = type.lower()
                file = _file_pool.create_file(suffix=TEMPSUFFIX)
                if "file" == type:
                    self.setResult(name, file)
                else: # assume String - set to string value after execution
                    setOutput.append((name, file))
                f = open(file.name, 'wb')
                open_files.append(f)
                kwargs['stdout'] = f.fileno()
            else:
                kwargs['stdout'] = subprocess.PIPE
        if "stderr" in self.conf:
            if file_std:
                name, type, options = self.conf["stderr"]
                type = type.lower()
                file = _file_pool.create_file(suffix=TEMPSUFFIX)
                if "file" == type:
                    self.setResult(name, file)
                else: # assume String - set to string value after execution
                    setOutput.append((name, file))
                f = open(file.name, 'wb')
                open_files.append(f)
                kwargs['stderr'] = f.fileno()
            else:
                kwargs['stderr'] = subprocess.PIPE
        # On windows, builtin commands like cd/dir must use shell=True
        if core.system.systemType in ['Windows', 'Microsoft'] and \
                          args[0] in ['dir', 'cd']:
            kwargs['shell'] = True   
            
        #print "calling", args, kwargs
        process = subprocess.Popen(args, **kwargs)
        if file_std:
            process.wait()
        else:
            #if stdin:
            #    print "stdin:", len(stdin), stdin[:30]
            stdout, stderr = process.communicate(stdin)
            #if stdout:
            #    print "stdout:", len(stdout), stdout[:30]
            #if stderr:
            #    print "stderr:", len(stderr), stderr[:30]

        for f in open_files:
            f.close()

        for name, file in setOutput:
            f = open(file.name)
            self.setResult(name, f.read())
            f.close()

        if not file_std:
            if stdout and "stdout" in self.conf:
                name, type, options = self.conf["stdout"]
                type = type.lower()
                if "file" == type:
                    file = _file_pool.create_file(suffix=TEMPSUFFIX)
                    f = open(file.name, 'w')
                    f.write(stdout)
                    f.close()
                    self.setResult(name, file)
                else: # assume String - set to string value after execution
                    self.setResult(name, stdout)
            if stderr and "stderr" in self.conf:
                name, type, options = self.conf["stderr"]
                type = type.lower()
                if "file" == type:
                    file = _file_pool.create_file(suffix=TEMPSUFFIX)
                    f = open(file.name, 'w')
                    f.write(stderr)
                    f.close()
                    self.setResult(name, file)
                else: # assume String - set to string value after execution
                    self.setResult(name, stderr)


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
        # add recognized types here - default is String
        return '(edu.utah.sci.vistrails.basic:%s)' % \
          {'file':'File', 'flag':'Boolean', 'list':'List'
          }.get(str(s).lower(), 'String')
    # add module ports
    if 'stdin' in conf:
        name, type, options = conf['stdin']
        optional = 'required' not in options
        reg.add_input_port(M, name, to_vt_type(type), optional=optional)
    if 'stdout' in conf:
        name, type, options = conf['stdout']
        optional = 'required' not in options
        reg.add_output_port(M, name, to_vt_type(type), optional=optional)
    if 'stderr' in conf:
        name, type, options = conf['stderr']
        optional = 'required' not in options
        reg.add_output_port(M, name, to_vt_type(type), optional=optional)
    for type, name, klass, options in conf['args']:
        optional = 'required' not in options
        if 'input' == type.lower():
            reg.add_input_port(M, name, to_vt_type(klass), optional=optional)
        elif 'output' == type.lower():
            reg.add_output_port(M, name, to_vt_type(klass), optional=optional)
    cl_tools[tool_name] = M


def initialize(*args, **keywords):
    if "CLTools" == name:
        # this is the original package 
        location = os.path.join(core.system.default_dot_vistrails(),
                                     "CLTools")
        # make sure dir exist
        if not os.path.isdir(location):
            try:
                debug.log("Creating CLTools directory...")
                os.mkdir(location)
            except:
                debug.critical("""Could not create CLTools directory. Make
 sure '%s' does not exist and parent directory is writable""" % location)
                sys.exit(1)
    else:
        # this is a standalone package so modules are placed in this directory
        location = os.path.dirname(__file__)
    

    reg = core.modules.module_registry.get_module_registry()
    reg.add_module(CLTools, **{'hide_descriptor':True})
    for path in os.listdir(location):
        if path.endswith(SUFFIX):
            try:
                add_tool(os.path.join(location, path))
            except Exception as exc:
                import traceback
                debug.critical("Package CLTools failed to create module "
                   "from '%s': %s" % (os.path.join(location, path), str(exc)),
                   traceback.format_exc())
                
        
def finalize():
    _file_pool.cleanup()
