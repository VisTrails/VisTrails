###############################################################################
##
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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

import sys

# This can't stay here
sys.path.append('../../piccolo/piccolo2d-core-1.3.1.jar')
sys.path.append('../../piccolo/piccolo2d-extras-1.3.1.jar')

from vistrail_controller import JVistrailController
from pipeline_view import JPipelineView
from version_view import JVersionVistrailView
from core.db.locator import ZIPFileLocator
from core.db.io import load_vistrail
import core.packagemanager
import core.application
import core.system

from javax.swing import ImageIcon
from javax.swing import JFileChooser
from javax.swing import JFrame
from javax.swing import JMenu
from javax.swing import JMenuBar
from javax.swing import JMenuItem
from javax.swing import JToolBar
from javax.swing import JButton
from javax.swing import JPanel
from javax.swing import SwingConstants
from java.awt import BorderLayout


class BuilderFrame(JFrame):
    """The window, used to edit a vistrail.

    It is the main class of the GUI, it creates and updates the views.

    """
    def __init__(self):
        self.title = "Vistrails running on Jython"
        self.setTitle(self.title)
        self.filename = ""
        self.currentLocator = None
        menuBar = JMenuBar()
        fileMenu = JMenu("File")
        self.openItem = JMenuItem("Open a file")
        self.openItem.actionPerformed = self.openAction
        fileMenu.add(self.openItem)
        menuBar.add(fileMenu)
        self.setJMenuBar(menuBar)
        core.application.init()

    def showFrame(self):
        self.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
        self.setSize(300, 300)
        self.show()

    def open_vistrail(self, fileName):
        # This part is identical with the Python/Qt version
        locator = ZIPFileLocator(fileName)
        if locator:
            if hasattr(locator, '_vnode'):
                version = locator._vnode
                if hasattr(locator,'_vtag'):
                    # if a tag is set, it should be used instead of the
                    # version number
                    if locator._vtag != '':
                        version = locator._vtag
            self.currentLocator = locator
            self.open_vistrail_without_prompt(locator, version)

    def set_current_view(self, view):
        if view != self.current_view:
            if self.current_view != None:
                self.contentPanel.remove(self.current_view)
            self.contentPanel.add(view, BorderLayout.CENTER)
            self.current_view = view

            self.contentPanel.revalidate() # Needed when using remove()
            self.repaint()

    def open_vistrail_without_prompt(self, locator, version = None):
        self.current_view = None
        self.controller = JVistrailController()
        self.currentVersion = "-1"

        # Open the vistrail
        (vistrail, abstractions, thumbnails, mashups) = \
                load_vistrail(self.currentLocator, False)

        # Initialize the controller
        self.controller.set_vistrail(
                vistrail, self.currentLocator, abstractions, thumbnails)

        # Create the pipeline view
        self.pipelineView = JPipelineView(
                vistrail, locator, self.controller,
                abstractions, thumbnails)

        # Create the version view
        self.versionView = JVersionVistrailView(
                vistrail, locator, self.controller,
                abstractions, thumbnails)

        # Setup the view (pipeline by default)
        self.contentPanel = JPanel(BorderLayout())
        self.set_current_view(self.pipelineView)
        toolBar = JToolBar()
        root = str(core.system.vistrails_root_directory())

        # Create and add the different buttons
        openIconFile = root + "/gui/resources/images/open_vistrail.png"
        openIcon = ImageIcon(openIconFile)
        self.openButton = JButton(openIcon)
        self.openButton.actionPerformed = self.buttonClicked
        self.openButton.setToolTipText("Open")
        self.openButton.setVerticalTextPosition(SwingConstants.BOTTOM);
        self.openButton.setHorizontalTextPosition(SwingConstants.CENTER);
        self.openButton.setText("Open")
        executeIconFile = root + "/gui/resources/images/execute.png"
        executeIcon = ImageIcon(executeIconFile)
        self.executeButton = JButton(executeIcon)
        self.executeButton.actionPerformed = self.buttonClicked
        self.executeButton.setToolTipText("Execute the current pipeline")
        self.executeButton.setVerticalTextPosition(SwingConstants.BOTTOM);
        self.executeButton.setHorizontalTextPosition(SwingConstants.CENTER);
        self.executeButton.setText("Execute")
        pipelineIconFile = root + "/gui/resources/images/pipeline.png"
        pipelineIcon = ImageIcon(pipelineIconFile)
        self.pipelineButton = JButton(pipelineIcon)
        self.pipelineButton.actionPerformed = self.buttonClicked
        self.pipelineButton.setToolTipText("Switch to pipeline view")
        self.pipelineButton.setVerticalTextPosition(SwingConstants.BOTTOM);
        self.pipelineButton.setHorizontalTextPosition(SwingConstants.CENTER);
        self.pipelineButton.setText("Pipeline")
        historyIconFile = root + "/gui/resources/images/history.png"
        historyIcon = ImageIcon(historyIconFile)
        self.historyButton = JButton(historyIcon)
        self.historyButton.setToolTipText("Switch to version view")
        self.historyButton.actionPerformed = self.buttonClicked
        self.historyButton.setVerticalTextPosition(SwingConstants.BOTTOM);
        self.historyButton.setHorizontalTextPosition(SwingConstants.CENTER);
        self.historyButton.setText("Version")
        toolBar.add(self.openButton)
        toolBar.add(self.executeButton)
        toolBar.add(self.pipelineButton)
        toolBar.add(self.historyButton)
        self.contentPanel.add(toolBar, BorderLayout.NORTH)
        self.setContentPane(self.contentPanel)

    def buttonClicked(self, event):
        if (event.getSource() == self.pipelineButton):
            self.set_current_view(self.pipelineView)
        elif (event.getSource() == self.historyButton):
            self.set_current_view(self.versionView)
        elif (event.getSource() == self.executeButton):
            self.pipelineView.execute_workflow()
            return
        elif (event.getSource() == self.openButton):
            self.openAction(event)
            return

    def openAction(self, event):
        fileChooser = JFileChooser()
        returnedValue = fileChooser.showOpenDialog(self.openItem)
        if (returnedValue == JFileChooser.APPROVE_OPTION):
            filename = fileChooser.getSelectedFile()
            print filename.getAbsolutePath()
            self.open_vistrail(filename.getAbsolutePath())
            self.getContentPane().getComponent(1).invalidate()
            self.getContentPane().getComponent(1).revalidate()
            self.getContentPane().getComponent(1).repaint()

frame = BuilderFrame()

def load_module_if_req(codepath):
    package_manager = core.packagemanager.get_package_manager()
    try:
        package_manager.get_package_by_codepath(codepath)
    except core.packagemanager.PackageManager.MissingPackage:
        print "Loading package '%s'..." % codepath
        try:
            package_manager.late_enable_package(codepath)
            print "Loading complete"
        except core.packagemanager.PackageManager.MissingPackage, e:
            sys.stderr.write("Unable to load package '%s':" % codepath, str(e), "\n")
    else:
        print "Package '%s' had already been loaded automatically" % codepath

load_module_if_req('obvioustest')

frame.open_vistrail("C:/Documents and Settings/remirampin/Mes documents/obvious.vt")
frame.showFrame()
