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

import docker
import docker.errors
import subprocess
import sys

from vistrails.core.modules.vistrails_module import Module, ModuleError

from . import configuration


def get_docker():
    if configuration.has('machine'):
        p = subprocess.Popen(['docker-machine', 'env', configuration.machine],
                             stdout=subprocess.PIPE)
        out, _ = p.communicate()
        if p.wait() != 0:
            raise EnvironmentError("Error running docker-machine")
        env = {}
        for line in out.splitlines():
            line = line.strip()
            if not line or line[0] == '#':
                continue
            if line[:7] == 'export ':
                line = line[7:]
            k, v = line.split('=')
            if v.startswith('"'):
                if v[-1] == '"':
                    v = v[:-1]
                v = v.replace('\\"', '"').replace('\\\\', '\\')
            env[k] = v
        return docker.from_env(environment=env)
    elif configuration.has('host'):
        return docker.Client(configuration.host)
    else:
        return docker.Client('unix://var/run/docker.sock')


class RunContainer(Module):
    _input_ports = [
        ('image', 'basic:String'),
        ('command', 'basic:List',
         {'optional': True, 'defaults': '["[]"]'}),
        ('assert_zero', 'basic:Boolean',
         {'optional': True, 'defaults': '[True]'}),
        ('combined_stdout', 'basic:Boolean',
         {'optional': True, 'defaults': '[False]'})]
    _output_ports = [
        ('exit_status', 'basic:Integer'),
        ('stdout', 'basic:String'),
        ('stderr', 'basic:String')]

    def compute(self):
        image = self.get_input('image')
        command = self.get_input('command')

        client = get_docker()
        try:
            container = client.create_container(image=image, command=command)
        except docker.errors.NotFound:
            client.pull(image)
            container = client.create_container(image=image, command=command)
        client.start(container=container['Id'])
        for line in client.logs(container=container['Id'], stream=True):
            sys.stderr.write(line)
        ret = client.wait(container=container['Id'])
        if ret == -1 or (ret != 0 and self.get_input('assert_zero')):
            raise ModuleError(self, "Container exited with status %d" % ret)
        if self.get_input('combined_stdout'):
            stdout = client.logs(container=container['Id'],
                                 stdout=True, stderr=True)
            stderr = ''
        else:
            stdout = client.logs(container=container['Id'],
                                 stdout=True, stderr=False)
            stderr = client.logs(container=container['Id'],
                                 stdout=False, stderr=True)
        self.set_output('stdout', stdout)
        self.set_output('stderr', stderr)
        client.remove_container(container=container.get('Id'))


_modules = [RunContainer]
