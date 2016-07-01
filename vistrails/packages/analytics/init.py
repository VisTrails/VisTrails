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
from __future__ import division

from vistrails.core.modules.vistrails_module import Module, ModuleError
import vistrails.core.vistrail.vistrail
import vistrails.core.log.log 
import vistrails.db.services.io


class Vistrail(Module):
    pass

class Log(Module):
    pass

class ReadVistrail(Module):
    _input_ports = [('file', '(basic:File)')]
    _output_ports = [('vistrail','(Vistrail)'),
                     ('log', '(Log)')]

    def read_vistrail(self, fname):
        # open the .vt bundle specified by the filename "fname"
        bundle = vistrails.db.services.io.open_vistrail_bundle_from_zip_xml(fname)[0]

        # access the vistrail from the bundle
        vistrail = bundle.vistrail

        # convert the vistrail from a db object
        vistrails.core.vistrail.vistrail.Vistrail.convert(vistrail)

        return vistrail

    def read_log(self, fname):
        # open the .vt bundle specified by the filename "fname"
        bundle = vistrails.db.services.io.open_vistrail_bundle_from_zip_xml(fname)[0]
       
        # get the log filename
        log_fname = bundle.vistrail.db_log_filename
  
        if log_fname is not None:
            # open the log
            log = vistrails.db.services.io.open_log_from_xml(log_fname, True)

            # convert the log from a db object
            vistrails.core.log.log.Log.convert(log)
            return log
        if log_fname is None:
            # throw error message
            raise ModuleError(self, "No log file accessible")

        return None

    def compute(self):
        fname = self.get_input('file').name
        vistrail = self.read_vistrail(fname)
        self.set_output('vistrail', vistrail)
        fname = self.get_input('file').name
        log = self.read_log(fname)
        self.set_output('log', log)

class CountActions(Module):
    _input_ports = [('vistrail', '(Vistrail)')]
    _output_ports = [('counts', '(basic:Dictionary)')]

    def count_actions(self, vistrail):
    # loop through the actionMap dictionary's (key, value) pairs in
    # sorted order
        Tally={}
        for id, action in sorted(vistrail.actionMap.iteritems()):
            # print action information
            for action in action.operations:
                # look for action(what) in dictionary
                # if not there, create an entry with a sub dictionary containing the vtType
                if action.what not in Tally:
                    Tally[action.what] = {action.vtType : 1}

                # if is there, if subdictionray has the vtType key, update vtType count
                elif Tally.has_key(action.what):
                    if Tally[action.what].has_key(action.vtType):
                        Tally[action.what][action.vtType] += 1
                    else:
                        Tally[action.what] = {action.vtType : 1}

                # if is there, if subdictionary does not have vtType key, create entry
                elif Tally.has_key(action.what) is None:
                    Tally[action.what] = {action.vtType : 1}
        return Tally

    def compute(self):
        vistrail = self.get_input('vistrail')
        Tally = self.count_actions(vistrail)
        self.set_output('counts', Tally)

class CountExecutedWorkflows(Module):
    _input_ports = [('log', '(Log)')]
    _output_ports = [('completed', '(basic:Dictionary)')]
    def count_executed_workflows(self,log):
        users={}
        for workflow_exec in log.workflow_execs:
            if workflow_exec.completed == 1:
                if workflow_exec.user not in users:
                    users[workflow_exec.user] = 1
                else:
                    users[workflow_exec.user] += 1
        return users

    def compute(self):
        log = self.get_input('log')
        users = self.count_executed_workflows(log)
        self.set_output('completed', users)

class TotalDays(Module):
    _input_ports = [('vistrail','(Vistrail)')]
    _output_ports = [('completed','(basic:Dictionary)')]
    def calc_time(self, vistrail):
        time = {}
        totals = {}
        for id,action in sorted(vistrail.actionMap.iteritems()):
            if action.user not in time:
                # action.date is a string representation
                # action.db_date is the real python datetime object
                time[action.user] = [action.db_date]
            else:
                time[action.user].append(action.db_date)

        for user, time_list in time.iteritems():
            max_time = max(time_list)
            min_time = min(time_list)

            # this is a timedelta object
            # http://docs.python.org/library/datetime.html#timedelta-objects
            time_delta = max_time - min_time

            # .days returns the number of days in the time delta
            totals[user] = time_delta.days + 1

        return totals
                
    def compute(self):
        vistrail = self.get_input('vistrail')
        totals = self.calc_time(vistrail)
        self.set_output('completed', totals)

#class TimevsTags(Module):
    #Compare a few workflows to see how long the project took vs. how many tags were made
 #   pass

_modules = [Vistrail, Log, ReadVistrail, CountActions, CountExecutedWorkflows, TotalDays]
