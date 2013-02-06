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

from core import debug
from gui.vistrails_palette import QVistrailsPaletteInterface
from gui import theme

class QJobView(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.timer_id = None

        self.workflowItems = {}
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.setMargin(5)
        buttonsLayout.setSpacing(5)
        label = QtGui.QLabel('Refresh interval:')
        buttonsLayout.addWidget(label)
        button_group = QtGui.QButtonGroup()
        refresh_states = [('Off', 0), ('10 sec', 10),
                          ('1 min', 60), ('10 min', 600),
                          ('1 hour', 3600)]
        for text, seconds in refresh_states:
            button = QtGui.QRadioButton(text)
            button_group.addButton(button)
            buttonsLayout.addWidget(button)
            def make_callback(p):
                return lambda: self.set_refresh(p)
            button.clicked.connect(make_callback(seconds))
            if seconds == 0:
                button.setChecked(True)
        buttonsLayout.addStretch(1000000)
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
        # changes the timer time
        if refresh:
            if self.timer_id is not None:
                self.killTimer(self.timer_id)
            self.timer_id = self.startTimer(refresh*1000)
        else:
            if self.timer_id:
                self.killTimer(self.timer_id)
                self.timer_id = None
                
    def update_jobs(self):
        # check all jobs
        state_icons = [theme.get_current_theme().JOB_SCHEDULED,
                       theme.get_current_theme().JOB_FINISHED]
 
        for workflow in self.workflowItems.itervalues():
            if workflow.workflowFinished:
                continue
            workflow.setIcon(0, theme.get_current_theme().JOB_CHECKING)
            for job in workflow.jobs.itervalues():
                if job.jobFinished:
                    continue
                job.setIcon(0, theme.get_current_theme().JOB_CHECKING)
                # call queue
                job.jobFinished = job.queue.finished().val()
                job.setIcon(0, state_icons[job.jobFinished])
                workflow.countJobs()
            workflow.workflowFinished = len(workflow.jobs) == \
                         sum(j.jobFinished for j in workflow.jobs.itervalues())
            workflow.setIcon(0, state_icons[workflow.workflowFinished])
            workflow.countJobs()
            if workflow.workflowFinished:
                ret = QtGui.QMessageBox.information(self, "Job Ready",
                        'Pending Jobs in workflow "%s" has finished, do you want '
                        'to continue the execution now?' % workflow.name,
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                if ret == QtGui.QMessageBox.Ok:
                    workflow.execute()

    def timerEvent(self, id):
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
                    self.jobView.takeTopLevelItem(index)
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def add_job(self, controller, error, prev='', workflow=None):
        """ Adds job recursively """
        added = False
        if not prev:
            name = controller.vistrail.locator.short_name
            version_id = controller.current_version
            if (name, version_id) not in self.workflowItems:
                workflow = QWorkflowItem(controller, error, self.jobView)
                self.jobView.addTopLevelItem(workflow)
                self.workflowItems[(name, version_id)] = workflow
            else:
                workflow = self.workflowItems[(name, version_id)]
        job_name = ((prev+'.') if prev else '') + error.module.__class__.__name__

        if not error.children:
            if not error.queue:
                return False
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
                        
    def delete_job(self, controller):
        name = controller.vistrail.locator.short_name
        version_id = controller.current_version
        if (name, version_id) in self.workflowItems:
            self.jobView.takeTopLevelItem(
                self.jobView.indexOfTopLevelItem(
                    self.workflowItems[(name, version_id)]))
        self.updating_now = False

    def item_selected(self, item):
        if type(item) == QWorkflowItem:
            item.goto()

class QWorkflowItem(QtGui.QTreeWidgetItem):
    """ The workflow that was suspended """
    def __init__(self, controller, error, parent):
        self.name = "%s:%s" % (controller.vistrail.locator.short_name,
                                controller.get_pipeline_name()[10:])
        QtGui.QTreeWidgetItem.__init__(self, parent,
                    [self.name, error if type(error)==str else error.msg])
        self.controller = controller
        self.version = controller.current_version
        self.setIcon(0, theme.get_current_theme().JOB_SCHEDULED)
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
        from gui.vistrails_window import _app
        _app.change_view(self.view)
        self.view.version_selected(self.version, True, double_click=True)
        self.view.execute()

class QJobItem(QtGui.QTreeWidgetItem):
    """ The module that was suspended """
    def __init__(self, name, error, parent=None):
        QtGui.QTreeWidgetItem.__init__(self, parent, [name, error.msg])
        self.queue = error.queue
        self.setIcon(0, theme.get_current_theme().JOB_SCHEDULED)
        self.jobFinished = False
