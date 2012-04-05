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

from view_manager import JViewManager
from core.db.locator import ZIPFileLocator
from core.modules.module_registry import ModuleRegistry
from core.packagemanager import PackageManager
import core.modules
import core.system
import sys

class BuilderFrame(JFrame):
    
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
        self.viewManager = JViewManager()
        self.currentVersion = "-1"
        self.clickedVersionNodeId = -1
        core.application.init()
        configuration = core.configuration.default()
        """self.vistrailsStartup = core.startup.VistrailsStartup(
             configuration)
        self.vistrailsStartup.set_registry()"""

    
    def showFrame(self):
        self.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
        self.setSize(300, 300)
        self.show()
            
    def open_vistrail(self, fileName):
        """ This part is identical with the PythonC version """
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

    
    def open_vistrail_without_prompt(self, locator, version = None):
        self.viewComp = self.viewManager.open_vistrail(self.currentLocator, None, None, False, self)
        self.contentPanel = JPanel(BorderLayout())
        self.contentPanel.add(self.viewComp, BorderLayout.CENTER)
        toolBar = JToolBar()
        root = str(core.system.vistrails_root_directory())
        #Create and add the different buttons
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
        self.pipelineButton.actionPerformed= self.buttonClicked
        self.pipelineButton.setToolTipText("Switch to pipeline view")
        self.pipelineButton.setVerticalTextPosition(SwingConstants.BOTTOM);
        self.pipelineButton.setHorizontalTextPosition(SwingConstants.CENTER);
        self.pipelineButton.setText("Pipeline")
        historyIconFile = root + "/gui/resources/images/history.png"
        historyIcon = ImageIcon(historyIconFile)
        self.historyButton = JButton(historyIcon)
        self.historyButton.setToolTipText("Switch to version view")
        self.historyButton.actionPerformed= self.buttonClicked
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
            viewCompTemp = self.viewManager.open_vistrail(self.currentLocator, "pipeline", None, False, self)
        elif (event.getSource() == self.historyButton):
            viewCompTemp = self.viewManager.open_vistrail(self.currentLocator, "version", None, False, self)
        elif (event.getSource() == self.executeButton):
            from vistrail_view import JVistrailView
            if str(self.viewManager.vistrailView.__class__) == "<class 'vistrail_view.JVistrailView'>":
                viewCompTemp = self.viewManager.vistrailView
                viewCompTemp.execute_workflow()
                return
            else:
                viewCompTemp = self.viewManager.open_vistrail(self.currentLocator, "pipeline", None, False, self)
                viewCompTemp.execute_workflow()
        elif (event.getSource() == self.openButton):
            self.openAction(event)
            return
        self.getContentPane().remove(self.viewComp)
        self.getContentPane().invalidate()
        self.getContentPane().revalidate()
        self.getContentPane().repaint()
        self.viewComp = viewCompTemp
        self.getContentPane().add(self.viewComp, BorderLayout.CENTER)
        self.getContentPane().getComponent(1).invalidate()
        self.getContentPane().getComponent(1).revalidate()
        self.getContentPane().getComponent(1).repaint()
        
    def openAction(self, event):
        fileChooser = JFileChooser()
        returnedValue = fileChooser.showOpenDialog(self.openItem)
        if (returnedValue == JFileChooser.APPROVE_OPTION):
            file = fileChooser.getSelectedFile()
            print file.getAbsolutePath()
            self.open_vistrail(file.getAbsolutePath())
            self.getContentPane().getComponent(1).invalidate()
            self.getContentPane().getComponent(1).revalidate()
            self.getContentPane().getComponent(1).repaint()

frame = BuilderFrame()
frame.open_vistrail("C:/Program Files/VisTrails/examples/terminator.vt")
frame.showFrame()

