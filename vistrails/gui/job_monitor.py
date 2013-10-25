###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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

from vistrails.api import get_current_controller
from vistrails.core import debug, configuration
from vistrails.core.db.locator import BaseLocator, UntitledLocator
from vistrails.core.modules.vistrails_module import ModuleSuspended
from vistrails.core.interpreter.job import JobMonitor, Workflow
from vistrails.gui import theme
from vistrails.gui.common_widgets import QDockPushButton
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

import time

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

        self.jobMonitor = JobMonitor.getInstance()
        self.jobMonitor.setCallback(self)
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
        conf = configuration.get_vistrails_configuration()
        if conf.jobCheckInterval and conf.jobCheckInterval != 10:
            self.interval.setEditText(str(conf.jobCheckInterval))
        buttonsLayout.addWidget(self.interval)

        self.autorun = QtGui.QCheckBox("Automatic re-execution")
        self.autorun.setToolTip("Automatically re-execute workflow when jobs "
                                "complete")
        self.autorun.toggled.connect(self.autorunToggled)
        if conf.jobAutorun:
            self.autorun.setChecked(True)
        buttonsLayout.addWidget(self.autorun)

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

    def autorunToggled(self, value):
        conf = configuration.get_vistrails_configuration()
        conf.jobAutorun = value
    
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
        conf = configuration.get_vistrails_configuration()
        conf.jobCheckInterval = refresh
        self.updating_now = False
                
    def startWorkflow(self, workflow):
        pass

    def finishWorkflow(self, workflow):
        """ update workflow status
        
        """
        workflowItem = self.workflowItems.get(workflow.id, None)
        if workflowItem:
            workflowItem.updateJobs()
            self.set_visible(True)
            
    def update_jobs(self):
        """ check all jobs both for workflows with and without monitors
        """
        for workflow in self.workflowItems.values():
            # jobs without a queue can also be checked
            if not workflow.has_queue:
                # restart job and execute
                self.jobMonitor.startWorkflow(workflow.workflow)
                self.updating_now = False
                workflow.execute()
                self.updating_now = True
                continue
            if workflow.workflowFinished:
                continue
            for job in workflow.jobs.itervalues():
                if job.jobFinished:
                    continue
                try:
                    # call queue
                    job.jobFinished = job.queue.finished()
                    # old version of BatchQ needs to call .val()
                    if not isinstance(job.jobFinished, bool):
                        job.jobFinished = job.jobFinished.val()
                    if job.jobFinished:
                        job.setText(1, "Finished")
                except Exception, e:
                    debug.critical("Error checking job %s: %s" %
                                   (workflow.name, str(e)))
            workflow.updateJobs()
            if workflow.workflowFinished:
                if self.autorun.isChecked():
                    self.jobMonitor.startWorkflow(workflow.workflow)
                    self.updating_now = False
                    workflow.execute()
                    self.updating_now = True
                    continue
                ret = QtGui.QMessageBox.information(self, "Job Ready",
                        'Pending Jobs in workflow "%s" have finished, '
                        'continue execution now?' % workflow.name,
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                if ret == QtGui.QMessageBox.Ok:
                    self.jobMonitor.startWorkflow(workflow.workflow)
                    self.updating_now = False
                    workflow.execute()
                    self.updating_now = True

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
                item = items[0]
                if isinstance(item, QWorkflowItem):
                    self.jobMonitor.deleteWorkflow(item.workflow.id)
                elif isinstance(item, QJobItem):
                    # find parent
                    parent = item.parent()
                    while not isinstance(parent, QWorkflowItem):
                        parent = parent.parent()
                    self.jobMonitor.deleteJob(item.job.id, parent.workflow.id)
                index = self.jobView.indexOfTopLevelItem(items[0])
                if index>=0:
                    self.delete_job(items[0].controller, items[0].version)
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def addJob(self, job):
        """ addJob(self, job: job.Module) -> None
            Adds or updates job in interface
        """

        workflow = self.jobMonitor.currentWorkflow()
        if workflow.id not in self.workflowItems:
            workflowItem = QWorkflowItem(workflow, self.jobView)
            self.jobView.addTopLevelItem(workflowItem)
            self.workflowItems[workflow.id] = workflowItem

        workflowItem = self.workflowItems[workflow.id]
        if job.id not in workflowItem.jobs:
            workflowItem.jobs[job.id] = QJobItem(job, workflowItem)
        workflowItem.updateJobs()

    def checkJob(self, module, monitor, exception=None, name=''):
        """ checkJob(module: VistrailsModule, monitor: instance,
                     exception: ModuleSuspended) -> None
            Checks if job has completed
            Also creates parent modules

        """
        workflow = self.jobMonitor.currentWorkflow()
        if not workflow:
            return
        workflowItem = self.workflowItems[workflow.id]
        id = module.signature
        item = workflowItem.jobs.get(id, None)
        if item:
            item.setText(0, name if name else item.job.name)
        else:
            # this is a new parent item
            parentItem = QParentItem(module.signature, name, workflowItem)
            workflowItem.intermediates[module.signature] = parentItem
            for child in exception.children:
                # set all child jobs as child of this one
                item = workflowItem.jobs.get(child.module.signature, None)
                if item:
                    parentItem.addChild(item)
                # set all child intermediates as child of this one
                item = workflowItem.intermediates.get(child.module.signature,
                                                      None)
                if item:
                    parentItem.addChild(item)
            return
        if exception:
            # This is a suspended old/new job
            # we don't need to do anything else here
            return
        # we are still running, we should check the status using monitor
        # and show dialog
        # get current view progress bar and hijack it
        if monitor:
            item.queue = monitor
        workflow = self.job.currentWorkflow()
        workflow.countJobs()
        workflowItem = self.workflowItems.get(workflow.id, None)
        progress = workflowItem.view.current_pipeline_scene().progress

        conf = configuration.get_vistrails_configuration()
        interval = conf.jobCheckInterval
        if interval:
            if monitor:
                # wait for module to complete
                while not monitor.finished():
                    progress.setLabelText(("%s- external job\n"
                                           "Started %s\n"
                                           "Press Cancel to suspend")
                                           % (item.job.name,
                                              item.job.started))
                    time.sleep(interval)
                    QtCore.QCoreApplication.processEvents()
                    if progress.wasCanceled():
                        raise ModuleSuspended(module,
                                       'Interrupted by user, job'
                                       ' is still running', queue=monitor)
        if not monitor or not monitor.finished():
            raise ModuleSuspended(module, 'Job is running', queue=monitor)
        
    def deleteWorkflow(self, id):
        """ deleteWorkflow(id: str) -> None
            deletes a workflow

        """
        self.jobView.takeTopLevelItem(
            self.jobView.indexOfTopLevelItem(
                self.workflowItems[id]))
        del self.workflowItems[id]
        
    def deleteJob(self, id, parent_id=None):
        """ deleteJob(id: str, parent_id: str) -> None
            deletes a job
            if parent_id is None, the current workflow is used
        """
        workflowItem = self.workflowItems[parent_id]
        jobItem = workflowItem.jobs[id]
        jobItem.parent().takeChild(jobItem.parent().indexOfChild(jobItem))
        workflowItem.updateJobs()
        del workflowItem.jobs[id]
        
    def item_selected(self, item):
        if isinstance(item, QWorkflowItem):
            item.goto()

    def load_running_jobs(self):
        workflows = self.jobMonitor.load_from_file()
        # update gui
        for workflow in workflows.itervalues():
            workflowItem = QWorkflowItem(workflow, self.jobView)
            self.jobView.addTopLevelItem(workflowItem)
            self.workflowItems[workflow.id] = workflowItem
            for job in workflow.modules.itervalues():
                workflowItem.jobs[job.id] = QJobItem(job, workflowItem)
                workflowItem.updateJobs()
        if workflows:
            self.set_visible(True)

class QWorkflowItem(QtGui.QTreeWidgetItem):
    """ The workflow that was suspended """
    def __init__(self, workflow, parent):
        from vistrails.gui.vistrails_window import _app
        self.locator = BaseLocator.from_url(workflow.vistrail)
        self.view = _app.getViewFromLocator(self.locator)
        if self.view:
            self.name = "%s:%s" % (self.locator.short_name,
                                   self.view.controller.get_pipeline_name())
        else:
            self.name = "%s:%s" % (self.locator.short_name, workflow.version)
        QtGui.QTreeWidgetItem.__init__(self, parent, [self.name, ''])
        self.setToolTip(0, "Double-Click to View Pipeline")
        self.setToolTip(1, '')
        self.workflow = workflow
        self.has_queue = True
        self.setIcon(0, theme.get_current_theme().JOB_CHECKING)
        self.workflowFinished = False
        self.jobs = {}
        self.intermediates = {}
    
    def updateJobs(self):
        self.has_queue = True
        for job in self.jobs.itervalues():
            job.updateJob()
            if not job.job.finished and not job.queue:
                self.has_queue = False
        count = self.childCount()
        finished = sum([job.jobFinished for job in self.jobs.values()])
        self.setText(1, "(%s/%s)" % (finished, count))
        self.workflowFinished = (finished == count)
        if self.workflowFinished:
            self.setIcon(0, theme.get_current_theme().JOB_FINISHED)
        elif not self.has_queue:
            self.setIcon(0, theme.get_current_theme().JOB_SCHEDULED)
        else:
            self.setIcon(0, theme.get_current_theme().JOB_CHECKING)

    def goto(self):
        from vistrails.gui.vistrails_window import _app
        if not self.view:
            _app.open_vistrail_without_prompt(self.locator)
            self.view = _app.getViewFromLocator(self.locator)
        _app.change_view(self.view)
        self.view.version_selected(self.workflow.version, True,
                                   double_click=True)
    
    def execute(self):
        self.goto()
        self.view.execute()

class QJobItem(QtGui.QTreeWidgetItem):
    """ The module that was suspended """
    def __init__(self, job, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [job.name,
                                                      job.description()])
        self.setToolTip(1, job.description())
        self.job = job
        self.queue = None
        self.updateJob()
    
    def updateJob(self):
        self.jobFinished = self.job.finished
        self.setText(1, self.job.parameters.get('__message__',
                        "Finished" if self.jobFinished else "Running"))
        if self.jobFinished:
            self.setIcon(0, theme.get_current_theme().JOB_FINISHED)
            self.setToolTip(0, "This Job Has Finished")
        elif self.queue:
            self.setIcon(0, theme.get_current_theme().JOB_SCHEDULED)
            self.setToolTip(0, "This Job is Running and Scheduled for Checking")
        else:
            self.setIcon(0, theme.get_current_theme().JOB_CHECKING)
            self.setToolTip(0, "This Job is Running")

class QParentItem(QtGui.QTreeWidgetItem):
    """ A parent module of a suspended job """
    def __init__(self, id, name, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [name, ''])
        self.id = id