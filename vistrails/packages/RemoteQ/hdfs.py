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
""" Wrapper for Hadoop DFS operations """

from __future__ import division

import os
import shutil

from vistrails.core.modules.basic_modules import File, Boolean, String, \
                                                 PathObject, Path
from vistrails.core.modules.config import IPort, OPort, ModuleSettings
from vistrails.core.modules.vistrails_module import ModuleError
from base import HadoopBaseModule


################################################################################
class HDFSPut(HadoopBaseModule):
    """
    Putting a local file to the Hadoop DFS
    First copying it to the server
    """
    _settings = ModuleSettings(namespace='hadoop')
    _input_ports = [IPort('Local File', File),
                    IPort('Remote Location', String),
                    IPort('Override', Boolean),
                    IPort('Machine', '(org.vistrails.vistrails.remoteq:Machine)')]

    _output_ports = [OPort('Machine', '(org.vistrails.vistrails.remoteq:Machine)'),
                     OPort('Remote Location', String)]

    def __init__(self):
        HadoopBaseModule.__init__(self)

    def compute(self):
        machine = self.get_machine()
        jm = self.job_monitor()
        id = self.signature
        job = jm.getCache(id)
        if not job:
            remote = self.get_input('Remote Location')
            local = self.get_input('Local File')
            override = self.force_get_input('Override', False)
            if '://' not in remote:
                remote = self.add_prefix(remote, machine)
            if not int(self.call_hdfs('dfs -test -e ' + remote +
                                      '; echo $?', machine)):
                if override:
                    self.call_hdfs('dfs -rm -r ' + remote, machine)
                else:
                    raise ModuleError(self, 'Remote entry already exists')
            tempfile = machine.remote.send_command('mktemp -u').strip()
            result = machine.sendfile(local.name, tempfile)
            self.call_hdfs('dfs -put %s %s' % (tempfile, remote), machine)
            result = machine.remote.rm(tempfile,force=True,recursively=True)
            d = {'remote':remote,'local':local.name}
            self.set_job_machine(d, machine)
            jm.setCache(id, d, self.job_name())
            job = jm.getJob(id)
        self.set_output('Remote Location', job.parameters['remote'])
        self.set_output('Machine', machine)

################################################################################
class HDFSGet(HadoopBaseModule):
    """
    Getting a file from the Hadoop DFS
    Then getting it from the server
    
    """
    _settings = ModuleSettings(namespace='hadoop')
    _input_ports = [IPort('Local File', Path),
                    IPort('Remote Location', String),
                    IPort('Override', Boolean),
                    IPort('Machine', '(org.vistrails.vistrails.remoteq:Machine)')]

    _output_ports = [OPort('Machine', '(org.vistrails.vistrails.remoteq:Machine)'),
                     OPort('Local File', File)]


    def __init__(self):
        HadoopBaseModule.__init__(self)

    def compute(self):
        machine = self.get_machine()
        jm = self.job_monitor()
        id = self.signature
        job = jm.getCache(id)
        if not job:
            remote = self.get_input('Remote Location')
            local = self.get_input('Local File')
            override = self.force_get_input('Override', False)
            if '://' not in remote:
                remote = self.add_prefix(remote, machine)
            if os.path.exists(local.name):
                if override==False:
                    raise ModuleError(self, 'Output already exists')
                else:
                    if os.path.isdir(local.name):
                        shutil.rmtree(local.name)
                    else:
                        os.unlink(local.name)

            tempfile = machine.remote.send_command('mktemp -d -u').strip()
            result = self.call_hdfs('dfs -get %s %s' % (remote, tempfile), machine)
            # too slow with many files
            #res = machine.send_command("get -r %s %s" % (tempfile, local.name) )
            # tar files to increase speed
            result = machine.local.send_command('mkdir %s'%local.name)
            result = machine.sync(local.name,
                                  tempfile,
                                  mode=machine.MODE_REMOTE_LOCAL,
                                  use_tar=True)
            result = machine.remote.rm(tempfile,force=True,recursively=True)
            d = {'remote':remote,'local':local.name}
            self.set_job_machine(d, machine)
            jm.setCache(id, d, self.job_name())
            job = jm.getCache(id)
        self.set_output('Local File', PathObject(job.parameters['local']))
        self.set_output('Machine', machine)

################################################################################
class HDFSEnsureNew(HadoopBaseModule):
    """
    Make sure the file is removed
    
    """
    _settings = ModuleSettings(namespace='hadoop')
    _input_ports = [IPort('Name', String),
                    IPort('Machine', '(org.vistrails.vistrails.remoteq:Machine)')]

    _output_ports = [OPort('Machine', '(org.vistrails.vistrails.remoteq:Machine)'),
                     OPort('Name', String)]

    def __init__(self):
        HadoopBaseModule.__init__(self)

    def compute(self):
        machine = self.get_machine()
        jm = self.job_monitor()
        id = self.signature
        job = jm.getCache(id)
        if not job:
            entry_name = self.get_input('Name')
            if '://' not in entry_name:
                entry_name = self.add_prefix(entry_name, machine)
            if not int(self.call_hdfs('dfs -test -e ' + entry_name +
                                      '; echo $?', machine)):
                #self.call_hdfs('dfs -rm -r ' + entry_name, machine)
                # we are using -rmr but it is deprecated
                self.call_hdfs('dfs -rmr ' + entry_name, machine)
            d = {'entry_name':entry_name}
            self.set_job_machine(d, machine)
            jm.setCache(id, d, self.job_name())
            job = jm.getCache(id)
        self.set_output('Name', job.parameters['entry_name'])
        self.set_output('Machine', machine)

################################################################################
def register():
    return [HDFSPut, HDFSGet, HDFSEnsureNew]
