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
""" Base classes for all Hadoop Modules """

from __future__ import division

from init import configuration
from vistrails.core.modules.basic_modules import File, String
from vistrails.gui.modules.python_source_configure import \
                                                PythonSourceConfigurationWidget
from vistrails.core.modules.config import ModuleSettings, IPort, OPort
from vistrails.core.modules.vistrails_module import Module, NotCacheable, \
                                                   ModuleError, ModuleSuspended
from remoteq.core.stack import select_machine, end_machine, use_machine, \
                                                                current_machine
from remoteq.batch.commandline import Subshell
from remoteq.batch.directories import CreateDirectory
import urllib
import xml.etree.cElementTree as ET

from init import RQModule

################################################################################
class HadoopBaseModule(RQModule):
    """
    The base class for all modules in the Hadoop package. We would
    like to implement a few basic functionality such as looking for
    Hadoop installation directory, execute Hadoop commands, etc. for
    subclasses to use
    
    """
    _settings = ModuleSettings(abstract=True)

    hadoop_configuration = None
    def __init__(self):
        Module.__init__(self)
    
    def get_hadoop_home(self, machine):
        HADOOP_HOME = machine.remote.send_command("echo $HADOOP_HOME").strip()
        if HADOOP_HOME == '':
            # raise ModuleError(self, 'HADOOP_HOME has to be defined')
            # it does not actually. This means it is part of the system.
            pass
        return HADOOP_HOME

    def read_site_config(self, machine):
        config = HadoopBaseModule.hadoop_configuration
        # For AWS
        core_site = config['home']+'/conf/core-site.xml'
        # for NYU/CUSP
        #core_site = config['home']+'/etc/hadoop/conf/core-site.xml'
        site_string = machine.remote.cat(core_site)
        root = ET.fromstring(site_string)
        for node in root:
            name = node.find('name').text
            value = node.find('value').text
            config[name] = value

    def get_hadoop_config(self, machine):
        if HadoopBaseModule.hadoop_configuration==None:
            hadoop_home = self.get_hadoop_home(machine)
            # paths to try in order
            streaming_paths = ['/share/hadoop/tools/lib/',   # AWS
                               '/usr/lib/hadoop-mapreduce/', # NYU/CUSP
                               '/contrib/streaming/']
            for path in streaming_paths:
                hs = hadoop_home + path
                command = ("python -c \"import os, os.path; print '' if not "
                           "os.path.exists('{0}') else ''.join([i for i in "
                           "os.listdir('{0}') if 'streaming' in i][-1:])\""
                           ).format(hs)
                streamingjar = machine.remote.send_command(command).strip()
                if streamingjar:
                    break
            if not streamingjar:
                raise ModuleError(self,
                                  'hadoop-streaming.jar not found. Please add '
                                  'its directory to list of supported paths.')
            hadoop = (hadoop_home + '/bin/hadoop') if hadoop_home else 'hadoop'
            hdfs = (hadoop_home + '/bin/hdfs') if hadoop_home else 'hdfs'
            if not machine.remote.command_exists(hdfs):
                hdfs = hadoop
            config = {'home': hadoop_home,
                      'hadoop': hadoop,
                      'hdfs': hdfs,
                      'streaming.jar': hs + streamingjar}
            HadoopBaseModule.hadoop_configuration = config
            # reading configuration files are error-prone
            #self.read_site_config(machine)
            config['fs.defaultFS'] = ''
            # can access config only if hdfs command exists
            if hadoop != hdfs:
                config['fs.defaultFS'] = \
                    self.call_hdfs('getconf -confKey fs.defaultFS', machine)
        return HadoopBaseModule.hadoop_configuration

    def add_prefix(self, path, machine): 
        aliases = []
        if configuration.check('uris') and configuration.uris:
            aliases = dict([(uri.split('#')[1], uri.split('#')[0])
                            for uri in configuration.uris.split(';')])
        if path in aliases:
            return aliases[path]
        if configuration.check('defaultFS'):
            prefix = configuration.defaultFS
            return prefix + path
        else:
            prefix = self.get_hadoop_config(machine)['fs.defaultFS']
            return prefix + '/' + path


    def call_hadoop(self, arguments, workdir, identifier, machine):
        self.is_cacheable = lambda *args, **kwargs: False
        config = self.get_hadoop_config(machine)
        argList = [config['hadoop']]
        if type(arguments) in [str, unicode]:
            argList += arguments.split(' ')
        elif type(arguments)==list:
            argList += arguments
        else:
            raise ModuleError(self, 'Invalid argument types to hadoop')

        # 1. this version returns when finished
        #return subprocess.call(argList)
        # 2. this version reads the results incrementally
#         expect = machine.remote._expect_token
#         machine.remote.push_expect(None) # Do not wait for call to finish
#         result =  machine.remote.send_command(" ".join(argList)).strip()
#         machine.remote.pop_expect() # restore expect
#         # We could show the output in a gui
#         print "**** hadoop streaming running ****"
#         print result,
#         while not expect in result:
#             output = machine.remote.consume_output()
#             if output:
#                 print output,
#             result += output
        # 3. The final version should detach the process on the server
        use_machine(machine)
        cdir = CreateDirectory("remote", workdir)
        job = Subshell("remote", command=" ".join(argList),
                       working_directory=workdir, identifier=identifier,
                       dependencies=[cdir])
        job.run()
        finished = job.finished()
        if not finished:
            status = job.status()
            # The Subshell class provides the JobHandle interface, i.e.
            # finished()
            raise ModuleSuspended(self, '%s' % status, handle=job)
        self.is_cacheable = lambda *args, **kwargs: True
        return job.standard_error()

    def call_hdfs(self, arguments, machine):
        config = self.get_hadoop_config(machine)
        argList = [config['hdfs']]
        if type(arguments) in [str, unicode]:
            argList += arguments.split(' ')
        elif type(arguments)==list:
            argList += arguments
        else:
            raise ModuleError(self, 'Invalid argument types to hdfs: %s'%type(arguments))

        result =  machine.remote.send_command(" ".join(argList)).strip()
        return result
        #return subprocess.call(argList)

################################################################################
class PythonSourceToFileConfigurationWidget(PythonSourceConfigurationWidget):
    """
    A simple python source configuration widget, i.e. hiding all of
    the input/output port table
    
    """
    def __init__(self, module, controller, parent=None):
        PythonSourceConfigurationWidget.__init__(self, module,
                                                 controller, parent)
        self.inputPortTable.hide()
        self.outputPortTable.hide()
        self.setWindowTitle('Python Source Editor')

################################################################################
class PythonSourceToFile(Module):
    """
    This is the class for specifying a python code snippet for running
    with Hadoop Streaming, it will take its contents and output to a
    temporary Python file. The code will not be passed around.
    
    """
    _settings = ModuleSettings(namespace='hadoop',
                        configure_widget=PythonSourceToFileConfigurationWidget)

    _input_ports = [IPort('Input File', File),
                    IPort('source', String, optional=True)]

    _output_ports = [OPort('Temporary File', File)]

    def compute(self):
        inputFile = self.force_get_input('Input File')

        if inputFile!=None:
#            tempFile = file_pool.make_local_copy(inputFile.name)
            tempFile = inputFile
        else:
            source = urllib.unquote(self.force_get_input('source', ''))
            tempFile = self.interpreter.filePool.create_file()
            f = open(tempFile.name, 'w')
            f.write(source)
            f.close()
        self.set_output('Temporary File', tempFile)
            

################################################################################
def register():
    return [HadoopBaseModule, PythonSourceToFile]
    
