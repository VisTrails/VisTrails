###############################################################################
##
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

from __future__ import division

from PyQt4 import QtCore, QtGui

from vistrails.core import debug, configuration
from vistrails.core.db.locator import BaseLocator
from vistrails.core.modules.vistrails_module import ModuleSuspended
from vistrails.core.interpreter.job import JobMonitor
from vistrails.gui import theme
from vistrails.gui.common_widgets import QDockPushButton
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

import time


refresh_states = [('Off', 0), ('10 sec', 10),
                  ('1 min', 60), ('10 min', 600),
                  ('1 hour', 3600)]


class QNumberValidator(QtGui.QIntValidator):
    """Variant of QIntValidaator that rejects Intermediate values.

    Intermediate strings are strings that could be the left part of an
    Acceptable string.
    """
    def validate(self, input, pos):
        result = QtGui.QIntValidator.validate(self, input, pos)
        if len(input) and result[0] == QtGui.QIntValidator.Intermediate:
            return (QtGui.QIntValidator.Invalid, pos)
        return result


class QJobTree(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        menu = QtGui.QMenu(self)
        if item and isinstance(item, QJobItem):
            act = QtGui.QAction("View Standard &Output", self)
            act.setStatusTip("View Standard Output in new window")
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   item.stdout)
            menu.addAction(act)
            act = QtGui.QAction("View Standard &Error", self)
            act.setStatusTip("View Standard Error in new window")
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   item.stderr)
            menu.addAction(act)
            menu.exec_(event.globalPos())


class QJobView(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.jobMonitor = JobMonitor.getInstance()
        self.jobMonitor.setCallback(self)
        self.timer_id = None

        self.workflowItems = {}

        self.layout = QtGui.QVBoxLayout()

        buttonsLayout = QtGui.QHBoxLayout()
        run_now = QDockPushButton("Check now")
        run_now.setToolTip("Check all jobs now")
        run_now.clicked.connect(self.timerEvent)
        buttonsLayout.addWidget(run_now)
        label = QtGui.QLabel('Refresh interval (seconds):')
        buttonsLayout.addWidget(label)

        self.interval = QtGui.QComboBox()
        for text, seconds in refresh_states:
            self.interval.addItem(text, seconds)
        self.interval.setCompleter(None)
        self.interval.setEditable(True)
        self.interval.editTextChanged.connect(self.set_refresh)
        self.interval.setValidator(QNumberValidator())
        conf = configuration.get_vistrails_configuration()
        self.interval.setEditText(unicode(conf.jobCheckInterval))
        buttonsLayout.addWidget(self.interval)

        self.autorun = QtGui.QCheckBox("Automatic re-execution")
        self.autorun.setToolTip("Automatically re-execute workflow when jobs "
                                "complete")
        self.connect(self.autorun, QtCore.SIGNAL('toggled(bool)'),
                     self.autorunToggled)
        self.autorun.setChecked(conf.jobAutorun)
        buttonsLayout.addWidget(self.autorun)

        buttonsLayout.addStretch(1)
        self.layout.addLayout(buttonsLayout)

        self.jobView = QJobTree()
        self.jobView.setContentsMargins(0, 0, 0, 0)
        self.jobView.setColumnCount(2)
        self.jobView.setHeaderLabels(['Job', 'Message'])
        self.jobView.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.jobView.header().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.jobView.setExpandsOnDoubleClick(False)
        self.connect(self.jobView,
                     QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                     self.item_clicked)
        self.layout.addWidget(self.jobView)

        self.setLayout(self.layout)
        self.setWindowTitle('Running Jobs')
        self.resize(QtCore.QSize(800, 600))
        self.updating_now = False

    def autorunToggled(self, value):
        conf = configuration.get_vistrails_configuration()
        conf.jobAutorun = value

    def set_refresh(self, refresh=0):
        """Changes the timer time.

        Called when the QComboBox self.interval changes. Updates the
        configuration and restarts the timer.
        """
        self.updating_now = True
        refresh = unicode(refresh) if refresh else '0'
        if refresh in dict(refresh_states):
            refresh = dict(refresh_states)[refresh]
            self.interval.setEditText(unicode(refresh))
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
        """Empty callback.
        """

    def addJobRec(self, obj, parent_id=None):
        """Recursively adds jobs that are executed by other modules like
           Groups and Maps. This is only for display purposes.
        """
        workflow = self.jobMonitor.currentWorkflow()
        workflowItem = self.workflowItems[workflow.id]
        # top down. Base is assumed to have been added already
        base = (workflowItem.intermediates[parent_id] if parent_id is not None
                                                      else workflowItem)
        id = obj.signature
        if id not in workflow.modules and parent_id:
            id = '%s/%s' % (parent_id, obj.signature)
        if obj.children:
            # add parent items and their children
            if id not in workflowItem.intermediates:
                workflowItem.intermediates[id] = QParentItem(id,
                                                             obj.name, base)
            for child in obj.children:
                self.addJobRec(child, id)
        elif obj.signature in workflow.modules:
            # this is an already existing new-style job
            job = workflowItem.jobs[obj.signature]
            job.monitor = obj.monitor
            # need to force takeChild
            base.addChild(job.parent().takeChild(job.parent().indexOfChild(job)))
        elif id in workflow.modules:
            # this is an already existing old-style job
            job = workflowItem.jobs[id]
            job.monitor = obj.monitor
            # need to force takeChild
            base.addChild(job.parent().takeChild(job.parent().indexOfChild(job)))

    def finishWorkflow(self, workflow):
        """Callback, updates workflow status.
        """
        workflow = self.jobMonitor.currentWorkflow()
        # untangle parents
        for parent in workflow.parents.itervalues():
            self.addJobRec(parent)

        workflowItem = self.workflowItems.get(workflow.id, None)
        if workflowItem:
            workflowItem.updateJobs()
            self.set_visible(True)

    def update_jobs(self):
        """Called via a timer.

        Checks all jobs for workflows both with and without monitors.
        """
        for workflow in self.workflowItems.values():
            # jobs without a monitor can also be checked
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
                    # call monitor
                    job.jobFinished = self.jobMonitor.isDone(job.monitor)
                    if job.jobFinished:
                        job.setText(1, "Finished")
                except Exception, e:
                    debug.critical("Error checking job %s: %s" % workflow.name,
                                   e)
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
        Callback, adds or updates a job in the interface.
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

    def checkJob(self, module, id, monitor):
        """ checkJob(module: VistrailsModule, id: str, monitor: instance)
        Callback, checks if job has completed.
        """
        workflow = self.jobMonitor.currentWorkflow()
        if not workflow:
            if not monitor or not self.jobMonitor.isDone(monitor):
                raise ModuleSuspended(module, 'Job is running', monitor=monitor,
                                      job_id=id)
        workflowItem = self.workflowItems[workflow.id]
        item = workflowItem.jobs.get(id, None)
        item.setText(0, item.job.name)
        # we should check the status using monitor and show dialog
        # get current view progress bar and hijack it
        if monitor:
            item.monitor = monitor
        workflow = self.jobMonitor.currentWorkflow()
        workflowItem = self.workflowItems.get(workflow.id, None)
        workflowItem.updateJobs()
        progress = workflowItem.view.controller.progress

        conf = configuration.get_vistrails_configuration()
        interval = conf.jobCheckInterval
        if interval and not conf.jobAutorun and not progress.suspended:
            # we should keep checking the job
            if monitor:
                # wait for module to complete
                labelText = (("Running external job %s\n"
                                       "Started %s\n"
                                       "Press Cancel to suspend")
                                       % (item.job.name,
                                          item.job.start))
                progress.setLabelText(labelText)
                while not self.jobMonitor.isDone(monitor):
                    i = 0
                    while i < interval:
                        i += 1
                        time.sleep(1)
                        QtCore.QCoreApplication.processEvents()
                        if progress.wasCanceled():
                            # this does not work, need to create a new progress dialog
                            #progress.goOn()
                            new_progress =  progress.__class__(progress.parent())
                            new_progress.setMaximum(progress.maximum())
                            new_progress.setValue(progress.value())
                            new_progress.setLabelText(labelText)
                            new_progress.setMinimumDuration(0)
                            new_progress.suspended = True
                            workflowItem.view.controller.progress = new_progress
                            progress.hide()
                            progress.deleteLater()
                            progress = new_progress
                            progress.show()
                            QtCore.QCoreApplication.processEvents()
                            raise ModuleSuspended(module,
                                       'Interrupted by user, job'
                                       ' is still running', monitor=monitor,
                                       job_id=id)
                return
        if not monitor or not self.jobMonitor.isDone(monitor):
            raise ModuleSuspended(module, 'Job is running', monitor=monitor,
                                  job_id=id)

    def deleteWorkflow(self, id):
        """ deleteWorkflow(id: str) -> None
        Callback, deletes a workflow.
        """
        self.jobView.takeTopLevelItem(
            self.jobView.indexOfTopLevelItem(
                self.workflowItems[id]))
        del self.workflowItems[id]

    def deleteJob(self, id, parent_id=None):
        """ deleteJob(id: str, parent_id: str) -> None
        Callback, deletes a a single job.

        If parent_id is None, the current workflow is used
        """
        workflowItem = self.workflowItems[parent_id]
        jobItem = workflowItem.jobs[id]
        jobItem.parent().takeChild(jobItem.parent().indexOfChild(jobItem))
        workflowItem.updateJobs()
        del workflowItem.jobs[id]

    def item_clicked(self, item):
        """Item activated.
        """
        if isinstance(item, QWorkflowItem):
            item.goto()

    def load_running_jobs(self):
        """Loads the current jobs from the JSON file.
        """
        workflows = self.jobMonitor._running_workflows
        # update gui
        for workflow in workflows.itervalues():
            if workflow.id not in self.workflowItems:
                workflowItem = QWorkflowItem(workflow, self.jobView)
                self.jobView.addTopLevelItem(workflowItem)
                self.workflowItems[workflow.id] = workflowItem
                for job in workflow.modules.itervalues():
                    if job.id not in workflowItem.jobs:
                        workflowItem.jobs[job.id] = QJobItem(job, workflowItem)
                        workflowItem.updateJobs()
        if workflows:
            self.set_visible(True)


class QWorkflowItem(QtGui.QTreeWidgetItem):
    """A suspended workflow.

    This top-level item can have children items.
    """
    def __init__(self, workflow, parent):
        self.locator = BaseLocator.from_url(workflow.vistrail)
        QtGui.QTreeWidgetItem.__init__(self, parent, ['', ''])
        self.setToolTip(0, "Double-Click to View Pipeline")
        self.setToolTip(1, workflow.id)
        self.workflow = workflow
        self.has_queue = True
        self.setIcon(0, theme.get_current_theme().JOB_CHECKING)
        self.setExpanded(True)
        self.workflowFinished = False
        self.jobs = {}
        self.intermediates = {}
        self.updateJobs()

    def updateJobs(self):
        from vistrails.gui.vistrails_window import _app
        self.view = _app.getViewFromLocator(self.locator)
        if self.view:
            self.name = "%s:%s" % (self.locator.short_name,
                                   self.view.controller.get_pipeline_name())
        else:
            self.name = "%s:%s" % (self.locator.short_name,
                                   self.workflow.version)
        self.setText(0, self.name)
        self.has_queue = True
        for job in self.jobs.itervalues():
            job.updateJob()
            if not job.job.finished and not job.monitor:
                self.has_queue = False
        count = len(self.jobs)
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
    """A pending job, i.e. a single module that was suspended.

    These will be either under a QWorkflowItem or a QParentItem.
    """
    def __init__(self, job, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [job.name,
                                                      job.description()])
        self.setToolTip(1, job.description())
        self.job = job
        # This is different from job.jobFinished after monitor finishes
        self.jobFinished = self.job.finished
        self.monitor = None
        self.updateJob()
        self.setExpanded(True)

    def updateJob(self):
        if self.job.finished:
            self.jobFinished = self.job.finished
        self.setText(1, self.job.parameters.get('__message__',
                        "Finished" if self.jobFinished else "Running"))
        if self.jobFinished:
            self.setIcon(0, theme.get_current_theme().JOB_FINISHED)
            self.setToolTip(0, "This Job Has Finished")
        elif self.monitor:
            self.setIcon(0, theme.get_current_theme().JOB_SCHEDULED)
            self.setToolTip(0, "This Job is Running and Scheduled for Checking")
        else:
            self.setIcon(0, theme.get_current_theme().JOB_CHECKING)
            self.setToolTip(0, "This Job is Running")
        self.setToolTip(1, self.job.id)

    def stdout(self):
        if self.monitor:
            sp = LogMonitor("Standard Output for " + self.job.name,
                            self.monitor)
            sp.exec_()

    def stderr(self):
        if self.monitor:
            sp = ErrorMonitor("Standard Output for " + self.job.name,
                              self.monitor)
            sp.exec_()


class QParentItem(QtGui.QTreeWidgetItem):
    """A composite job, i.e. a module whose child suspended.
    """
    def __init__(self, id, name, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [name, ''])
        self.id = id
        self.setExpanded(True)
        self.setToolTip(0, self.id)


class LogMonitor(QtGui.QDialog):
    """Displays the content of a Job's standard_output().
    """
    def __init__(self, name, monitor, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.monitor = monitor
        self.resize(700, 400)
        self.setWindowTitle(name)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.text = QtGui.QTextEdit('')
        self.update_text()
        self.text.setReadOnly(True)
        self.text.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        layout.addWidget(self.text)
        buttonLayout = QtGui.QHBoxLayout()

        close = QtGui.QPushButton('Close', self)
        close.setFixedWidth(100)
        buttonLayout.addWidget(close)
        self.connect(close, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('close()'))

        update = QtGui.QPushButton('Update', self)
        update.setFixedWidth(100)
        buttonLayout.addWidget(update)
        self.connect(update, QtCore.SIGNAL('clicked()'),
                     self.update_text)

        layout.addLayout(buttonLayout)

    def update_text(self):
        self.text.setPlainText(self.monitor.standard_output())


class ErrorMonitor(LogMonitor):
    """Displays the content of a job's standard_error().
    """
    def update_text(self):
        self.text.setPlainText(self.monitor.standard_error())
