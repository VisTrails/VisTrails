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

"""The builder frame is the main window of VisTrails.

It contains the pipeline view and its associated panels, the version view, a
menu bar and various buttons.
It terminates Swing's Event Dispatch Thread when closed, and uses a condition
to pause Jython's main thread while running (see waitClose()).
"""

import copy
import sys
import threading

from java.awt import BorderLayout
from java.awt.event import WindowAdapter
from javax.swing import ImageIcon, JFileChooser, JFrame, JOptionPane, \
    JPanel, JToolBar
from javax.swing import JMenu, JMenuBar, JMenuItem, JButton
from javax.swing import SwingConstants, SwingUtilities

from com.vlsolutions.swing.docking import Dockable, DockGroup, \
    DockingConstants, DockingDesktop, DockKey

from core.db.locator import ZIPFileLocator, DBLocator, FileLocator, \
        untitled_locator
from core.db.io import load_vistrail
from core.vistrail.vistrail import Vistrail
from core import debug, get_vistrails_application
from core.thumbnails import ThumbnailCache
import core.interpreter.cached
import core.system
from db.services.locator import BaseLocator
from extras.db.javagui.locator import JavaLocatorHelperProvider
from javagui.module_info import JModuleInfo
from javagui.module_palette import JModulePalette
from javagui.pipeline_view import JPipelineView
from javagui.preference_window import PreferenceWindow
from javagui.version_view import JVersionView
from javagui.vistrail_controller import JVistrailController
from javagui.vistrail_holder import VistrailHolder


class CloseListener(WindowAdapter):
    def __init__(self, frame):
        self._frame = frame

    # @Override
    def windowClosing(self, e):
        self.closed()

    def closed(self):
        if self._frame.closing():
            self._frame.setVisible(False)
            # This will only kill the current thread: AWT's Event Dispatch
            # Thread
            sys.exit(0)
            # We need to kill it so that the application can exit, as
            # sys.exit() in the main thread will join() all the remaining
            # threads (this is different from Java's System.exit())


class DockableContainer(JPanel, Dockable):
    def __init__(self, key, close_enabled=False, weight=1.0):
        self._key = DockKey(key)
        self._key.setResizeWeight(weight)
        self._key.setCloseEnabled(close_enabled)

        self.setLayout(BorderLayout())

    # @Override
    def getDockKey(self):
        return self._key

    # @Override
    def getComponent(self, *args):
        if len(args) == 0:
            return self
        else:
            return JPanel.getComponent(self, *args)

    def change_content(self, widget):
        self.removeAll()
        if widget is not None:
            self.add(widget)
        self.revalidate()


class BuilderFrame(JFrame):
    """The window, used to edit a vistrail.

    It is the main class of the GUI, it creates and updates the views.
    """
    PANELS = DockGroup("panels")
    CONTENT = DockGroup("content")

    def __init__(self):
        self.title = "Vistrails running on Jython"
        self.setTitle(self.title)
        self.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE)

        self.filename = ""
        self.dbDefault = False

        # The vistrails that are currently opened
        self._opened_vistrails = VistrailHolder()

        # The menu bar
        menuBar = JMenuBar()

        fileMenu = JMenu("File")
        self.openMenuItem = JMenuItem("Open a file")
        self.openMenuItem.actionPerformed = self.openAction
        fileMenu.add(self.openMenuItem)
        fileMenu.addSeparator()

        quitItem = JMenuItem("Quit")
        quitItem.actionPerformed = self.quitAction
        fileMenu.add(quitItem)
        menuBar.add(fileMenu)

        editMenu = JMenu("Edit")
        self.preferencesMenuItem = JMenuItem("Preferences...")
        self.preferencesMenuItem.actionPerformed = self.showPreferences
        editMenu.add(self.preferencesMenuItem)
        menuBar.add(editMenu)

        workflowMenu = JMenu("Workflow")
        self.executeMenuItem = JMenuItem("Execute")
        self.executeMenuItem.actionPerformed = self.executeAction
        workflowMenu.add(self.executeMenuItem)
        eraseCacheItem = JMenuItem("Erase cache contents")
        eraseCacheItem.actionPerformed = self.erase_cache
        workflowMenu.add(eraseCacheItem)
        menuBar.add(workflowMenu)

        menuBar.add(self._setup_packages_menu())

        menuBar.add(self._opened_vistrails.create_jmenu(self.select_vistrail))

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

        top.add(toolBar, BorderLayout.NORTH)

        self.desktop = DockingDesktop()

        top.add(self.desktop)

        self._controller = None
        self.first_controller = None

        # Create the pipeline dockable, with no pipeline view at the moment
        self.pipelineView = None
        self.pipeline_dockable = DockableContainer('pipeline')
        self.pipeline_dockable.getDockKey().setDockGroup(BuilderFrame.CONTENT)
        self.desktop.addDockable(self.pipeline_dockable)

        # Create the version dockable, with no version view at the moment
        self.versionView = None
        self.version_dockable = DockableContainer('version')
        self.version_dockable.getDockKey().setDockGroup(BuilderFrame.CONTENT)
        self.desktop.createTab(self.pipeline_dockable, self.version_dockable,
                               1, False)

        # These actions are impossible without a vistrail
        self.saveButton.setEnabled(False)
        self.saveAsButton.setEnabled(False)
        self.executeButton.setEnabled(False)
        self.executeMenuItem.setEnabled(False)

        # Create the module palette
        self.modulepalette = JModulePalette()
        self.modulepalette.getDockKey().setDockGroup(BuilderFrame.PANELS)
        self.modulepalette.getDockKey().setResizeWeight(0.2)
        self.modulepalette.getDockKey().setCloseEnabled(False)
        self.desktop.split(self.pipeline_dockable, self.modulepalette,
                           DockingConstants.SPLIT_LEFT)

        # Create the module info panel
        self.moduleInfo = JModuleInfo()
        self.moduleInfo.getDockKey().setDockGroup(BuilderFrame.PANELS)
        self.moduleInfo.getDockKey().setResizeWeight(0.2)
        self.moduleInfo.getDockKey().setCloseEnabled(False)
        self.desktop.split(self.pipeline_dockable, self.moduleInfo,
                           DockingConstants.SPLIT_RIGHT)

        self._visibleCond = threading.Condition()

        self._windowCloseListener = CloseListener(self)
        self.addWindowListener(self._windowCloseListener)

    def _setup_packages_menu(self):
        self.packages_menu = JMenu("Packages")
        self.packages_menu_items = dict()

        def add_package_menu(pkg_id, pkg_name, items):
            try:
                menu = self.packages_menu_items[pkg_id]
            except KeyError:
                pass
            else:
                self.packages_menu.remove(menu)
                del self.packages_menu_items[pkg_id]
            menu = JMenu(pkg_name)
            def wrap(f):
                def wrapped(event=None):
                    return f()
                return wrapped
            for caption, action in items:
                item = JMenuItem(caption)
                item.actionPerformed = wrap(action)
                menu.add(item)
            self.packages_menu.add(menu)
            self.packages_menu_items[pkg_id] = menu

        def remove_package_menu(pkg_id):
            self.packages_menu.remove(self.packages_menu_items[pkg_id])
            del self.packages_menu_items[pkg_id]

        app = get_vistrails_application()
        app.register_notification('pm_add_package_menu',
                                  add_package_menu)
        app.register_notification('pm_remove_package_menu',
                                  remove_package_menu)

        return self.packages_menu

    def showFrame(self):
        self.setSize(650, 500)
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

            try:
                controller = self._opened_vistrails.find_controller(locator)
            except KeyError:
                return self.open_vistrail_without_prompt(locator, version)
            else:
                if version is not None:
                    controller.change_selected_version(version)
                self.select_vistrail(controller)
                return controller

    def flush_changes(self):
        self.pipelineView.flushMoveActions()

    def create_first_vistrail(self):
        if untitled_locator().has_temporaries():
            if not FileLocator().prompt_autosave(
                    JavaLocatorHelperProvider(self)):
                untitled_locator().clean_temporaries()
        self.first_controller = self.new_vistrail(True)

    def new_vistrail(self, recover_files=False):
        if recover_files and untitled_locator().has_temporaries():
            locator = copy.copy(untitled_locator())
        else:
            locator = None

        return self.open_vistrail_without_prompt(locator)

    def _version_get(self):
        return self._controller.current_version
    def _version_set(self, version):
        if version != self._controller.current_version:
            self._controller.change_selected_version(version)
            self.pipelineView.version_changed()
    current_version = property(_version_get, _version_set)

    def _confirm_closing(self, controller, name=None):
        if name is None:
            if (isinstance(controller.locator, BaseLocator) and
                    controller.locator.name):
                name = controller.locator.name
            else:
                name = "Untitled%s" % core.system.vistrails_default_file_type()
        ret = JOptionPane.showConfirmDialog(
                self,
                "Vistrail %s contains unsaved changes.\nDo you want to save "
                "changes before closing it?" % name,
                "VisTrails",
                JOptionPane.YES_NO_CANCEL_OPTION)
        if ret == JOptionPane.YES_OPTION:
            return True
        elif ret == JOptionPane.NO_OPTION:
            return False
        else:
            return None

    # Might return False (user presses "cancel")
    def close_vistrail(self, controller, quiet=False, save=False,
                       override_name=None):
        if isinstance(controller.locator, BaseLocator):
            print "close_vistrail(%r)" % controller.locator.name
        elif controller.locator is not None:
            print "close_vistrail(%r)" % controller.locator
        else:
            print "close_vistrail(%r)" % controller
        if not quiet and controller.changed:
            ret = self._confirm_closing(controller, override_name)
            if ret is None:
                # Don't close it
                return False
            elif ret is True:
                save = True
        if save and controller.changed:
            if self.dbDefault:
                r = self.save_vistrail(
                        controller, DBLocator,
                        force_choose_locator=override_name is not None)
            else:
                r = self.save_vistrail(
                        controller, FileLocator(),
                        force_choose_locator=override_name is not None)
            if r == False:
                return False
        if controller is self._controller:
            self._controller = None
            self.pipeline_dockable.change_content(None)
            self.version_dockable.change_content(None)
        self._opened_vistrails.remove(controller)
        return True

    def open_vistrail_without_prompt(self, locator, version=None, select=True):
        if isinstance(locator, BaseLocator):
            print "Opening vistrail %r" % locator.name
        else:
            print "Opening vistrail %r" % locator
        try:
            controller = JVistrailController()
            controller.add_execution_listener(self.set_executing)

            # Open the vistrail
            (vistrail, abstractions, thumbnails, mashups) = \
                    load_vistrail(locator, False)

            # Initialize the controller
            controller.set_vistrail(
                    vistrail, locator, abstractions, thumbnails)

            if version is not None:
                controller.change_selected_version(version)
            else:
                controller.select_latest_version()

            controller.set_changed(False)
        except Exception:
            import traceback
            traceback.print_exc()
            return
        else:
            self._opened_vistrails.add(controller, locator)
            if select:
                self.select_vistrail(controller)

        return controller

    def select_vistrail(self, arg, version=None):
        print "select_vistrail(%r, %s)" % (arg, version)
        controller = self._opened_vistrails.find_controller(arg)

        if (version is not None and
                version != controller.current_version):
            controller.change_selected_version(version)
        elif controller == self._controller:
            return

        controller.current_pipeline.validate()
        self._controller = controller

        # Create the pipeline view
        self.pipelineView = JPipelineView(self, self._controller)
        self._controller.current_pipeline_view = self.pipelineView
        self.pipeline_dockable.change_content(self.pipelineView)

        # Create the version view
        self.versionView = JVersionView(
                self._controller, self)
        self.version_dockable.change_content(self.versionView)

        self.moduleInfo.controller = self._controller

        # Close the first controller if necessary
        if (self.first_controller and self.first_controller != controller and
                not self.first_controller.changed):
            self.close_vistrail(self.first_controller, quiet=True, save=False)
            self.first_controller = None

        # Restores buttons
        self.set_executing(False)

        return True

    def buttonClicked(self, event):
        if event.getSource() == self.executeButton:
            self.executeAction()
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
            self.open_vistrail(filename.getAbsolutePath())

    def saveAction(self, event=None):
        if self.dbDefault:
            self.save_vistrail(self._controller, DBLocator)
        else:
            self.save_vistrail(self._controller, FileLocator())

    def saveAsAction(self, event=None):
        if self.dbDefault:
            self.save_vistrail(self._controller, DBLocator,
                               force_choose_locator=True)
        else:
            self.save_vistrail(self._controller, FileLocator(),
                               force_choose_locator=True)

    def save_vistrail(self, controller, locator_class,
                      force_choose_locator=False):
        self.flush_changes()
        if force_choose_locator:
            locator = locator_class.save_from_gui(
                    JavaLocatorHelperProvider(self),
                    Vistrail.vtType,
                    controller.locator)
        else:
            locator = controller.locator or locator_class.save_from_gui(
                    JavaLocatorHelperProvider(self),
                    Vistrail.vtType,
                    controller.locator)

        if locator == untitled_locator():
            locator = locator_class.save_from_gui(
                    JavaLocatorHelperProvider(self),
                    Vistrail.vtType,
                    controller.locator)

        # if couldn't get one, ignore the request
        if not locator:
            return False

        # update collection
        try:
            controller.write_vistrail(locator)
        except Exception, e:
            debug.critical("An error has occurred", str(e))
            raise
            return False
        try:
            from core.collection import Collection
            thumb_cache = ThumbnailCache.getInstance()
            controller.vistrail.thumbnails = controller.find_thumbnails(
                    tags_only=thumb_cache.conf.tagsOnly)
            controller.vistrail.abstractions = controller.find_abstractions(
                    controller.vistrail, True)

            collection = Collection.getInstance()
            url = locator.to_url()
            # create index if not exist
            entity = collection.fromUrl(url)
            if entity:
                # find parent vistrail
                while entity.parent:
                    entity = entity.parent
            else:
                entity = collection.updateVistrail(url, controller.vistrail)
            # add to relevant workspace categories
            collection.add_to_workspace(entity)
            collection.commit()
        except Exception, e:
            debug.critical('Failed to index vistrail', str(e))
        return locator

    def set_executing(self, executing):
        self.saveButton.setEnabled(not executing)
        self.saveAsButton.setEnabled(not executing)
        self.openButton.setEnabled(not executing)
        self.executeButton.setEnabled(not executing)
        self.openMenuItem.setEnabled(not executing)
        self.preferencesMenuItem.setEnabled(not executing)
        self.executeMenuItem.setEnabled(not executing)

    def set_active_module(self, module):
        self.moduleInfo.update_module(module)

    def executeAction(self, event=None):
        self.pipelineView.execute_workflow()

    def quitAction(self, event=None):
        self._windowCloseListener.closed()

    def showPreferences(self, event=None):
        self.preferenceWindow.setVisible(True)

    def erase_cache(self, event=None):
        core.interpreter.cached.CachedInterpreter.flush()

    def closing(self):
        def first(collection):
            i = iter(collection)
            return i.next()

        # Loop on opened vistrails and close them
        while not self._opened_vistrails.empty():
            controller = first(self._opened_vistrails)
            if not self.close_vistrail(controller):
                self.select_vistrail(controller)
                return False

        # Notify threads blocked by waitClose()
        self._visibleCond.acquire()
        self._visibleCond.notifyAll()
        self._visibleCond.release()

        return True

    def waitClose(self):
        """Wait for the window to close.
        """
        assert not SwingUtilities.isEventDispatchThread()
        self._visibleCond.acquire()
        self._visibleCond.wait()
        while self.isVisible():
            self._visibleCond.wait()
        self._visibleCond.release()
