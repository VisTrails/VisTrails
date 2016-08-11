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

"""Testing package for Job Submission"""

##############################################################################
import time
from vistrails.core.modules.vistrails_module import Module
from vistrails.core.vistrail.job import JobMixin
from vistrails.core.modules.config import IPort, OPort

identifier = 'org.vistrails.vistrails.myjobs'
version = '0.1.0'
name = 'My Jobs'


class TimedJobMonitor(object):
    """ Example that will complete when the specified time have passed

    """
    def __init__(self, start_time, how_long=10):
        self.start_time = start_time
        self.how_long = how_long

    def finished(self):
        print time.time(), self.start_time, self.how_long
        return (time.time()-self.start_time) > self.how_long


class TimedJob(JobMixin, Module):
    """ A module that suspends until 'how_long' seconds have passed

    """
    _input_ports = [IPort("how_long", "basic:Integer", default=10)]
    _output_ports = [OPort("finished", "basic:Boolean")]

    def job_read_inputs(self):
        """ Implemented by modules to read job parameters from input ports.

        Returns the `params` dictionary used by subsequent methods.
        """
        return {'how_long': self.force_get_input('how_long') or 10}

    def job_start(self, params):
        """ Implemented by modules to submit the job.

        Gets the `params` dictionary and returns a new dictionary, for example
        with additional info necessary to check the status later.
        """

        # this example gets the current time and stores it
        # this time represents the information necessary to check the status of the job

        params['start_time'] = time.time()
        return params

    def job_finish(self, params):
        """ Implemented by modules to get info from the finished job.

        This is called once the job is finished to get the results. These can
        be added to the `params` dictionary that this method returns.

        This is the right place to clean up the job from the server if they are
        not supposed to persist.
        """
        return params

    def job_set_results(self, params):
        """ Implemented by modules to set the output ports.

        This is called after job_finished() or after getting the cached results
        to set the output ports on this module, from the `params` dictionary.
        """
        self.set_output('finished', True)

    def job_get_handle(self, params):
        """ Implemented by modules to return the JobHandle object.

        This returns an object following the JobHandle interface. The
        JobMonitor will use it to check the status of the job and call back
        this module once the job is done.

        JobHandle needs the following method:
          * finished(): returns True if the job is finished
        """
        return TimedJobMonitor(params['start_time'], params['how_long'])


class SuspendNJobMonitor(object):
    """ Example that will complete the n-th  time it is checked

    """
    def __init__(self, module, params):
        """ Store job params so that n can be updated in job info
        """
        self.module = module
        self.params = params

    def finished(self):
        if self.params['n'] == 0:
            return True
        else:
            self.params['n'] -= 1
            return False


class SuspendNJob(JobMixin, Module):
    """ A module that suspends until it has been checked 'n' times

    """
    _input_ports = [IPort("n", "basic:Integer", default=1)]
    _output_ports = [OPort("finished", "basic:Boolean")]

    def job_read_inputs(self):
        """ Implemented by modules to read job parameters from input ports.

        Returns the `params` dictionary used by subsequent methods.
        """
        return {'n': self.force_get_input('n') or 1}

    def job_start(self, params):
        """ Implemented by modules to submit the job.

        Gets the `params` dictionary and returns a new dictionary, for example
        with additional info necessary to check the status later.
        """

        # this example does not need to be started since it only uses an input as initial job state
        return params

    def job_finish(self, params):
        """ Implemented by modules to get info from the finished job.

        This is called once the job is finished to get the results. These can
        be added to the `params` dictionary that this method returns.

        This is the right place to clean up the job from the server if they are
        not supposed to persist.
        """
        return params

    def job_set_results(self, params):
        """ Implemented by modules to set the output ports.

        This is called after job_finished() or after getting the cached results
        to set the output ports on this module, from the `params` dictionary.
        """
        self.set_output('finished', True)

    def job_get_handle(self, params):
        """ Implemented by modules to return the JobHandle object.

        This returns an object following the JobHandle interface. The
        JobMonitor will use it to check the status of the job and call back
        this module once the job is done.

        JobHandle needs the following method:
          * finished(): returns True if the job is finished
        """
        return SuspendNJobMonitor(self, params)

_modules = [TimedJob, SuspendNJob]
