############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

from core.modules.basic_modules import new_constant
from core.modules.vistrails_module import Module, ModuleError, ModuleConnector
import core.vistrail.vistrail
import core.log.log 
import db.services.io


class Vistrail(Module):
    pass

class Log(Module):
    pass

class ReadVistrail(Module):
    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)')]
    _output_ports = [('vistrail','(edu.utah.sci.vistrails.analytics:Vistrail)'),
                      ('log', '(edu.utah.sci.vistrails.analytics:Log)')]

    def read_vistrail(self, fname):
        # open the .vt bundle specified by the filename "fname"
        bundle = db.services.io.open_vistrail_bundle_from_zip_xml(fname)[0]

        # access the vistrail from the bundle
        vistrail = bundle.vistrail

        # convert the vistrail from a db object
        core.vistrail.vistrail.Vistrail.convert(vistrail)

        return vistrail

    def read_log(self, fname):
        # open the .vt bundle specified by the filename "fname"
        bundle = db.services.io.open_vistrail_bundle_from_zip_xml(fname)[0]
       
        # get the log filename
        log_fname = bundle.vistrail.db_log_filename
  
        if log_fname is not None:
            # open the log
            log = db.services.io.open_log_from_xml(log_fname, True)

            # convert the log from a db object
            core.log.log.Log.convert(log)
            return log
        if log_fname is None:
            # throw error message
            raise ModuleError(self, "No log file accessible")

        return None

    def compute(self):
        fname = self.getInputFromPort('file').name
        vistrail = self.read_vistrail(fname)
        self.setResult('vistrail', vistrail)
        fname = self.getInputFromPort('file').name
        log = self.read_log(fname)
        self.setResult('log', log)

class CountActions(Module):
    _input_ports = [('vistrail',
                    '(edu.utah.sci.vistrails.analytics:Vistrail)')]
    _output_ports = [('counts',
                    '(edu.utah.sci.vistrails.basic:Dictionary)')]

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
                elif Tally.has_key(action.what) == none:
                    Tally[action.what] = {action.vtType : 1}
        return Tally

    def compute(self):
        vistrail = self.getInputFromPort('vistrail')
        Tally = self.count_actions(vistrail)
        self.setResult('counts', Tally)

class CountExecutedWorkflows(Module):
    _input_ports = [('log',
                    '(edu.utah.sci.vistrails.analytics:Log)')]
    _output_ports = [('completed',
                    '(edu.utah.sci.vistrails.basic:Dictionary)')]
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
        log = self.getInputFromPort('log')
        users = self.count_executed_workflows(log)
        self.setResult('completed', users)

class TotalDays(Module):
    _input_ports = [('vistrail','(edu.utah.sci.vistrails.analytics:Vistrail)')]
    _output_ports = [('completed','(edu.utah.sci.vistrails.basic:Dictionary)')]
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
        vistrail = self.getInputFromPort('vistrail')
        totals = self.calc_time(vistrail)
        self.setResult('completed', totals)

#class TimevsTags(Module):
    #Compare a few workflows to see how long the project took vs. how many tags were made
 #   pass

_modules = [Vistrail, Log, ReadVistrail, CountActions, CountExecutedWorkflows, TotalDays]
