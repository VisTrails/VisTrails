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

from PyQt4 import QtCore, QtGui

from vistrails.core import debug
from vistrails.core.configuration import get_vistrails_configuration, \
    get_vistrails_persistent_configuration
from vistrails.core.modules.vistrails_module import ModuleSuspended
from vistrails.core.vistrail.job import module_name
from vistrails.gui import theme
from vistrails.gui.common_widgets import QDockPushButton
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

import vistrails.core.system
import vistrails.gui.utils

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
            act = QtGui.QAction("&Check", self)
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   lambda :self.parent().check_jobs(item))
            menu.addAction(act)

            act = QtGui.QAction("&Delete", self)
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   lambda :self.parent().delete_item(item))
            menu.addAction(act)

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

        if item and isinstance(item, QWorkflowItem):

            act = QtGui.QAction("&Check", self)
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   lambda :self.parent().check_jobs(item))
            menu.addAction(act)

            if not item.paused and not item.workflowFinished:
                act = QtGui.QAction("&Pause", self)
                QtCore.QObject.connect(act,
                                       QtCore.SIGNAL("triggered()"),
                                       item.pause)
                menu.addAction(act)

            act = QtGui.QAction("Delete", self)
            QtCore.QObject.connect(act,
                                   QtCore.SIGNAL("triggered()"),
                                   lambda :self.parent().delete_item(item))

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
        run_now = QDockPushButton("Check selected")
        run_now.setToolTip("Check selected job now")
        run_now.clicked.connect(self.check_selected_job)
        buttonsLayout.addWidget(run_now)
        run_all = QDockPushButton("Check all")
        run_all.setToolTip("Check all jobs now")
        run_all.clicked.connect(self.timerEvent)
        buttonsLayout.addWidget(run_all)
        label = QtGui.QLabel('Refresh interval (seconds):')
        buttonsLayout.addWidget(label)

        self.interval = QtGui.QComboBox()
        for text, seconds in refresh_states:
            self.interval.addItem(text, seconds)
        self.interval.setCompleter(None)
        self.interval.setEditable(True)
        self.interval.editTextChanged.connect(self.set_refresh)
        self.interval.setValidator(QNumberValidator())
        conf = get_vistrails_configuration()
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
        get_vistrails_configuration().jobAutorun = value
        get_vistrails_persistent_configuration().jobAutorun = value

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
        get_vistrails_configuration().jobCheckInterval = refresh
        get_vistrails_persistent_configuration().jobCheckInterval = refresh
        self.updating_now = False

    def update_job(self, job, force=True):
        """ Checks specified job

            force: bool - True means we should ask user to resume jobs
            that has been paused
        """
        if isinstance(job, QJobItem):
            vistrail_item = job.vistrail()
            workflow_item = job.workflow()
        elif isinstance(job, QWorkflowItem):
            vistrail_item = job.parent()
            workflow_item = job
            job = None
        else:
            for workflow_item in job.workflowItems.values():
                self.update_job(workflow_item, force)
            return
        jm = vistrail_item.jobMonitor
        workflow = workflow_item.workflow
        if workflow_item.workflowFinished:
            return
        # re-execute if no handle is set
        if not workflow_item.has_handle:
            if workflow_item.paused:
                if force:
                    workflow_item.resume()
                else:
                    return
            try:
                int(workflow.version)
            except ValueError:
                if (workflow.version.startswith("Parameter Exploration") or
                    workflow.version.startswith("Mashup")):
                    QtGui.QMessageBox.question(self, "Running job(s) found",
                        'Running jobs in "%s" are not yet monitored. Rerun it to start monitoring.' %
                                             workflow_item.text(0),
                        QtGui.QMessageBox.Ok)
                    # do not notify again
                    workflow_item.pause()
                return
            # Ask user to re-execute workflow
            ret = QtGui.QMessageBox.question(self, "Running job(s) found",
                    'Running jobs in workflow "%s" are not yet monitored. Load and check now?' %
                                             workflow_item.text(0),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                workflow_item.pause()
                return
            # restart job and execute
            jm.startWorkflow(workflow)
            self.updating_now = False
            workflow_item.execute()
            self.updating_now = True
            return

        job_items = workflow_item.jobs.values() if job is None else [job]
        for job_item in job_items:
            if job_item.job.finished or job_item.job.ready:
                continue
            try:
                # call monitor
                if jm.isDone(job_item.handle):
                    job_item.job.ready = True
            except Exception, e:
                debug.critical("Error checking job %s: %s" %
                               (workflow_item.text(0), e))
        if workflow_item.updateJobs():
            QJobView.instance().set_visible(True)

        if workflow_item.workflowFinished:
            try:
                int(workflow.version)
            except ValueError:
                if workflow.version.startswith("Parameter Exploration"):
                    # this is too annoying
                    #QtGui.QMessageBox.information(self, "Job Ready",
                    #    'Pending Jobs in "%s" have finished, '
                    #    'execute it again to get results' % workflow_item.text(0),
                    #    QtGui.QMessageBox.Ok)
                    # TODO: Only notify user when all cells have finished
                    pass
                elif workflow.version.startswith("Mashup"):
                    QtGui.QMessageBox.information(self, "Job Ready",
                        'Pending Jobs in "%s" have finished, '
                        'execute it again to get results' % workflow_item.text(0),
                        QtGui.QMessageBox.Ok)
                return
            if self.autorun.isChecked():
                jm.startWorkflow(workflow)
                self.updating_now = False
                workflow_item.execute()
                self.updating_now = True
                return
            ret = QtGui.QMessageBox.information(self, "Job Ready",
                    'Pending Jobs in workflow "%s" have finished, '
                    'continue execution now?' % workflow_item.text(0),
                    QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Ok:
                jm.startWorkflow(workflow)
                self.updating_now = False
                workflow_item.execute()
                self.updating_now = True

    def check_jobs(self, job=None):
        if self.updating_now:
            return
        self.updating_now = True
        try:
            if job is None:
                for i in xrange(self.jobView.topLevelItemCount()):
                    vistrail_item = self.jobView.topLevelItem(i)
                    self.update_job(vistrail_item, force=False)
            else:
                self.update_job(job)
        finally:
            self.updating_now = False

    def check_selected_job(self):
        items = self.jobView.selectedItems()
        if len(items) != 1:
            return
        self.check_jobs(items[0])

    def timerEvent(self, id=None):
        self.check_jobs()

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            for item in self.jobView.selectedItems():
                self.delete_item(item)
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def item_clicked(self, item):
        """Item activated.
        """
        if isinstance(item, QWorkflowItem):
            item.goto()

    def delete_item(self, item):
        if isinstance(item, QWorkflowItem):
            item.parent().controller.set_changed(True)
            item.parent().jobMonitor.deleteWorkflow(item.workflow.id)
        elif isinstance(item, QJobItem):
            # find parent workflow
            item.vistrail().controller.set_changed(True)
            item.vistrail().jobMonitor.deleteJob(item.job.id)

class QJobProgressDialog(QtGui.QDialog):
    def __init__(self, job_name, job_start, parent=None, value=0, max_value=100):
        super(QJobProgressDialog, self).__init__(parent)
        f = self.windowFlags()
        f |= QtCore.Qt.CustomizeWindowHint
        f &= ~QtCore.Qt.WindowCloseButtonHint
        self.job_name = job_name
        self.job_start = job_start
        self.was_cancelled = False
        self.was_checked = False
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(max_value)
        self.progressbar.setValue(value)
        self.cancel_button = QtGui.QPushButton('&Cancel')
        self.check_now_button = QtGui.QPushButton('Check &Now')
        self.cancel_button.clicked.connect(lambda :setattr(self,
                                                           'was_cancelled',
                                                           True))
        self.check_now_button.clicked.connect(lambda :setattr(self,
                                                              'was_checked',
                                                              True))
        self.label = QtGui.QLabel()
        self.updateLabel()
        main_layout = QtGui.QGridLayout()
        main_layout.addWidget(self.label, 0, 0, 2, 2)
        main_layout.addWidget(self.progressbar, 2, 0, 1, 2)
        main_layout.addWidget(self.check_now_button, 3, 0)
        main_layout.addWidget(self.cancel_button, 3, 1)
        self.setLayout(main_layout)
        self.setWindowTitle('Running Job')
        self.setWindowModality(QtCore.Qt.WindowModal)

    def updateLabel(self):
        labelText = (("Running external job %s\n"
                               "Started %s\n"
                               "Last checked %s\n"
                               "Press Check Now to check or Cancel to suspend")
                               % (self.job_name,
                                  self.job_start,
                                  QtCore.QDateTime.currentDateTime().toString(
                                      QtCore.Qt.ISODate)))
        self.label.setText(labelText)


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
        changed = False
        if job.id not in workflow_item.jobs:
            workflow_item.jobs[job.id] = QJobItem(job, workflow_item)
            changed = True
        if workflow_item.updateJobs() or changed:
            QJobView.instance().set_visible(True)

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
                if workflow_item.updateJobs():
                    QJobView.instance().set_visible(True)

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
                parent_item = QParentItem(id, module_name(obj.module), base)
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

        workflow_item = self.workflowItems.get(workflow.id, None)
        if workflow_item:
            if workflow_item.updateJobs():
                QJobView.instance().set_visible(True)

    def checkJob(self, module, id, handle):
        """ checkJob(module: VistrailsModule, id: str, handle: object)
        Callback, checks if job has completed.
        """
        workflow = self.jobMonitor.currentWorkflow()
        if not workflow:
            if not self.jobMonitor.isDone(handle):
                raise ModuleSuspended(module, 'Job is running',
                                      handle=handle)
        workflow_item = self.workflowItems[workflow.id]
        item = workflow_item.jobs.get(id, None)
        item.setText(0, item.job.name)
        # we should check the status using the JobHandle and show dialog
        # get current view progress bar and hijack it
        item.handle = handle
        workflow = self.jobMonitor.currentWorkflow()
        workflow_item = self.workflowItems.get(workflow.id, None)
        workflow_item.updateJobs()
        conf = get_vistrails_configuration()
        interval = conf.jobCheckInterval
        is_done = self.jobMonitor.isDone(handle)
        old_progress = self.controller.progress
        if (interval and not conf.jobAutorun and
               not old_progress.suspended and not is_done):
            # wait for module to complete
            old_progress.hide()
            progress = QJobProgressDialog(item.job.name,
                                          item.job.start,
                                          old_progress.parent(),
                                          old_progress.value(),
                                          old_progress.maximum())
            progress.show()
            while not is_done:
                dieTime = QtCore.QDateTime.currentDateTime().addSecs(interval)
                while QtCore.QDateTime.currentDateTime() < dieTime and not is_done:
                    QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 100)
                    if progress.was_checked:
                        progress.check_now_button.setText('Checking')
                        progress.check_now_button.setEnabled(False)
                        progress.cancel_button.setEnabled(False)
                        is_done = self.jobMonitor.isDone(handle)
                        progress.check_now_button.setText('Check &Now')
                        progress.check_now_button.setEnabled(True)
                        progress.cancel_button.setEnabled(True)
                        progress.was_checked = False
                        progress.updateLabel()
                    elif progress.was_cancelled:
                        # this does not work, need to create a new progress dialog
                        #old_progress.goOn()
                        new_progress = old_progress.__class__(old_progress.parent())
                        new_progress.setMaximum(old_progress.maximum())
                        new_progress.setValue(old_progress.value())
                        new_progress.setLabelText(old_progress.labelText())
                        new_progress.setMinimumDuration(0)
                        new_progress.suspended = True
                        self.controller.progress = new_progress
                        old_progress.deleteLater()
                        progress.hide()
                        new_progress.show()
                        QtCore.QCoreApplication.processEvents()
                        raise ModuleSuspended(module,
                                   'Interrupted by user, job'
                                   ' is still running', handle=handle)
                is_done = is_done or self.jobMonitor.isDone(handle)
            # is_done!
            new_progress = old_progress.__class__(old_progress.parent())
            new_progress.setMaximum(old_progress.maximum())
            new_progress.setValue(old_progress.value())
            new_progress.setLabelText(old_progress.labelText())
            new_progress.setMinimumDuration(0)
            new_progress.suspended = True
            self.controller.progress = new_progress
            old_progress.deleteLater()
            progress.hide()
            new_progress.show()
            QtCore.QCoreApplication.processEvents()
            return
        if not is_done:
            raise ModuleSuspended(module, 'Job is running', handle=handle)


class QWorkflowItem(QtGui.QTreeWidgetItem):
    """A workflow with jobs.

       It can reference a workflow version, a parameter exploration workflow,
       or a mashup

    This item can have child module items.
    """
    def __init__(self, workflow, parent):
        QtGui.QTreeWidgetItem.__init__(self, parent, ['', ''])
        self.workflow = workflow
        self.has_handle = True
        # Paused workflows will not be checked by the timer/"Check all" button
        self.paused = False
        self.setIcon(0, theme.get_current_theme().PIPELINE_ICON)
        self.setIcon(1, theme.get_current_theme().JOB_CHECKING)
        self.workflowFinished = False
        self.jobs = {}
        self.intermediates = {}
        self.updateJobs()

    def updateJobs(self):
        """ Updates name and job states
        """
        self.paused = False
        try:
            name = self.parent().controller.get_pipeline_name(
                                                           self.workflow.version)
            self.setToolTip(0, 'Double-Click to View Pipeline "%s" with id %s' %
                               (name, self.workflow.version))
        except KeyError:
            name = self.workflow.version
        self.setText(0, name)
        self.setToolTip(1, "Log id: %s" % self.workflow.id)
        changed = False
        self.has_handle = True
        for job in self.jobs.itervalues():
            if job.updateJob():
                changed = True
            if not job.job.finished and not job.handle:
                self.has_handle = False
        count = len(self.jobs)
        finished = sum([job.job.finished or job.job.ready for job in self.jobs.values()])
        self.setText(1, "(%s/%s)" % (finished, count))
        self.workflowFinished = (finished == count)
        if self.workflowFinished:
            self.setIcon(1, theme.get_current_theme().JOB_FINISHED)
        elif not self.has_handle:
            self.setIcon(1, theme.get_current_theme().JOB_SCHEDULED)
        else:
            self.setIcon(1, theme.get_current_theme().JOB_CHECKING)
        return changed

    def goto(self):
        """ Shows this pipeline

        """
        try:
            int(self.workflow.version)
        except ValueError:
            # this is not a pipeline id
            return
        from vistrails.gui.vistrails_window import _app
        view = _app.getViewFromLocator(self.parent().controller.locator)
        _app.change_view(view)
        view.version_selected(self.workflow.version, True, double_click=True)
        return view

    def execute(self):
        """ Shows and executes this pipeline
        """
        try:
            int(self.workflow.version)
        except ValueError:
            # this is not a pipeline id
            return
        self.goto().execute()

    def pause(self):
        self.paused = True
        self.setIcon(1, theme.get_current_theme().JOB_SCHEDULED)

    def resume(self):
        self.paused = False
        self.setIcon(1, theme.get_current_theme().JOB_CHECKING)

class QJobItem(QtGui.QTreeWidgetItem):
    """A pending job, i.e. a single module that was suspended.

    These will be either under a QWorkflowItem or a QParentItem.
    """
    def __init__(self, job, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [job.name,
                                                      job.description()])
        self.setToolTip(1, job.description())
        self.job = job
        self.handle = None
        self.finished = None
        self.updateJob()

    def updateJob(self):
        changed = self.job.finished != self.finished
        self.finished = self.job.finished
        self.setText(1, self.job.parameters.get('__message__',
                        "Finished" if self.job.finished or self.job.ready else "Running"))
        if self.job.finished or self.job.ready:
            self.setIcon(1, theme.get_current_theme().JOB_FINISHED)
            self.setToolTip(0, "This Job Has Finished")
        elif self.handle:
            self.setIcon(1, theme.get_current_theme().JOB_SCHEDULED)
            self.setToolTip(0, "This Job is Running and Scheduled for Checking")
        else:
            self.setIcon(1, theme.get_current_theme().JOB_CHECKING)
            self.setToolTip(0, "This Job is Running")
        self.setToolTip(1, self.job.id)
        return changed

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

    def workflow(self):
        # find parent workflow
        parent = self.parent()
        while not isinstance(parent, QWorkflowItem):
            parent = parent.parent()
        return parent

    def vistrail(self):
        # find parent vistrail
        return self.workflow().parent()

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


################################################################################
# Testing


class TestJobMonitor(vistrails.gui.utils.TestVisTrailsGUI):

    @classmethod
    def setUpClass(cls):
        get_vistrails_configuration().jobAutorun = True
        get_vistrails_persistent_configuration().jobAutorun = True
        QJobView.instance().set_refresh()
        cls.filename = (vistrails.core.system.vistrails_root_directory() +
                        '/tests/resources/jobs.vt')

        pm = vistrails.core.packagemanager.get_package_manager()
        if pm.has_package('org.vistrails.vistrails.myjobs'):
            return
        d = {'myjob': 'vistrails.tests.resources.'}
        pm.late_enable_package('myjob', d)

    @classmethod
    def tearDownClass(cls):
        manager = vistrails.core.packagemanager.get_package_manager()
        if manager.has_package('org.vistrails.vistrails.myjobs'):
            manager.late_disable_package('myjob')

    def tearDown(self):
        vistrails.gui.utils.TestVisTrailsGUI.tearDown(self)
        from vistrails.core.interpreter.cached import CachedInterpreter
        CachedInterpreter.flush()

    def testSuspended(self):
        from vistrails import api
        view = api.open_vistrail_from_file(self.filename)
        c = view.controller
        api.select_version('SuspendOnce', c)

        result = c.execute_user_workflow()[0][0]
        # assert suspended
        self.assertEqual(result.errors, {})
        self.assertNotEqual(result.suspended, {})

        result = c.execute_user_workflow()[0][0]
        # assert finished
        self.assertEqual(result.errors, {})
        self.assertEqual(result.suspended, {})

        for i in c.jobMonitor.workflows.keys():
            c.jobMonitor.deleteWorkflow(i)

    def testGroup(self):
        from vistrails import api
        view = api.open_vistrail_from_file(self.filename)
        c = view.controller
        api.select_version('SuspendGroup', c)
        result = c.execute_user_workflow()[0][0]

        # assert suspended
        self.assertEqual(result.errors, {})
        self.assertNotEqual(result.suspended, {})

        for i in c.jobMonitor.workflows.keys():
            c.jobMonitor.deleteWorkflow(i)

    def testMap(self):
        from vistrails import api
        view = api.open_vistrail_from_file(self.filename)
        c = view.controller
        api.select_version('SuspendMap', c)

        result = c.execute_user_workflow()[0][0]
        # assert suspended
        self.assertEqual(result.errors, {})
        self.assertNotEqual(result.suspended, {})

        result = c.execute_user_workflow()[0][0]
        # assert finished
        self.assertEqual(result.errors, {})
        self.assertEqual(result.suspended, {})

        for i in c.jobMonitor.workflows.keys():
            c.jobMonitor.deleteWorkflow(i)

    def testLoop(self):
        from vistrails import api
        view = api.open_vistrail_from_file(self.filename)
        c = view.controller
        api.select_version('SuspendLoop', c)

        result = c.execute_user_workflow()[0][0]
        # assert suspended
        self.assertEqual(result.errors, {})
        self.assertNotEqual(result.suspended, {})

        result = c.execute_user_workflow()[0][0]
        # assert finished
        self.assertEqual(result.errors, {})
        self.assertEqual(result.suspended, {})

        for i in c.jobMonitor.workflows.keys():
            c.jobMonitor.deleteWorkflow(i)

    def testParameterExploration(self):
        from vistrails import api
        view = api.open_vistrail_from_file(self.filename)
        c = view.controller
        api.select_version('SuspendOnce', c)

        pe = c.vistrail.get_named_paramexp('SuspendOnce')
        try:
            c.executeParameterExploration(pe)
        except:
            self.fail("Parameter Exploration with Job failed")

        # Check that we have 2 jobs
        self.assertEqual(len(c.jobMonitor.workflows.keys()), 2)
        for i in c.jobMonitor.workflows.keys():
            wf = c.jobMonitor.workflows[i]
            self.assertFalse(wf.completed())

        try:
            c.executeParameterExploration(pe)
        except:
            self.fail("Parameter Exploration with Job failed")

        # Check that the 2 jobs has completed
        for i in c.jobMonitor.workflows.keys():
            wf = c.jobMonitor.workflows[i]
            self.assertTrue(wf.completed())

        for i in c.jobMonitor.workflows.keys():
            c.jobMonitor.deleteWorkflow(i)

    def testMashup(self):
        from vistrails import api
        view = api.open_vistrail_from_file(self.filename)
        c = view.controller

        c.flush_delayed_actions()
        id = "80f58f50-57b1-11e5-a1da-000c2960b7d8"
        mashup = view.get_mashup_from_mashuptrail_id(id, "SuspendOnce")
        self.assert_(mashup)

        view.open_mashup(mashup)
        self.assertEqual(len(c.jobMonitor.workflows.keys()), 1)
        self.assertFalse(c.jobMonitor.workflows.values()[0].completed())

        # close associated mashup apps
        from vistrails.gui.version_prop import QVersionProp
        version_prop = QVersionProp.instance()
        for app in version_prop.versionMashups.apps.values():
            app.close()

        view.open_mashup(mashup)
        self.assertEqual(len(c.jobMonitor.workflows.keys()), 1)
        self.assertTrue(c.jobMonitor.workflows.values()[0].completed())

        for i in c.jobMonitor.workflows.keys():
            c.jobMonitor.deleteWorkflow(i)
