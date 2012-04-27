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
from module_palette import JModulePalette
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
        self.current_view = None
        
        self.contentPanel = JPanel(BorderLayout())
        self.setContentPane(self.contentPanel)
        root = str(core.system.vistrails_root_directory())
        toolBar = JToolBar()

        # Create and add the different buttons
        def addButton(image, tooltip, text):
            iconFile = root + "/gui/resources/images/" + image
            icon = ImageIcon(iconFile)
            button = JButton(icon)
            button.actionPerformed = self.buttonClicked
            button.setToolTipText(tooltip)
            button.setVerticalTextPosition(SwingConstants.BOTTOM)
            button.setHorizontalTextPosition(SwingConstants.CENTER)
            button.setText(text)
            toolBar.add(button)
            return button

        self.openButton = addButton('open_vistrail.png', "Open", "Open")
        self.executeButton = addButton(
                'execute.png', "Execute the current pipeline", "Execute")
        self.pipelineButton = addButton('pipeline.png',
                                        "Switch to pipeline view", "Pipeline")
        self.historyButton = addButton('history.png',
                                       "Switch to version view", "Version")

        self.contentPanel.add(toolBar, BorderLayout.NORTH)
        
        # Create the module palette
        self.modulepalette = JModulePalette()
        self.contentPanel.add(self.modulepalette, BorderLayout.WEST)
        # TODO : scrollbar for the palette!

    def showFrame(self):
        self.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
        self.setSize(300, 300)
        self.setVisible(True)
    
    def link_registry(self):
        self.modulepalette.link_registry()

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
        self.set_current_view(self.pipelineView)

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
