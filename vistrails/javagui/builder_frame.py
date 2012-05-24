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
from preference_window import PreferenceWindow
from core.db.locator import ZIPFileLocator, DBLocator, FileLocator, \
        untitled_locator
from core.db.io import load_vistrail
from core.vistrail.vistrail import Vistrail
from core import debug
from core.thumbnails import ThumbnailCache
import core.system

from javax.swing import ImageIcon, JFileChooser, JFrame, JToolBar, JPanel
from javax.swing import JMenu, JMenuBar, JMenuItem, JButton, SwingConstants
from javax.swing import JSplitPane

from java.awt import BorderLayout
from java.lang import System

from extras.core.db.javagui.locator import JavaLocatorHelperProvider


class BuilderFrame(JFrame):
    """The window, used to edit a vistrail.

    It is the main class of the GUI, it creates and updates the views.
    """
    def __init__(self):
        self.title = "Vistrails running on Jython"
        self.setTitle(self.title)
        self.filename = ""
        self.currentLocator = None
        self.dbDefault = False
        menuBar = JMenuBar()
        fileMenu = JMenu("File")
        openItem = JMenuItem("Open a file")
        openItem.actionPerformed = self.openAction
        fileMenu.add(openItem)
        fileMenu.addSeparator()
        quitItem = JMenuItem("Quit")
        quitItem.actionPerformed = self.quitAction
        fileMenu.add(quitItem)
        menuBar.add(fileMenu)
        editMenu = JMenu("Edit")
        preferencesItem = JMenuItem("Preferences...")
        preferencesItem.actionPerformed = self.showPreferences
        editMenu.add(preferencesItem)
        menuBar.add(editMenu)
        self.setJMenuBar(menuBar)
        self.current_view = None

        self.preferenceWindow = PreferenceWindow(self)

        top = JPanel(BorderLayout())
        self.setContentPane(top)
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

        self.saveButton = addButton('save_vistrail.png',
                                    "Save changes", "Save")
        self.saveAsButton = addButton('save_vistrail.png',
                                    "Select a file to save to", "Save as...")
        self.openButton = addButton('open_vistrail.png', "Open", "Open")
        self.executeButton = addButton(
                'execute.png', "Execute the current pipeline", "Execute")
        self.pipelineButton = addButton('pipeline.png',
                                        "Switch to pipeline view", "Pipeline")
        self.historyButton = addButton('history.png',
                                       "Switch to version view", "Version")

        top.add(toolBar, BorderLayout.NORTH)
        
        self.contentPanel = JSplitPane(JSplitPane.HORIZONTAL_SPLIT)
        top.add(self.contentPanel)

        # Create the module palette
        self.modulepalette = JModulePalette()
        self.contentPanel.setLeftComponent(self.modulepalette)
        self.contentPanel.setDividerLocation(200)

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
            self.contentPanel.setRightComponent(view)
            self.current_view = view

            self.contentPanel.revalidate() # Needed when using remove()
            self.repaint()

    def flush_changes(self):
        self.pipelineView.flushMoveActions()

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
        if event.getSource() == self.pipelineButton:
            self.set_current_view(self.pipelineView)
        elif event.getSource() == self.historyButton:
            self.set_current_view(self.versionView)
        elif event.getSource() == self.executeButton:
            self.pipelineView.execute_workflow()
            return
        elif event.getSource() == self.openButton:
            self.openAction()
            return
        elif event.getSource() == self.saveButton:
            self.saveAction()
            return
        elif event.getSource() == self.saveAsButton:
            self.saveAsAction()
            return

    def openAction(self, event=None):
        fileChooser = JFileChooser()
        returnedValue = fileChooser.showOpenDialog(self)
        if (returnedValue == JFileChooser.APPROVE_OPTION):
            filename = fileChooser.getSelectedFile()
            print filename.getAbsolutePath()
            self.open_vistrail(filename.getAbsolutePath())
            self.getContentPane().getComponent(1).invalidate()
            self.getContentPane().getComponent(1).revalidate()
            self.getContentPane().getComponent(1).repaint()

    def saveAction(self, event=None):
        if self.dbDefault:
            self.save_vistrail(DBLocator)
        else:
            self.save_vistrail(FileLocator())

    def saveAsAction(self, event=None):
        if self.dbDefault:
            locator = self.save_vistrail(DBLocator,
                                         force_choose_locator=True)
        else:
            locator = self.save_vistrail(FileLocator(),
                                         force_choose_locator=True)

        self.currentLocator = locator

    def save_vistrail(self, locator_class, force_choose_locator=False):
        self.flush_changes()
        if force_choose_locator:
            locator = locator_class.save_from_gui(
                    JavaLocatorHelperProvider(self),
                    Vistrail.vtType,
                    self.controller.locator)
        else:
            locator = self.controller.locator or \
                    locator_class.save_from_gui(
                            JavaLocatorHelperProvider(self),
                            Vistrail.vtType,
                            self.controller.locator)

        if locator == untitled_locator():
            locator = locator_class.save_from_gui(
                    JavaLocatorHelperProvider(self),
                    Vistrail.vtType,
                    self.controller.locator)

        # if couldn't get one, ignore the request
        if not locator:
            return False

        # update collection
        try:
            self.controller.write_vistrail(locator)
        except Exception, e:
            debug.critical('An error has occurred', str(e))
            raise
            return False
        try:
            from core.collection import Collection
            thumb_cache = ThumbnailCache.getInstance()
            self.controller.vistrail.thumbnails = \
                self.controller.find_thumbnails(
                    tags_only=thumb_cache.conf.tagsOnly)
            self.controller.vistrail.abstractions = \
                self.controller.find_abstractions(
                    self.controller.vistrail, True)

            collection = Collection.getInstance()
            url = locator.to_url()
            # create index if not exist
            entity = collection.fromUrl(url)
            if entity:
                # find parent vistrail
                while entity.parent:
                    entity = entity.parent
            else:
                entity = collection.updateVistrail(url, self.controller.vistrail)
            # add to relevant workspace categories
            collection.add_to_workspace(entity)
            collection.commit()
        except Exception, e:
            debug.critical('Failed to index vistrail', str(e))
        return locator

    def quitAction(self, event=None):
        System.exit(0)

    def showPreferences(self, event=None):
        self.preferenceWindow.setVisible(True)
