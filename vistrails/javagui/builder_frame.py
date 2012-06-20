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
import threading
import copy

# This can't stay here
sys.path.append('../../piccolo/piccolo2d-core-1.3.1.jar')
sys.path.append('../../piccolo/piccolo2d-extras-1.3.1.jar')
sys.path.append('../../vldocking/vldocking_3.0.0.jar')

from vistrail_controller import JVistrailController
from pipeline_view import JPipelineView
from version_view import JVersionVistrailView
from module_palette import JModulePalette
from module_info import JModuleInfo
from preference_window import PreferenceWindow
from core.db.locator import ZIPFileLocator, DBLocator, FileLocator, \
        untitled_locator
from core.db.io import load_vistrail
from core.vistrail.vistrail import Vistrail
from core import debug
from core.thumbnails import ThumbnailCache
import core.system

from javax.swing import ImageIcon, JFileChooser, JFrame, JToolBar, JPanel
from javax.swing import JMenu, JMenuBar, JMenuItem, JButton
from javax.swing import SwingConstants, SwingUtilities

from java.awt import BorderLayout, Color
from java.awt.event import WindowAdapter

from com.vlsolutions.swing.docking import DockingDesktop, DockingConstants,\
    DockKey, Dockable, DockGroup

from extras.core.db.javagui.locator import JavaLocatorHelperProvider


class CloseListener(WindowAdapter):
    def __init__(self, frame):
        self._frame = frame

    # @Override
    def windowClosing(self, e):
        self._frame.setVisible(False)
        self.closed()

    def closed(self):
        self._frame._visibleCond.acquire()
        self._frame._visibleCond.notifyAll()
        self._frame._visibleCond.release()
        # This will only kill the current thread: AWT's Event Dispatch Thread
        sys.exit(0)
        # We need to kill it so that the application can exit, as sys.exit() in
        # the main thread will join() all the remaining threads
        # (this is different from Java's System.exit())


class BuilderFrame(JFrame):
    """The window, used to edit a vistrail.

    It is the main class of the GUI, it creates and updates the views.
    """
    PANELS = DockGroup("panels")
    CONTENT = DockGroup("content")

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

        self.desktop = DockingDesktop()

        top.add(self.desktop)

        # Empty view
        class EmptyView(JPanel, Dockable):
            def __init__(self, group):
                self._key = DockKey("(empty)")
                self._key.setDockGroup(group)
                self._key.setResizeWeight(1.0)

            # @Override
            def getDockKey(self):
                return self._key

            # @Override
            def getComponent(self):
                return self

            # @Override
            def getBackground(self):
                return Color.green

            def flushMoveActions(self): pass
            def execute_workflow(self): pass

        self.current_view = EmptyView(BuilderFrame.CONTENT)
        self.desktop.addDockable(self.current_view)
        self.pipelineView = self.current_view
        self.versionView = self.current_view

        # Create the module palette
        self.modulepalette = JModulePalette()
        self.modulepalette.getDockKey().setDockGroup(BuilderFrame.PANELS)
        self.modulepalette.getDockKey().setResizeWeight(0.2)
        self.desktop.split(self.current_view, self.modulepalette, DockingConstants.SPLIT_LEFT)

        # Create the module info panel
        self.moduleInfo = JModuleInfo()
        self.moduleInfo.getDockKey().setDockGroup(BuilderFrame.PANELS)
        self.moduleInfo.getDockKey().setResizeWeight(0.2)
        self.desktop.split(self.current_view, self.moduleInfo, DockingConstants.SPLIT_RIGHT)

        self._visibleCond = threading.Condition()

        self._windowCloseListener = CloseListener(self)
        self.addWindowListener(self._windowCloseListener)

    def showFrame(self):
        self.setSize(300, 300)
        self.setVisible(True)

    def link_registry(self):
        self.modulepalette.link_registry()

    def open_vistrail(self, fileName):
        # This part is identical with the Python/Qt version
        if isinstance(fileName, basestring):
            locator = ZIPFileLocator(fileName)
        else:
            locator = fileName
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
            self.desktop.addDockable(view)
            self.desktop.close(view)
            self.desktop.replace(self.current_view, view)
            self.current_view = view

    def flush_changes(self):
        self.pipelineView.flushMoveActions()

    def create_first_vistrail(self):
        if self.current_view:
            return
        if untitled_locator().has_temporaries():
            if not FileLocator().prompt_autosave(
                    JavaLocatorHelperProvider(self)):
                untitled_locator().clean_temporaries()
        self.new_vistrail(True)

    def new_vistrail(self, recover_files=False):
        if recover_files and untitled_locator().has_temporaries():
            locator = copy.copy(untitled_locator())
        else:
            locator = None

        self.open_vistrail_without_prompt(locator)

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
        self.pipelineView.getDockKey().setDockGroup(BuilderFrame.CONTENT)
        self.pipelineView.getDockKey().setResizeWeight(1.0)

        # Create the version view
        self.versionView = JVersionVistrailView(
                vistrail, locator, self.controller,
                abstractions, thumbnails)
        self.versionView.getDockKey().setDockGroup(BuilderFrame.CONTENT)
        self.versionView.getDockKey().setResizeWeight(1.0)

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
                entity = collection.updateVistrail(url,
                                                   self.controller.vistrail)
            # add to relevant workspace categories
            collection.add_to_workspace(entity)
            collection.commit()
        except Exception, e:
            debug.critical('Failed to index vistrail', str(e))
        return locator

    def quitAction(self, event=None):
        self.setVisible(False)
        self._windowCloseListener.closed()

    def showPreferences(self, event=None):
        self.preferenceWindow.setVisible(True)

    def waitClose(self):
        """Wait for the window to close.
        """
        assert not SwingUtilities.isEventDispatchThread()
        self._visibleCond.acquire()
        self._visibleCond.wait()
        while self.isVisible():
            self._visibleCond.wait()
        self._visibleCond.release()
