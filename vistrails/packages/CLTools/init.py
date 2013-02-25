###############################################################################
##
## Copyright (C) 2011-2012, NYU-Poly.
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
import subprocess
import errno
import shutil

import core.system
import core.modules.module_registry
from core import debug
from core.modules.vistrails_module import Module, ModuleError, new_module

cl_tools = {}

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
DEFAULTFILESUFFIX = '.cld'

def _eintr_retry_call(func, *args):
    # Fixes OSErrors and IOErrors
    #From: http://code.google.com/p/seascope/source/detail?spec=svn8dbe5e23d41db673727ce90fd338e9a43f8877e8&name=8dbe5e23d41d&r=8dbe5e23d41db673727ce90fd338e9a43f8877e8
    # IOError added
    while True:
        try:
            return func(*args)
        except (OSError, IOError), e:
            if e.errno == errno.EINTR:
                continue
            raise

def add_tool(path):
    global cl_tools
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
                flag = 'flag' in options and options['flag']
                if flag:
                    args.append(flag)
                if name:
                    # if flag==name we assume user tried to name a constant
                    if not name == flag:
                        if 'prefix' in options:
                            name = options['prefix'] + str(name)
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
                        if value and 'flag' in options and options['flag']:
                            value = options['flag']
                        else:
                            # use name as flag
                            value = name
                    elif 'file' == klass:
                        value = str(value.name)
                    # check for flag and append file name
                    if not 'flag' == klass and 'flag' in options:
                        args.append(options['flag'])
                    if 'prefix' in options:
                        value = options['prefix'] + str(value)
                    args.append(str(value))
            elif "output" == type:
                # output must be a filename but we may convert the result to a string
                # create new file
                file = self.interpreter.filePool.create_file(
                              suffix=options.get('suffix', DEFAULTFILESUFFIX))
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
            elif "inputoutput" == type:
                # handle single file that is both input and output
                values = self.forceGetInputListFromPort(name)
                for value in values:
                    # create copy of infile to operate on
                    outfile = self.interpreter.filePool.create_file(
                              suffix=options.get('suffix', DEFAULTFILESUFFIX))
                    try:
                        shutil.copyfile(value.name, outfile.name)
                    except IOError, e:
                        raise ModuleError("Error copying file '%s': %s" %
                                          (value.name, str(e)))
                    value = str(outfile.name)
                    # check for flag and append file name
                    if 'flag' in options:
                        args.append(options['flag'])
                    if 'prefix' in options:
                        value = options['prefix'] + str(value)
                    args.append(str(value))
                    self.setResult(name, outfile)
                    # only process one input
                    break
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
                        file = self.interpreter.filePool.create_file()
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
                file = self.interpreter.filePool.create_file(
                                                     suffix=DEFAULTFILESUFFIX)
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
                file = self.interpreter.filePool.create_file(
                                                     suffix=DEFAULTFILESUFFIX)
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
            
        env = {}
        # 0. add defaults
        # 1. add from configuration
        # 2. add from module env
        # 3. add from env port
        if configuration.check('env'):
            try:
                for var in configuration.env.split(";"):
                    key, value = str(var).split('=')
                    key = key.strip()
                    value = value.strip()
                    if key:
                        env[key] = value
            except Exception, e:
                raise ModuleError('Error parsing configuration env: %s' % str(e))

        if 'options' in self.conf and 'env' in self.conf['options']:
            try:
                for var in self.conf['options']['env'].split(";"):
                    key, value = str(var).split('=')
                    key = key.strip()
                    value = value.strip()
                    if key:
                        env[key] = value
            except Exception, e:
                raise ModuleError('Error parsing module env: %s' % str(e))
            
        if 'options' in self.conf and 'env_port' in self.conf['options']:
            for e in self.forceGetInputListFromPort('env'):
                try:
                    for var in e.split(';'):
                        if not var:
                            continue
                        key, value = str(var).split('=')
                        key = key.strip()
                        value = value.strip()
                        if key:
                            env[key] = value
                except Exception, e:
                    raise ModuleError('Error parsing env port: %s' % str(e))

        if env:
            kwargs['env'] = dict(os.environ)
            kwargs['env'].update(env)
            # write to execution provenance
            env = ';'.join(['%s=%s'%(k,v) for k,v in env.iteritems()])
            self.annotate({'execution_env': env})

        if 'dir' in self.conf:
            kwargs['cwd'] = self.conf['dir']

        process = subprocess.Popen(args, **kwargs)
        if file_std:
            process.wait()
        else:
            #if stdin:
            #    print "stdin:", len(stdin), stdin[:30]
            stdout, stderr = _eintr_retry_call(process.communicate, stdin)
            #stdout, stderr = process.communicate(stdin)
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
                    file = self.interpreter.filePool.create_file(
                                                     suffix=DEFAULTFILESUFFIX)
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
                    file = self.interpreter.filePool.create_file(
                                                     suffix=DEFAULTFILESUFFIX)
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
    reg.add_module(M, package=identifier, package_version=version)

    def to_vt_type(s):
        # add recognized types here - default is String
        return '(edu.utah.sci.vistrails.basic:%s)' % \
          {'file':'File', 'flag':'Boolean', 'list':'List',
           'float':'Float','integer':'Integer'
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
    if 'options' in conf and 'env_port' in conf['options']:
        reg.add_input_port(M, 'env', to_vt_type('string'))
    for type, name, klass, options in conf['args']:
        optional = 'required' not in options
        if 'input' == type.lower():
            reg.add_input_port(M, name, to_vt_type(klass), optional=optional)
        elif 'output' == type.lower():
            reg.add_output_port(M, name, to_vt_type(klass), optional=optional)
        elif 'inputoutput' == type.lower():
            reg.add_input_port(M, name, to_vt_type('file'), optional=optional)
            reg.add_output_port(M, name, to_vt_type('file'), optional=optional)
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
    reg.add_module(CLTools, abstract=True)
    for path in os.listdir(location):
        if path.endswith(SUFFIX):
            try:
                add_tool(os.path.join(location, path))
            except Exception as exc:
                import traceback
                debug.critical("Package CLTools failed to create module "
                   "from '%s': %s" % (os.path.join(location, path), str(exc)),
                   traceback.format_exc())

def reload_scripts():
    global cl_tools

    reg = core.modules.module_registry.get_module_registry()
    for tool_name in cl_tools.keys():
        del cl_tools[tool_name]
        reg.delete_module(identifier, tool_name)
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
    
    for path in os.listdir(location):
        if path.endswith(SUFFIX):
            try:
                add_tool(os.path.join(location, path))
            except Exception as exc:
                import traceback
                debug.critical("Package CLTools failed to create module "
                   "from '%s': %s" % (os.path.join(location, path), str(exc)),
                   traceback.format_exc())

    from gui.vistrails_window import _app
    _app.invalidate_pipelines()

wizards_list = []

def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.
    
    """
    # if wizard.py does not exist, assume it is a standalone package and abort
    try:
        from wizard import QCLToolsWizardWindow
    except:
        return
    lst = []
    if "CLTools" == name:
        def open_wizard():
            window = QCLToolsWizardWindow(reload_scripts=reload_scripts)
            wizards_list.append(window)
            window.show()
        lst.append(("Open Wizard", open_wizard))
    lst.append(("Reload All Scripts", reload_scripts))
    return tuple(lst)
        
def finalize():
    pass
