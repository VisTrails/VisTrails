###############################################################################
##
## Copyright (C) 2014-2015, New York University.
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

import time

from PyQt4 import QtCore, QtGui

from vistrails.core import debug, configuration
from vistrails.core.modules.vistrails_module import ModuleSuspended
from vistrails.gui import theme
from vistrails.gui.common_widgets import QDockPushButton
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface


refresh_states = [('Off', 0), ('10 sec', 10),
                  ('1 min', 60), ('10 min', 600),
                  ('1 hour', 3600)]


class QNumberValidator(QtGui.QIntValidator):
    """Variant of QIntValidator that rejects Intermediate values.

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
        self.setContentsMargins(0, 0, 0, 0)
        self.setColumnCount(2)
        self.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.header().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.header().close()
        self.setExpandsOnDoubleClick(False)
        self.controller = None

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
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   item.stderr)
            menu.addAction(act)
            menu.exec_(event.globalPos())

class QJobView(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.timer_id = None
        self.updating_now = False
        self.widgets = {}

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
        self.interval.setEditText(str(conf.jobCheckInterval))
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
        self.jobView.itemDoubleClicked.connect(self.item_clicked)
        self.layout.addWidget(self.jobView)

        self.setLayout(self.layout)

        self.setWindowTitle('Running Jobs')
        self.resize(QtCore.QSize(800, 600))

    def set_controller(self, controller):
        # check if a controller has been closed
        from vistrails.gui.vistrails_window import _app
        controllers = [view.controller for view in _app.getAllViews()]
        for c in self.widgets.keys():
            if c not in controllers:
                self.jobView.takeTopLevelItem(self.jobView.indexOfTopLevelItem(self.widgets[c]))
                del self.widgets[c]

        if not controller:
            return

        # check if controller has been added
        if controller not in self.widgets and controller in controllers:
            item = QVistrailItem(controller)
            self.jobView.addTopLevelItem(item)
            self.jobView.expandAll()
            self.widgets[controller] = item
            if item.childCount() > 0:
                self.set_visible(True)

    def autorunToggled(self, value):
        conf = configuration.get_vistrails_configuration()
        conf.jobAutorun = value

    def set_refresh(self, refresh=0):
        """Changes the timer time.

        Called when the QComboBox self.interval changes. Updates the
        configuration and restarts the timer.
        """
        self.updating_now = True
        refresh = str(refresh) if refresh else '0'
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
        conf = configuration.get_vistrails_persistent_configuration()
        conf.jobCheckInterval = refresh
        self.updating_now = False

    def update_jobs(self):
        """Called via a timer.

        Checks jobs for all workflows both with and without monitors.
        """
        for i in xrange(self.jobView.topLevelItemCount()):
            vistrail = self.jobView.topLevelItem(i)
            jm = vistrail.jobMonitor
            for workflow_item in vistrail.workflowItems.values():
                workflow = workflow_item.workflow
                # jobs without a handle can also be checked
                if not workflow_item.has_handle:
                    # restart job and execute
                    jm.startWorkflow(workflow)
                    self.updating_now = False
                    workflow_item.execute()
                    self.updating_now = True
                    continue
                if workflow_item.workflowFinished:
                    continue
                for job in workflow_item.jobs.itervalues():
                    if job.jobFinished:
                        continue
                    try:
                        # call monitor
                        job.jobFinished = jm.isDone(job.handle)
                        if job.jobFinished:
                            job.setText(1, "Finished")
                    except Exception, e:
                        debug.critical("Error checking job %s: %s" %
                                       (workflow_item.text(0), e))
                workflow_item.updateJobs()
                if workflow_item.workflowFinished:
                    if self.autorun.isChecked():
                        jm.startWorkflow(workflow)
                        self.updating_now = False
                        workflow_item.execute()
                        self.updating_now = True
                        continue
                    ret = QtGui.QMessageBox.information(self, "Job Ready",
                            'Pending Jobs in workflow "%s" have finished, '
                            'continue execution now?' % workflow_item.text(0),
                            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                    if ret == QtGui.QMessageBox.Ok:
                        jm.startWorkflow(workflow)
                        self.updating_now = False
                        workflow_item.execute()
                        self.updating_now = True

    def timerEvent(self, id=None):
        if self.updating_now:
            return
        self.updating_now = True
        try:
            self.update_jobs()
        finally:
            self.updating_now = False

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            for item in self.jobView.selectedItems():
                if isinstance(item, QWorkflowItem):
                    item.parent().controller.set_changed(True)
                    item.parent().jobMonitor.deleteWorkflow(item.workflow.id)
                elif isinstance(item, QJobItem):
                    # find parent
                    parent = item.parent()
                    while not isinstance(parent, QWorkflowItem):
                        parent = parent.parent()
                    parent.parent().controller.set_changed(True)
                    parent.parent().jobMonitor.deleteJob(item.job.id)
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def item_clicked(self, item):
        """Item activated.
        """
        if isinstance(item, QWorkflowItem):
            item.goto()


class QVistrailItem(QtGui.QTreeWidgetItem):
    """A vistrail with running workflows.

    This top-level item can have QWorkflowItem's as children.
    """
    def __init__(self, controller, parent=None):
        self.controller = controller
        self.jobMonitor = controller.jobMonitor
        self.jobMonitor.setCallback(self)
        self.locator = controller.vistrail.locator
        QtGui.QTreeWidgetItem.__init__(self, parent,
                                       [self.locator.short_name, ''])
        self.setIcon(0, theme.get_current_theme().HISTORY_ICON)
        self.setToolTip(0, self.locator.to_url())
        self.workflowItems = {}
        self.load_running_jobs()

    def load_running_jobs(self):
        """Loads the current jobs from the JSON file.
        """
        workflows = self.jobMonitor.workflows
        # update gui
        for workflow in workflows.itervalues():
            if workflow.id not in self.workflowItems:
                workflow_item = QWorkflowItem(workflow, self)
                self.workflowItems[workflow.id] = workflow_item
                for job in workflow.jobs.itervalues():
                    if job.id not in workflow_item.jobs:
                        workflow_item.jobs[job.id] = QJobItem(job, workflow_item)
                        workflow_item.updateJobs()

    def startWorkflow(self, workflow):
        """Empty callback.
        """

    def addJob(self, job):
        """ addJob(self, job: job.Module) -> None
        Callback, adds or updates a job in the interface.
        """

        workflow = self.jobMonitor.currentWorkflow()
        if workflow.id not in self.workflowItems:
            workflow_item = QWorkflowItem(workflow, self)
            workflow_item.setExpanded(True)
            self.workflowItems[workflow.id] = workflow_item

        workflow_item = self.workflowItems[workflow.id]
        if job.id not in workflow_item.jobs:
            workflow_item.jobs[job.id] = QJobItem(job, workflow_item)
        workflow_item.updateJobs()

    def deleteWorkflow(self, id):
        """ deleteWorkflow(id: str) -> None
        Callback, deletes a workflow.
        """
        self.takeChild(self.indexOfChild(self.workflowItems[id]))
        del self.workflowItems[id]

    def deleteJob(self, id):
        """ deleteJob(id: str, parent_id: str) -> None
        Callback, deletes a a single job from all workflows.

        """

        for workflow_item in self.workflowItems.itervalues():
            if id in workflow_item.jobs:
                job_item = workflow_item.jobs[id]
                job_item.parent().takeChild(job_item.parent().indexOfChild(job_item))
            del workflow_item.jobs[id]
            workflow_item.updateJobs()

    def addJobRec(self, obj, parent_id=None):
        """addJobRec(obj: ModuleSuspended, parent_id: signature)  -> None

           Recursively adds jobs that are executed by other modules like
           Groups and Maps. This is only for display purposes.
        """
        workflow = self.jobMonitor.currentWorkflow()
        workflow_item = self.workflowItems[workflow.id]
        # top down. Base is assumed to have been added already
        base = (workflow_item.intermediates[parent_id] if parent_id is not None
                                                       else workflow_item)
        id = obj.module.signature
        if obj.children:
            # add parent items and their children
            if id not in workflow_item.intermediates:
                parent_item = QParentItem(id, obj.name, base)
                parent_item.setExpanded(True)
                workflow_item.intermediates[id] = parent_item

            for child in obj.children:
                self.addJobRec(child, id)
        elif obj.module.signature in workflow.jobs:
            # this is an already existing new-style job
            job = workflow_item.jobs[obj.module.signature]
            job.handle = obj.handle
            # need to force takeChild
            base.addChild(job.parent().takeChild(job.parent().indexOfChild(job)))
        elif id in workflow.jobs:
            # this is an already existing old-style job
            job = workflow_item.jobs[id]
            job.handle = obj.handle
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
            QJobView.instance().set_visible(True)

    def checkJob(self, module, id, handle):
        """ checkJob(module: VistrailsModule, id: str, handle: object)
        Callback, checks if job has completed.
        """
        workflow = self.jobMonitor.currentWorkflow()
        if not workflow:
            if not handle or not self.jobMonitor.isDone(handle):
                raise ModuleSuspended(module, 'Job is running',
                                      handle=handle)
        workflow_item = self.workflowItems[workflow.id]
        item = workflow_item.jobs.get(id, None)
        item.setText(0, item.job.name)
        # we should check the status using the JobHandle and show dialog
        # get current view progress bar and hijack it
        if handle:
            item.handle = handle
        workflow = self.jobMonitor.currentWorkflow()
        workflow_item = self.workflowItems.get(workflow.id, None)
        workflow_item.updateJobs()
        progress = self.controller.progress

        conf = configuration.get_vistrails_configuration()
        interval = conf.jobCheckInterval
        if interval and not conf.jobAutorun and not progress.suspended:
            # we should keep checking the job
            if handle:
                # wait for module to complete
                labelText = (("Running external job %s\n"
                                       "Started %s\n"
                                       "Press Cancel to suspend")
                                       % (item.job.name,
                                          item.job.start))
                progress.setLabelText(labelText)
                while not self.jobMonitor.isDone(handle):
                    i = 0
                    while i < interval:
                        i += 1
                        time.sleep(1)
                        QtCore.QCoreApplication.processEvents()
                        if progress.wasCanceled():
                            # this does not work, need to create a new progress dialog
                            #progress.goOn()
                            new_progress = progress.__class__(progress.parent())
                            new_progress.setMaximum(progress.maximum())
                            new_progress.setValue(progress.value())
                            new_progress.setLabelText(labelText)
                            new_progress.setMinimumDuration(0)
                            new_progress.suspended = True
                            self.controller.progress = new_progress
                            progress.hide()
                            progress.deleteLater()
                            progress = new_progress
                            progress.show()
                            QtCore.QCoreApplication.processEvents()
                            raise ModuleSuspended(module,
                                       'Interrupted by user, job'
                                       ' is still running', handle=handle)
                return
        if not handle or not self.jobMonitor.isDone(handle):
            raise ModuleSuspended(module, 'Job is running', handle=handle)


class QWorkflowItem(QtGui.QTreeWidgetItem):
    """A workflow with jobs.

    This item can have child items.
    """
    def __init__(self, workflow, parent):
        QtGui.QTreeWidgetItem.__init__(self, parent, ['', ''])
        self.workflow = workflow
        self.has_handle = True
        self.setIcon(0, theme.get_current_theme().PIPELINE_ICON)
        self.setIcon(1, theme.get_current_theme().JOB_CHECKING)
        self.workflowFinished = False
        self.jobs = {}
        self.intermediates = {}
        self.updateJobs()

    def updateJobs(self):
        """ Updates name and job states
        """
        name = self.parent().controller.get_pipeline_name(
                                                        self.workflow.version)
        self.setText(0, name)
        self.setToolTip(0, 'Double-Click to View Pipeline "%s" with id %s' %
                           (name, self.workflow.version))
        self.setToolTip(1, "Log id: %s" % self.workflow.id)
        self.has_handle = True
        for job in self.jobs.itervalues():
            job.updateJob()
            if not job.job.finished and not job.handle:
                self.has_handle = False
        count = len(self.jobs)
        finished = sum([job.jobFinished for job in self.jobs.values()])
        self.setText(1, "(%s/%s)" % (finished, count))
        self.workflowFinished = (finished == count)
        if self.workflowFinished:
            self.setIcon(1, theme.get_current_theme().JOB_FINISHED)
        elif not self.has_handle:
            self.setIcon(1, theme.get_current_theme().JOB_SCHEDULED)
        else:
            self.setIcon(1, theme.get_current_theme().JOB_CHECKING)

    def goto(self):
        """ Shows this pipeline

        """
        from vistrails.gui.vistrails_window import _app
        view = _app.getViewFromLocator(self.parent().controller.locator)
        _app.change_view(view)
        view.version_selected(self.workflow.version, True, double_click=True)
        return view

    def execute(self):
        """ Shows and executes this pipeline
        """
        self.goto().execute()


class QJobItem(QtGui.QTreeWidgetItem):
    """A pending job, i.e. a single module that was suspended.

    These will be either under a QWorkflowItem or a QParentItem.
    """
    def __init__(self, job, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [job.name,
                                                      job.description()])
        self.setToolTip(1, job.description())
        self.job = job
        # This is different from job.jobFinished after job finishes
        self.jobFinished = self.job.finished
        self.handle = None
        self.updateJob()

    def updateJob(self):
        if self.job.finished:
            self.jobFinished = self.job.finished
        self.setText(1, self.job.parameters.get('__message__',
                        "Finished" if self.jobFinished else "Running"))
        if self.jobFinished:
            self.setIcon(1, theme.get_current_theme().JOB_FINISHED)
            self.setToolTip(0, "This Job Has Finished")
        elif self.handle:
            self.setIcon(1, theme.get_current_theme().JOB_SCHEDULED)
            self.setToolTip(0, "This Job is Running and Scheduled for Checking")
        else:
            self.setIcon(1, theme.get_current_theme().JOB_CHECKING)
            self.setToolTip(0, "This Job is Running")
        self.setToolTip(1, self.job.id)

    def stdout(self):
        if self.handle:
            sp = LogMonitor("Standard Output for " + self.job.name,
                            self.handle)
            sp.exec_()

    def stderr(self):
        if self.handle:
            sp = ErrorMonitor("Standard Output for " + self.job.name,
                              self.handle)
            sp.exec_()


class QParentItem(QtGui.QTreeWidgetItem):
    """A composite job, i.e. a module whose child suspended.
    """
    def __init__(self, id, name, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [name, ''])
        self.id = id
        self.setToolTip(0, self.id)


class LogMonitor(QtGui.QDialog):
    """Displays the content of a Job's standard_output().
    """
    def __init__(self, name, handle, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.handle = handle
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
        self.text.setPlainText(self.handle.standard_output())


class ErrorMonitor(LogMonitor):
    """Displays the content of a job's standard_error().
    """
    def update_text(self):
        self.text.setPlainText(self.handle.standard_error())
