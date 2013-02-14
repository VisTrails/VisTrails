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

from PyQt4 import QtCore, QtGui

from core import debug, configuration
from gui.vistrails_palette import QVistrailsPaletteInterface
from gui import theme
from core.db.locator import BaseLocator
from gui.common_widgets import QDockPushButton

refresh_states = [('Off', 0), ('10 sec', 10),
                  ('1 min', 60), ('10 min', 600),
                  ('1 hour', 3600)]

class QNumberValidator(QtGui.QIntValidator):
    def validate(self, input, pos):
        result = QtGui.QIntValidator.validate(self, input, pos)
        if len(input) and result[0] == QtGui.QIntValidator.Intermediate:
            return (QtGui.QIntValidator.Invalid, pos)
        return result

class QJobView(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.timer_id = None

        self.workflowItems = {}
        self.layout = QtGui.QVBoxLayout()
#        self.layout.setContentsMargins(5, 5, 0, 0)

        buttonsLayout = QtGui.QHBoxLayout()
        #buttonsLayout.setMargin(5)
        #buttonsLayout.setSpacing(5)
        run_now = QDockPushButton("Check now")
        run_now.setToolTip("Check all jobs now")
        run_now.clicked.connect(self.timerEvent)
        buttonsLayout.addWidget(run_now)
        label = QtGui.QLabel('Refresh interval (seconds):')
        buttonsLayout.addWidget(label)

        self.interval = QtGui.QComboBox()
        for text, seconds in refresh_states:
            self.interval.addItem(text, seconds)
            self.interval.editTextChanged.connect(self.set_refresh)
        self.interval.setEditable(True)
        self.interval.setCurrentIndex(self.interval.findText('10 min'))
        self.interval.setCompleter(None)
        self.interval.setValidator(QNumberValidator())
        buttonsLayout.addWidget(self.interval)

        self.autorun = QtGui.QCheckBox("Run When Ready")
        self.autorun.setToolTip("Automatically re-execute the workflow when jobs have completed")
        buttonsLayout.addWidget(self.autorun)

        self.rerun = QtGui.QCheckBox("Run To Check")
        self.rerun.setToolTip("Automatically re-execute workflows that does not provide a status check method")
        buttonsLayout.addWidget(self.rerun)

        buttonsLayout.addStretch(1)
        self.layout.addLayout(buttonsLayout)

        self.jobView = QtGui.QTreeWidget()
        self.jobView.setContentsMargins(0, 0, 0, 0)
        self.jobView.setColumnCount(2)
        self.jobView.setHeaderLabels(['Job', 'Message'])
        self.jobView.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.jobView.header().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.jobView.setExpandsOnDoubleClick(False)
        self.connect(self.jobView,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.item_selected)
        self.layout.addWidget(self.jobView)

        self.setLayout(self.layout)
        self.setWindowTitle('Running Jobs')
        self.resize(QtCore.QSize(800, 600))
        self.updating_now = False


    def set_refresh(self, refresh=0):
        self.updating_now = True
        refresh = str(refresh) if refresh else '0'
        # changes the timer time
        if refresh in dict(refresh_states):
            refresh = dict(refresh_states)[refresh]
            self.interval.setEditText(str(refresh))
        else:
            refresh = int(refresh)
        if refresh:
            if self.timer_id is not None:
                self.killTimer(self.timer_id)
            self.timer_id = self.startTimer(refresh*1000)
        else:
            if self.timer_id:
                self.killTimer(self.timer_id)
                self.timer_id = None
        self.updating_now = False
                
    def update_jobs(self):
        # check all jobs
        for workflow in self.workflowItems.values():
            # jobs without a queue can also be checked
            if not workflow.has_queue:
                if self.rerun.isChecked():
                    workflow.execute()
                continue
            if workflow.workflowFinished:
                continue
            for job in workflow.jobs.itervalues():
                if job.jobFinished:
                    continue
                try:
                    # call queue
                    job.jobFinished = job.queue.finished().val()
                except Exception, e:
                    debug.critical("Error checking job %s: %s" %
                                   (workflow.name, str(e)))
                if job.jobFinished:
                    job.setIcon(0, theme.get_current_theme().JOB_FINISHED)
                workflow.countJobs()
            workflow.workflowFinished = len(workflow.jobs) == \
                         sum(j.jobFinished for j in workflow.jobs.itervalues())
            if workflow.workflowFinished:
                workflow.setIcon(0, theme.get_current_theme().JOB_FINISHED)
            workflow.countJobs()
            if workflow.workflowFinished:
                if self.autorun.isChecked():
                    workflow.execute()
                    continue
                ret = QtGui.QMessageBox.information(self, "Job Ready",
                        'Pending Jobs in workflow "%s" has finished, do you want '
                        'to continue the execution now?' % workflow.name,
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                if ret == QtGui.QMessageBox.Ok:
                    workflow.execute()

    def timerEvent(self, id=None):
        if self.updating_now:
            return
        self.updating_now = True
        self.update_jobs()
        self.updating_now = False

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            items = self.jobView.selectedItems()
            if len(items) == 1:
                index = self.jobView.indexOfTopLevelItem(items[0])
                if index>=0:
                    self.delete_job(items[0].controller)
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def add_job(self, controller, error, prev='', workflow=None):
        """ Adds job recursively """
        added = False
        if not prev:
            if controller.vistrail.locator:
                name = controller.vistrail.locator.short_name
            else:
                name = 'Untitled.vt'
            version_id = controller.current_version
            if (name, version_id) not in self.workflowItems:
                workflow = QWorkflowItem(controller, error, self.jobView)
                self.jobView.addTopLevelItem(workflow)
                self.workflowItems[(name, version_id)] = workflow

                # save job to configuration
                if controller.vistrail.locator:
                    conf = configuration.get_vistrails_configuration()
                    if not conf.has('runningJobsList') or not conf.runningJobsList:
                        conf_jobs = []
                    else:
                        conf_jobs = conf.runningJobsList.split(';')
                    if not conf_jobs:
                        conf_jobs = []
                    url = controller.vistrail.locator.to_url() + \
                          "?workflow=%s" % version_id
                    if not url in conf_jobs:
                        conf_jobs.append(str(url))
                        conf.runningJobsList = ';'.join(conf_jobs)
                        configuration.get_vistrails_persistent_configuration(
                            ).runningJobsList = conf.runningJobsList
            else:
                workflow = self.workflowItems[(name, version_id)]
        job_name = ((prev+'.') if prev else '') + error.module.__class__.__name__

        if not error.children:
            if not error.queue:
                # We allow jobs without queue objects, but they will
                # have to be checked by re-executing the entire workflow
                workflow.has_queue = False
                workflow.setIcon(0, theme.get_current_theme().JOB_SCHEDULED)
                workflow.setToolTip(0, 'To check this workflow it must be re-executed. Make sure "Run To Check" is checked.')

                #return False
            # remove any previous instance of this job, if name is shorter
            if id(error) in workflow.jobs and \
               len(job_name) > len(workflow.jobs[id(error)].text(0)):
                workflow.takeChild(workflow.indexOfChild(
                  workflow.jobs[id(error)]))
                del workflow.jobs[id(error)]
            # if we did not keep an already existing job, add it
            if id(error) not in workflow.jobs:
                job = QJobItem(job_name, error)
                workflow.addChild(job)
                workflow.jobs[id(error)] = job
                workflow.countJobs()
                return True
        else:
            for child in error.children:
                result = self.add_job(controller, child, job_name, workflow)
                if result:
                    added = True
        return added
                        
    def delete_job(self, controller, version_id=None, all=True):
        if all:
            for k in self.workflowItems.keys():
                workflow = self.workflowItems[k]
                if workflow.controller is controller:
                    self.jobView.takeTopLevelItem(
                        self.jobView.indexOfTopLevelItem(
                            self.workflowItems[k]))
                    del self.workflowItems[k]
                
        if not version_id:
            version_id = controller.current_version
        if controller.locator:
            conf = configuration.get_vistrails_configuration()
            if not conf.has('runningJobsList') or not conf.runningJobsList:
                conf_jobs = []
            else:
                conf_jobs = conf.runningJobsList.split(';')
            if not conf_jobs:
                conf_jobs = []
            url = controller.locator.to_url() + "?workflow=%s" % version_id
            if url in conf_jobs:
                conf_jobs.remove(url)
                conf.runningJobsList = ';'.join(conf_jobs)
                configuration.get_vistrails_persistent_configuration(
                    ).runningJobsList = conf.runningJobsList
            name = controller.vistrail.locator.short_name
        else:
            name = 'Untitled.vt'
        if (name, version_id) in self.workflowItems:
            self.jobView.takeTopLevelItem(
                self.jobView.indexOfTopLevelItem(
                    self.workflowItems[(name, version_id)]))
            del self.workflowItems[(name, version_id)]

    def item_selected(self, item):
        if type(item) == QWorkflowItem:
            item.goto()

    def load_running_jobs(self):
        conf = configuration.get_vistrails_configuration()
        if conf.has('runningJobsList') and conf.runningJobsList:
            result = QtGui.QMessageBox.question(self, "Running Jobs Found",
                "Running Jobs Found. Do you want to continue running the jobs from the previous session?",
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                for url in conf.runningJobsList.split(';'):
                    loc, version = url.split('?')
                    locator = BaseLocator.from_url(loc)
                    from gui.vistrails_window import _app
                    _app.open_vistrail_without_prompt(locator, int(version.split('=')[1]))
                    _app.get_current_view().execute()
            else:
                conf.runningJobsList = ''
                configuration.get_vistrails_persistent_configuration(
                            ).runningJobsList = conf.runningJobsList
                

class QWorkflowItem(QtGui.QTreeWidgetItem):
    """ The workflow that was suspended """
    def __init__(self, controller, error, parent):
        if controller.vistrail.locator:
            self.name = "%s:%s" % (controller.vistrail.locator.short_name,
                                    controller.get_pipeline_name()[10:])
        else:
            self.name = "Untitled.vt:%s" % controller.get_pipeline_name()[10:]
            
        QtGui.QTreeWidgetItem.__init__(self, parent,
                    [self.name, error if type(error)==str else error.msg])
        self.setToolTip(0, "Double-Click to View Pipeline")
        self.setToolTip(1, error if type(error)==str else error.msg)
        
        self.controller = controller
        self.version = controller.current_version
        self.has_queue = True
        self.setIcon(0, theme.get_current_theme().JOB_CHECKING)
        self.setToolTip(0, "This Job has a method to check if it has finished.")
        self.workflowFinished = False
        self.jobs = {}
        from gui.vistrails_window import _app
        self.view = _app.get_current_view()
    
    def countJobs(self):
        count = self.childCount()
        finished = sum([self.child(i).jobFinished for i in xrange(count)])
        self.setText(0, "%s (%s/%s)" % (self.name, finished, count))

    def goto(self):
        from gui.vistrails_window import _app
        _app.change_view(self.view)
        self.view.version_selected(self.version, True, double_click=True)
    
    def execute(self):
        self.goto()
        self.view.execute()

class QJobItem(QtGui.QTreeWidgetItem):
    """ The module that was suspended """
    def __init__(self, name, error, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [name, error.msg])
        self.setToolTip(1, error.msg)
        self.queue = error.queue
        if self.queue:
            self.setIcon(0, theme.get_current_theme().JOB_CHECKING)
            self.setToolTip(0, "This Job has a method to check if it has finished.")
        else:
            self.setIcon(0, theme.get_current_theme().JOB_SCHEDULED)
            self.setToolTip(0, 'To check this job the workflow must be re-executed. Make sure "Run To Check" is checked.')
        self.jobFinished = False
