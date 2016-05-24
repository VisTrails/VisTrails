###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

import errno
import json
import os
import shutil
import subprocess
import sys

from vistrails.core.modules.vistrails_module import Module, ModuleError, IncompleteImplementation, new_module
import vistrails.core.modules.module_registry
from vistrails.core import debug
from vistrails.core.packagemanager import get_package_manager
import vistrails.core.system
from vistrails.core.system import packages_directory, vistrails_root_directory

import identifiers


cl_tools = {}


class CLTools(Module):
    """ CLTools is the base Module.
     We will create a SUDSWebService Module for each method published by 
     the web service.

    """
    def compute(self):
        raise IncompleteImplementation # pragma: no cover


SUFFIX = '.clt'
DEFAULTFILESUFFIX = '.cld'


def _eintr_retry_call(func, *args):
    """Fixes OSErrors and IOErrors

    From: http://code.google.com/p/seascope/source/detail?spec=svn8dbe5e23d41db673727ce90fd338e9a43f8877e8&name=8dbe5e23d41d&r=8dbe5e23d41db673727ce90fd338e9a43f8877e8
    IOError added
    """
    while True:
        try:
            return func(*args)
        except (OSError, IOError), e: # pragma: no cover
            if e.errno == errno.EINTR:
                continue
            raise


def _add_tool(path):
    # first create classes
    tool_name = os.path.basename(path)
    if isinstance(tool_name, unicode):
        tool_name = tool_name.encode('utf-8')
    if not tool_name.endswith(SUFFIX): # pragma: no cover
        return
    (tool_name, _) = os.path.splitext(tool_name)

    if tool_name in cl_tools: # pragma: no cover
        debug.critical("Package CLTools already added: '%s'" % tool_name)
    try:
        conf = json.load(open(path))
    except ValueError as exc: # pragma: no cover
        debug.critical("Package CLTools could not parse '%s'" % path, exc)
        return

    def compute(self):
        """ 1. read inputs
            2. call with inputs
            3. set outputs
        """
        # add all arguments as an unordered list
        args = [self.conf['command']]
        file_std = 'options' in self.conf and 'std_using_files' in self.conf['options']
        fail_with_cmd = 'options' in self.conf and 'fail_with_cmd' in self.conf['options']
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
                        args.append('%s%s' % (options.get('prefix', ''), name))
            elif "input" == type:
                # handle multiple inputs
                values = self.force_get_input_list(name)
                if values and 'list' == klass:
                    values = values[0]
                    klass = options['type'].lower() \
                      if 'type' in options else 'string'
                for value in values:
                    if 'flag' == klass:
                        if not value:
                            continue
                        if 'flag' in options and options['flag']:
                            value = options['flag']
                        else:
                            # use name as flag
                            value = name
                    elif klass in ('file', 'directory', 'path'):
                        value = value.name
                    # check for flag and append file name
                    if not 'flag' == klass and 'flag' in options:
                        args.append(options['flag'])
                    value = '%s%s' % (options.get('prefix', ''),
                                      value)
                    args.append(value)
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
                    self.set_output(name, file)
                elif "string" == klass:
                    setOutput.append((name, file))
                else:
                    raise ValueError
            elif "inputoutput" == type:
                # handle single file that is both input and output
                value = self.get_input(name)

                # create copy of infile to operate on
                outfile = self.interpreter.filePool.create_file(
                        suffix=options.get('suffix', DEFAULTFILESUFFIX))
                try:
                    shutil.copyfile(value.name, outfile.name)
                except IOError, e: # pragma: no cover
                    raise ModuleError(self,
                                      "Error copying file '%s': %s" %
                                      (value.name, debug.format_exception(e)))
                value = '%s%s' % (options.get('prefix', ''), outfile.name)
                # check for flag and append file name
                if 'flag' in options:
                    args.append(options['flag'])
                args.append(value)
                self.set_output(name, outfile)
        if "stdin" in self.conf:
            name, type, options = self.conf["stdin"]
            type = type.lower()
            if self.has_input(name):
                value = self.get_input(name)
                if "file" == type:
                    if file_std:
                        f = open(value.name, 'rb')
                    else:
                        f = open(value.name, 'rb')
                        stdin = f.read()
                        f.close()
                elif "string" == type:
                    if file_std:
                        file = self.interpreter.filePool.create_file()
                        f = open(file.name, 'wb')
                        f.write(value)
                        f.close()
                        f = open(file.name, 'rb')
                    else:
                        stdin = value
                else: # pragma: no cover
                    raise ValueError
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
                    self.set_output(name, file)
                elif "string" == type:
                    setOutput.append((name, file))
                else: # pragma: no cover
                    raise ValueError
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
                    self.set_output(name, file)
                elif "string" == type:
                    setOutput.append((name, file))
                else: # pragma: no cover
                    raise ValueError
                f = open(file.name, 'wb')
                open_files.append(f)
                kwargs['stderr'] = f.fileno()
            else:
                kwargs['stderr'] = subprocess.PIPE

        if fail_with_cmd:
            return_code = 0
        else:
            return_code = self.conf.get('return_code', None)

        env = {}
        # 0. add defaults
        # 1. add from configuration
        # 2. add from module env
        # 3. add from env port
        if configuration.check('env'):
            try:
                for var in configuration.env.split(";"):
                    key, value = var.split('=')
                    key = key.strip()
                    value = value.strip()
                    if key:
                        env[key] = value
            except Exception, e: # pragma: no cover
                raise ModuleError(self,
                                  "Error parsing configuration env: %s" % (
                                  debug.format_exception(e)))

        if 'options' in self.conf and 'env' in self.conf['options']:
            try:
                for var in self.conf['options']['env'].split(";"):
                    key, value = var.split('=')
                    key = key.strip()
                    value = value.strip()
                    if key:
                        env[key] = value
            except Exception, e: # pragma: no cover
                raise ModuleError(self,
                                  "Error parsing module env: %s" % (
                                  debug.format_exception(e)))
            
        if 'options' in self.conf and 'env_port' in self.conf['options']:
            for e in self.force_get_input_list('env'):
                try:
                    for var in e.split(';'):
                        if not var:
                            continue
                        key, value = var.split('=')
                        key = key.strip()
                        value = value.strip()
                        if key:
                            env[key] = value
                except Exception, e: # pragma: no cover
                    raise ModuleError(self,
                                      "Error parsing env port: %s" % (
                                      debug.format_exception(e)))

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

        if return_code is not None:
            if process.returncode != return_code:
                raise ModuleError(self, "Command returned %d (!= %d)" % (
                                  process.returncode, return_code))
        self.set_output('return_code', process.returncode)

        for f in open_files:
            f.close()

        for name, file in setOutput:
            f = open(file.name, 'rb')
            self.set_output(name, f.read())
            f.close()

        if not file_std:
            if "stdout" in self.conf:
                name, type, options = self.conf["stdout"]
                type = type.lower()
                if "file" == type:
                    file = self.interpreter.filePool.create_file(
                            suffix=DEFAULTFILESUFFIX)
                    f = open(file.name, 'wb')
                    f.write(stdout)
                    f.close()
                    self.set_output(name, file)
                elif "string" == type:
                    self.set_output(name, stdout)
                else: # pragma: no cover
                    raise ValueError
            if "stderr" in self.conf:
                name, type, options = self.conf["stderr"]
                type = type.lower()
                if "file" == type:
                    file = self.interpreter.filePool.create_file(
                            suffix=DEFAULTFILESUFFIX)
                    f = open(file.name, 'wb')
                    f.write(stderr)
                    f.close()
                    self.set_output(name, file)
                elif "string" == type:
                    self.set_output(name, stderr)
                else: # pragma: no cover
                    raise ValueError


    # create docstring
    d = """This module is a wrapper for the command line tool '%s'""" % \
        conf['command']
    # create module
    M = new_module(CLTools, tool_name, {"compute": compute,
                                        "conf": conf,
                                        "tool_name": tool_name,
                                        "__doc__": d})
    reg = vistrails.core.modules.module_registry.get_module_registry()
    reg.add_module(M, package=identifiers.identifier,
                   package_version=identifiers.version)

    def to_vt_type(s):
        # add recognized types here - default is String
        return '(basic:%s)' % \
          {'file':'File', 'path':'Path', 'directory': 'Directory',
           'flag':'Boolean', 'list':'List',
           'float':'Float','integer':'Integer'
          }.get(s.lower(), 'String')
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
    reg.add_output_port(M, 'return_code', to_vt_type('integer'))
    cl_tools[tool_name] = M


def add_tool(path):
    try:
        _add_tool(path)
    except Exception as exc:  # pragma: no cover
        import traceback
        debug.critical("Package CLTools failed to create module "
           "from '%s': %s" % (path, exc),
           traceback.format_exc())


def initialize(*args, **keywords):
    reload_scripts(initial=True)


def remove_all_scripts():
    reg = vistrails.core.modules.module_registry.get_module_registry()
    for tool_name in cl_tools.keys():
        del cl_tools[tool_name]
        reg.delete_module(identifiers.identifier, tool_name)

def reload_scripts(initial=False, name=None):
    reg = vistrails.core.modules.module_registry.get_module_registry()
    if not initial:
        if name is None:
            remove_all_scripts()
        else:
            del cl_tools[name]
            reg.delete_module(identifiers.identifier, name)

    if "CLTools" == identifiers.name:
        # this is the original package
        location = os.path.join(vistrails.core.system.current_dot_vistrails(),
                                "CLTools")
        # make sure dir exist
        if not os.path.isdir(location): # pragma: no cover # pragma: no branch
            try:
                debug.log("Creating CLTools directory...")
                os.mkdir(location)
            except Exception, e:
                debug.critical("Could not create CLTools directory. Make "
                               "sure '%s' does not exist and parent directory "
                               "is writable" % location,
                               e)
                sys.exit(1)
    else:  # pragma: no cover
        # this is a standalone package so modules are placed in this directory
        location = os.path.dirname(__file__)

    if initial:
        reg.add_module(CLTools, abstract=True)
    if name is None:
        for path in os.listdir(location):
            if path.endswith(SUFFIX):  # pragma: no branch
                add_tool(os.path.join(location, path))
    else:
        path = os.path.join(location, name + SUFFIX)
        if os.path.exists(path):
            add_tool(path)

    if not initial:
        from vistrails.core.interpreter.cached import CachedInterpreter
        CachedInterpreter.clear_package(identifiers.identifier)

        from vistrails.gui.vistrails_window import _app
        _app.invalidate_pipelines()


wizards_list = []

def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.
    
    """
    try:
        from wizard import QCLToolsWizardWindow
    except Exception, e: # pragma: no cover
        if "CLTools" == identifiers.name:
            debug.unexpected_exception(e)
            raise
        else:
            return
    lst = []
    if "CLTools" == identifiers.name: # pragma: no branch
        def open_wizard():
            window = QCLToolsWizardWindow(reload_scripts=reload_scripts)
            wizards_list.append(window)
            window.show()
        lst.append(("Open Wizard", open_wizard))
    lst.append(("Reload All Scripts", reload_scripts))
    return tuple(lst)


def finalize():
    pass


def contextMenuName(name):
    if "CLTools" == name:
        return "Reload All Scripts"
    else:
        return "Reload Script"


def callContextMenu(name):
    if "CLTools" == name:
        reload_scripts()
    else:
        reload_scripts(name=name)


###############################################################################

import unittest
from vistrails.tests.utils import execute, intercept_results


class TestCLTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # first make sure CLTools is loaded
        pm = get_package_manager()
        if 'CLTools' not in pm._package_list: # pragma: no cover # pragma: no branch
            pm.late_enable_package('CLTools')
        remove_all_scripts()
        cls.testdir = os.path.join(packages_directory(), 'CLTools', 'test_files')
        cls._tools = {}
        for name in os.listdir(cls.testdir):
            if not name.endswith(SUFFIX):
                continue
            _add_tool(os.path.join(cls.testdir, name))
            toolname = os.path.splitext(name)[0]
            cls._tools[toolname] = cl_tools[toolname]
        cls._old_dir = os.getcwd()
        os.chdir(vistrails_root_directory())

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._old_dir)
        reload_scripts()

    def do_the_test(self, toolname):
        with intercept_results(
                self._tools[toolname],
                'return_code', 'f_out', 'stdout') as (
                return_code, f_out, stdout):
            self.assertFalse(execute([
                    (toolname, 'org.vistrails.vistrails.cltools', [
                        ('f_in', [('File', self.testdir + '/test_1.cltest')]),
                        ('chars', [('List', '["a", "b", "c"]')]),
                        ('false', [('Boolean', 'False')]),
                        ('true', [('Boolean', 'True')]),
                        ('nb', [('Integer', '42')]),
                        ('stdin', [('String', 'some line\nignored')]),
                    ]),
                ]))
        self.assertEqual(return_code, [0])
        self.assertEqual(f_out, ['ok\nmessage received'])
        self.assertEqual(stdout, ['program output here'])

    def test_with_pipes(self):
        """Without std_using_files: use pipes instead of files.
        """
        self.do_the_test('intern_cltools_1')

    def test_with_files(self):
        """With std_using_files: use files instead of pipes.
        """
        self.do_the_test('intern_cltools_2')
