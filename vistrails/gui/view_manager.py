###############################################################################
##
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
""" This holds a customized QTabWidget for controlling different
vistrail views and tools

QViewManager
"""

from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from gui.utils import getBuilderWindow
from gui.vistrail_view import QVistrailView
from core import system, debug
from core.configuration import get_vistrails_configuration
from core.db.locator import FileLocator, XMLFileLocator, untitled_locator
from core.db.io import load_vistrail
from core.thumbnails import ThumbnailCache
from core.log.log import Log
from core.log.opm_graph import OpmGraph
from core.collection import Collection
import core.system
from core.vistrail.pipeline import Pipeline
from core.vistrail.tag import Tag
from core.vistrail.vistrail import Vistrail
from core.modules.module_registry import ModuleRegistry, \
    ModuleRegistryException
import copy

################################################################################
class QDetachedView(QtGui.QStackedWidget):
    """
    QDetachedView is a stacked widget holding detached views
    (e.g. Pipeline, History, etc) from the main view manager.
    
    """
    
    def __init__(self, title, parent=None):
        """ QDetachedView(parent: QWidget) -> QDetachedView
        Create an empty stacked widget
        
        """
        QtGui.QStackedWidget.__init__(self, parent)
        self.title = title
        self.setWindowTitle(self.title)

    def sizeHint(self):
        """ sizeHint() -> QRect
        Return the recommended size of a detached view

        """
        return QtCore.QSize(800, 600)
        

################################################################################
class QViewManager(QtGui.QTabWidget):
    """
    QViewManager is a tabbed widget to containing multiple Vistrail
    views. It takes care of emiting useful signals to the builder
    window
    
    """
    def __init__(self, parent=None):
        """ QViewManager(view: QVistrailView) -> QViewManager
        Create an empty tab widget
        
        """
        QtGui.QTabWidget.__init__(self, parent)
        self.closeButton = QtGui.QToolButton(self)
        self.closeButton.setIcon(CurrentTheme.VIEW_MANAGER_CLOSE_ICON)
        self.closeButton.setAutoRaise(True)
        self.setCornerWidget(self.closeButton)
        self.activeIndex = -1
        
        self.connect(self, QtCore.SIGNAL('currentChanged(int)'),
                     self.currentChanged)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self.closeVistrail)
        
        self._views = {}
        self.single_document_mode = False
        self.pip_mode = True

        self.createDetachedViews()

    def createDetachedViews(self):
        """ createDetachedViews() -> None
        Create a set of QStackedWidget for displaying detached views
        based on the input configuration
        
        """
        if getattr(get_vistrails_configuration(), 'detachHistoryView'):
            self.historyView = QDetachedView('History View')
            self.historyView.show()
        else:
            self.historyView = None
        
    def set_single_document_mode(self, on):
        """ set_single_document_mode(on: bool) -> None
        Toggle single document interface
        
        """
        self.single_document_mode = on
        if self.single_document_mode:
            self.tabBar().hide()
        else:
            self.tabBar().show()

    def add_vistrail_view(self, view):
        """ add_vistrail_view(view: QVistrailView) -> None
        Add a vistrail view to the tab, and connect to the right signals
        
        """
        self._views[view] = view.controller
        if self.indexOf(view)!=-1:
            return

        if self.historyView!=None:
            self.historyView.addWidget(view.versionTab)
                
        view.installEventFilter(self)
        self.connect(view.pipelineTab,
                     QtCore.SIGNAL('moduleSelectionChange'),
                     self.moduleSelectionChange)
        self.connect(view,
                     QtCore.SIGNAL('versionSelectionChange'),
                     self.versionSelectionChange)
        self.connect(view,
                     QtCore.SIGNAL('execStateChange()'),
                     self.execStateChange)
        self.connect(view.versionTab,
                     QtCore.SIGNAL('vistrailChanged()'),
                     self.vistrailChanged)
        self.connect(view.pipelineTab,
                     QtCore.SIGNAL('resetQuery()'),
                     self.resetQuery)
        self.connect(view.versionTab,
                     QtCore.SIGNAL('resetQuery()'),
                     self.resetQuery)
        self.connect(view.queryTab,
                     QtCore.SIGNAL('resetQuery()'),
                     self.resetQuery)

        self.emit(QtCore.SIGNAL('vistrailViewAdded'), view)
        self.addTab(view, view.windowTitle())
        if self.count()==1:
            self.emit(QtCore.SIGNAL('currentChanged(int)'), 0)

    def removeVistrailView(self, view):
        """ removeVistrailView(view: QVistrailView) -> None
        Remove the current vistrail view and destroy it
        
        """
        if view:
            del self._views[view]
            view.removeEventFilter(self)
            self.disconnect(view.pipelineTab,
                            QtCore.SIGNAL('moduleSelectionChange'),
                            self.moduleSelectionChange)
            self.disconnect(view,
                            QtCore.SIGNAL('versionSelectionChange'),
                            self.versionSelectionChange)
            self.disconnect(view.versionTab,
                            QtCore.SIGNAL('vistrailChanged()'),
                            self.vistrailChanged)

            # FIXME move this elsewhere?
            self.disconnect(view.versionTab.versionView.scene(),
                            QtCore.SIGNAL('selectionChanged()'),
                            view.versionTab.versionView.scene().selectionChanged)
            self.emit(QtCore.SIGNAL('vistrailViewRemoved'), view)
            index = self.indexOf(view) 
            if index !=-1:
                if self.historyView:
                    self.historyView.removeWidget(self.historyView.widget(self.currentIndex()))
                self.removeTab(self.currentIndex())
                self.activeIndex = self.currentIndex()
            view.controller.cleanup()
            view.close()
            view.deleteLater()

    def moduleSelectionChange(self, selection):
        """ moduleSelectionChange(selection: list[id]) -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('moduleSelectionChange'), selection)

    def versionSelectionChange(self, versionId):
        """ versionSelectionChange(versionId: int) -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('versionSelectionChange'), versionId)

    def execStateChange(self):
        """ execStateChange() -> None
        Just echo the signal from the view

        """
        self.emit(QtCore.SIGNAL('execStateChange()'))

    def vistrailChanged(self):
        """ vistrailChanged() -> None
        Just echo the signal from the view
        
        """
        self.emit(QtCore.SIGNAL('vistrailChanged()'))

    def copySelection(self):
        """ copySelection() -> None
        Copy the current selected pipeline modules
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().copySelection()

    def group(self):
        """group() -> None
        Creates a group from the selected pipeline modules
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().group()

    def ungroup(self):
        """ungroup() -> None
        Ungroups selected pipeline modules
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().ungroup()

    def makeAbstraction(self):
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().makeAbstraction()
    
    def convertToAbstraction(self):
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().convertToAbstraction()

    def importAbstraction(self):
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().importAbstraction()

    def exportAbstraction(self):
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pipelineTab.pipelineView.scene().exportAbstraction()
            
    def currentView(self):
        """currentView() -> VistrailView. Returns the current vistrail view."""
        return self.currentWidget()

    def pasteToCurrentPipeline(self):
        """ pasteToCurrentPipeline() -> None
        Paste what is on the clipboard to the current pipeline
        
        """        
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.pasteToCurrentTab()

    def selectAllModules(self):
        """ selectAllModules() -> None
        Select all modules in the current view
        
        """
        vistrailView = self.currentWidget()
        if vistrailView:
            vistrailView.selectAll()

    def canSelectAll(self):
        """ canSelectAll() -> bool        
        Check to see if there is any module in the pipeline view to be
        selected
        
        """
        vistrailView = self.currentWidget()
        if vistrailView and vistrailView.controller.current_pipeline:
            return len(vistrailView.controller.current_pipeline.modules)>0
        return False

    def redo(self):
        """ redo() -> none
        Performs a redo step.

        """
        vistrailView = self.currentWidget()
        if not vistrailView:
            return
        new_version = vistrailView.redo()
        self.emit(QtCore.SIGNAL('versionSelectionChange'), new_version)

    def undo(self):
        """ undo() -> None
        Performs an undo step.

        """
        vistrailView = self.currentWidget()
        if not vistrailView:
            return
        new_version = vistrailView.undo()
        self.emit(QtCore.SIGNAL('versionSelectionChange'), new_version)

    def newVistrail(self, recover_files=True):
        """ newVistrail() -> (None or QVistrailView)
        Create a new vistrail with no name. If user cancels process,
        returns None.

        FIXME: We should do the interactive parts separately.
        
        """
        if self.single_document_mode and self.currentView():
            if not self.closeVistrail():
                return None
        if recover_files and untitled_locator().has_temporaries():
            locator = copy.copy(untitled_locator())
        else:
            locator = None
        try:
            (vistrail, abstraction_files, thumbnail_files, _) = load_vistrail(locator)
        except ModuleRegistryException, e:
            debug.critical("Module registry error for %s" %
                           str(e.__class__.__name__), str(e))
        except Exception, e:
            debug.critical('An error has occurred', str(e))
            raise
        return self.set_vistrail_view(vistrail, locator, abstraction_files,
                                      thumbnail_files)

    def close_first_vistrail_if_necessary(self):
        # Close first vistrail of no change was made
        if not self._first_view:
            return
        vt = self._first_view.controller.vistrail
        if vt.get_version_count() == 0:
            self.closeVistrail(self._first_view)
            self._first_view = None
        else:
            # We set it to none, since it's been changed, so
            # we don't want to ever close it again.
            self._first_view = None

    def set_vistrail_view(self, vistrail, locator, abstraction_files=None,
                          thumbnail_files=None, version=None):
        """set_vistrail_view(vistrail: Vistrail,
                             locator: VistrailLocator,
                             abstraction_files: list(str),
                             thumbnail_files: list(str),
                             version=None)
                          -> QVistrailView
        Sets a new vistrail view for the vistrail object for the given version
        if version is None, use the latest version
        """

        if type(version) == type(""):
            try:
                version = vistrail.get_version_number(version)
            except:
                version = None

        vistrailView = QVistrailView()
        vistrailView.set_vistrail(vistrail, locator, abstraction_files,
                                  thumbnail_files)
        self.add_vistrail_view(vistrailView)
        self.setCurrentWidget(vistrailView)
        vistrailView.setup_view(version)
        vistrailView.setPIPMode(self.pip_mode)
        self.versionSelectionChange(vistrailView.controller.current_version)
        return vistrailView

    def open_vistrail(self, locator, version=None, is_abstraction=False):
        """open_vistrail(locator: Locator, version = None: int or str,
                         is_abstraction: bool)

        opens a new vistrail from the given locator, selecting the
        given version.

        """
        self.close_first_vistrail_if_necessary()
        if self.single_document_mode and self.currentView():
            self.closeVistrail()
        view = self.ensureVistrail(locator)
        if view:
            if version is not None:
                if type(version) == type(""):
                    try:
                        version = view.vistrail.get_version_number(version)
                    except:
                        version = None
                if version is not None:
                    view.setup_view(version)
            return view
        try:
            (vistrail, abstraction_files, thumbnail_files, _) = \
                                        load_vistrail(locator, is_abstraction)
            result = self.set_vistrail_view(vistrail, locator, 
                                            abstraction_files, thumbnail_files,
                                            version)
            # update collection
            try:
                vistrail.thumbnails = thumbnail_files
                vistrail.abstractions = abstraction_files
                collection = Collection.getInstance()
                url = locator.to_url()
                # create index if not exist
                entity = collection.fromUrl(url)
                if entity:
                    # find parent vistrail
                    while entity.parent:
                        entity = entity.parent 
                else:
                    entity = collection.updateVistrail(url, vistrail)
                # add to relevant workspace categories
                collection.add_to_workspace(entity)
                collection.commit()
            except Exception, e:
                import traceback
                debug.critical('Failed to index vistrail', str(e) + traceback.format_exc())
            return result
        except ModuleRegistryException, e:
            debug.critical("Module registry error for %s" %
                           str(e.__class__.__name__), str(e))
        except Exception, e:
            import traceback
            debug.critical('An error has occurred', str(e) + traceback.format_exc())
            raise
        
    def save_vistrail(self, locator_class,
                      vistrailView=None,
                      force_choose_locator=False):
        """

        force_choose_locator=True triggers 'save as' behavior
        """
        global bobo

        if not vistrailView:
            vistrailView = self.currentWidget()
        vistrailView.flush_changes()
        if vistrailView:
            gui_get = locator_class.save_from_gui
            # get a locator to write to
            if force_choose_locator:
                locator = gui_get(self, Vistrail.vtType,
                                  vistrailView.controller.locator)
            else:
                locator = (vistrailView.controller.locator or
                           gui_get(self, Vistrail.vtType,
                                   vistrailView.controller.locator))
            if locator == untitled_locator():
                locator = gui_get(self, Vistrail.vtType,
                                  vistrailView.controller.locator)
            # if couldn't get one, ignore the request
            if not locator:
                return False
            # update collection
            try:
                vistrailView.controller.write_vistrail(locator)
            except Exception, e:
                debug.critical('An error has occurred', str(e))
                raise
                return False
            try:
                thumb_cache = ThumbnailCache.getInstance()
                vistrailView.controller.vistrail.thumbnails = \
                    vistrailView.controller.find_thumbnails(
                        tags_only=thumb_cache.conf.tagsOnly)
                vistrailView.controller.vistrail.abstractions = \
                    vistrailView.controller.find_abstractions(
                        vistrailView.controller.vistrail, True)

                collection = Collection.getInstance()
                url = locator.to_url()
                # create index if not exist
                entity = collection.fromUrl(url)
                if entity:
                    # find parent vistrail
                    while entity.parent:
                        entity = entity.parent 
                else:
                    entity = collection.updateVistrail(url, vistrailView.controller.vistrail)
                # add to relevant workspace categories
                collection.add_to_workspace(entity)
                collection.commit()
            except Exception, e:
                debug.critical('Failed to index vistrail', str(e))
            return locator
        return False
   
    def open_workflow(self, locator, version=None):
        self.close_first_vistrail_if_necessary()
        if self.single_document_mode and self.currentView():
            self.closeVistrail()

        vistrail = Vistrail()
        try:
            if locator is not None:
                workflow = locator.load(Pipeline)
                action_list = []
                for module in workflow.module_list:
                    action_list.append(('add', module))
                for connection in workflow.connection_list:
                    action_list.append(('add', connection))
                action = core.db.action.create_action(action_list)
                vistrail.add_action(action, 0L)
                vistrail.update_id_scope()
                vistrail.addTag("Imported workflow", action.id)
                # FIXME might need different locator?
        except ModuleRegistryException, e:
            msg = ('Cannot find module "%s" in package "%s". '
                    'Make sure package is ' 
                   'enabled in the Preferences dialog.' % \
                       (e._name, e._identifier))
            debug.critical(msg)
        except Exception, e:
            debug.critical('An error has occurred', str(e))
            raise

        return self.set_vistrail_view(vistrail, None)

    # FIXME normalize workflow/log/registry!!!
    def save_workflow(self, locator_class, force_choose_locator=True):
        vistrailView = self.currentWidget()

        if vistrailView:
            vistrailView.flush_changes()
            gui_get = locator_class.save_from_gui
            if force_choose_locator:
                locator = gui_get(self, Pipeline.vtType,
                                  vistrailView.controller.locator)
            else:
                locator = (vistrailView.controller.locator or
                           gui_get(self, Pipeline.vtType,
                                   vistrailView.controller.locator))
            if locator == untitled_locator():
                locator = gui_get(self, Pipeline.vtType,
                                  vistrailView.controller.locator)
            if not locator:
                return False
            vistrailView.controller.write_workflow(locator)
            return True
        return False

    def save_log(self, locator_class, force_choose_locator=True):
        vistrailView = self.currentWidget()

        if vistrailView:
            vistrailView.flush_changes()
            gui_get = locator_class.save_from_gui
            if force_choose_locator:
                locator = gui_get(self, Log.vtType,
                                  vistrailView.controller.locator)
            else:
                locator = (vistrailView.controller.locator or
                           gui_get(self, Log.vtType,
                                   vistrailView.controller.locator))
            if locator == untitled_locator():
                locator = gui_get(self, Log.vtType,
                                  vistrailView.controller.locator)
            if not locator:
                return False
            vistrailView.controller.write_log(locator)
            return True
        return False

    def save_registry(self, locator_class, force_choose_locator=True):
        vistrailView = self.currentWidget()

        if vistrailView:
            vistrailView.flush_changes()
            gui_get = locator_class.save_from_gui
            if force_choose_locator:
                locator = gui_get(self, ModuleRegistry.vtType,
                                  vistrailView.controller.locator)
            else:
                locator = (vistrailView.controller.locator or
                           gui_get(self, ModuleRegistry.vtType,
                                   vistrailView.controller.locator))
            if locator == untitled_locator():
                locator = gui_get(self, ModuleRegistry.vtType,
                                  vistrailView.controller.locator)
            if not locator:
                return False
            vistrailView.controller.write_registry(locator)
            return True
        return False

    def save_opm(self, locator_class=XMLFileLocator, 
                 force_choose_locator=True):
        vistrailView = self.currentWidget()

        if vistrailView:
            vistrailView.flush_changes()
            gui_get = locator_class.save_from_gui
            if force_choose_locator:
                locator = gui_get(self, OpmGraph.vtType,
                                  vistrailView.controller.locator)
            else:
                locator = (vistrailView.controller.locator or
                           gui_get(self, OpmGraph.vtType,
                                   vistrailView.controller.locator))
            if locator == untitled_locator():
                locator = gui_get(self, OpmGraph.vtType,
                                  vistrailView.controller.locator)
            if not locator:
                return False
            vistrailView.controller.write_opm(locator)
            return True
        return False
             
    def export_stable(self, locator_class=XMLFileLocator,
                      force_choose_locator=True):
        vistrailView = self.currentWidget()
        vistrailView.flush_changes()

        if vistrailView:
            vistrailView.flush_changes()
            gui_get = locator_class.save_from_gui
            if force_choose_locator:
                locator = gui_get(self, Vistrail.vtType,
                                  vistrailView.controller.locator)
            else:
                locator = (vistrailView.controller.locator or
                           gui_get(self, Vistrail.vtType,
                                   vistrailView.controller.locator))
            if locator == untitled_locator():
                locator = gui_get(self, Vistrail.vtType,
                                  vistrailView.controller.locator)
            if not locator:
                return False
            vistrailView.controller.write_vistrail(locator, '1.0.1')
            return True
        return False

    def closeVistrail(self, vistrailView=None, quiet=False):
        """ closeVistrail(vistrailView: QVistrailView, quiet: bool) -> bool
        Close the current active vistrail
        
        """
        if not vistrailView:
            vistrailView = self.currentWidget()
        vistrailView.flush_changes()

        if vistrailView:
            if not quiet and vistrailView.controller.changed:
                text = vistrailView.controller.name
                if text=='':
                    text = 'Untitled%s'%core.system.vistrails_default_file_type()
                text = ('Vistrail ' +
                        QtCore.Qt.escape(text) +
                        ' contains unsaved changes.\n Do you want to '
                        'save changes before closing it?')
                res = QtGui.QMessageBox.information(getBuilderWindow(),
                                                    'Vistrails',
                                                    text, 
                                                    '&Save', 
                                                    '&Discard',
                                                    'Cancel',
                                                    0,
                                                    2)
            else:
                res = 1
            locator = vistrailView.controller.locator
            if res == 0:
                if locator is None:
                    class_ = FileLocator()
                else:
                    class_ = type(locator)
                locator = self.save_vistrail(class_)
                if not locator:
                    return False
            elif res == 2:
                return False
 
            vistrailView.controller.close_vistrail(locator)
            self.removeVistrailView(vistrailView)
            if self.count()==0:
                self.emit(QtCore.SIGNAL('currentVistrailChanged'), None)
                self.emit(QtCore.SIGNAL('versionSelectionChange'), -1)
        if vistrailView == self._first_view:
            self._first_view = None
        return True
    
    def closeAllVistrails(self):
        """ closeAllVistrails() -> bool        
        Attemps to close every single vistrail, return True if
        everything is closed correctly
        
        """
        while self.count()>0:
            if not self.closeVistrail():
                return False
        return True

    def currentChanged(self, index):
        """ currentChanged(index: int):        
        Emit signal saying a different vistrail has been chosen to the
        builder
        
        """
        self.activeIndex = index
        self.emit(QtCore.SIGNAL('currentVistrailChanged'),
                  self.currentWidget())
        if index >= 0:
            self.emit(QtCore.SIGNAL('versionSelectionChange'), 
                      self.currentWidget().controller.current_version)
        else:
            self.emit(QtCore.SIGNAL('versionSelectionChange'), 
                      -1)
        if self.historyView:
            self.historyView.setCurrentIndex(index)
            if self.currentView()!=None:
                self.historyView.setWindowTitle('History View - ' +
                                                self.currentView().windowTitle())
        
    def eventFilter(self, object, event):
        """ eventFilter(object: QVistrailView, event: QEvent) -> None
        Filter the window title change event for the view widget
        
        """
        if event.type()==QtCore.QEvent.WindowTitleChange:
            if object==self.currentWidget():
                self.setTabText(self.currentIndex(), object.windowTitle())
                self.currentChanged(self.currentIndex())
        return QtGui.QTabWidget.eventFilter(self, object, event)

    def getCurrentVistrailFileName(self):
        """ getCurrentVistrailFileName() -> str        
        Return the filename of the current vistrail or None if it
        doesn't have one
        
        """        
        vistrailView = self.currentWidget()
        if vistrailView and vistrailView.controller.name!='':
            return vistrailView.controller.name
        else:
            return None

    def setPIPMode(self, on):
        """ setPIPMode(on: Bool) -> None
        Set the picture-in-picture mode for all views
        
        """
        self.pip_mode = on
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.setPIPMode(on)

    def setMethodsMode(self, on):
        """ setMethodsMode(on: Bool) -> None
        Turn the methods panel on/off for all views
        
        """
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.setMethodsMode(on)


    def setSetMethodsMode(self, on):
        """ setSetMethodsMode(on: Bool) -> None
        Turn the set methods panel on/off for all views
        
        """
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.setSetMethodsMode(on)

    def setPropertiesMode(self, on):
        """ setPropertiesMode(on: Bool) -> None
        Turn the properties panel on/off for all views
        
        """
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.setPropertiesMode(on)

    def setPropertiesOverlayMode(self, on):
        """ setPropertiesOverlayMode(on: Bool) -> None
        Turn the properties overlay panel on/off for all views
        
        """
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.setPropertiesOverlayMode(on)
            
    def setModuleConfigMode(self, on):
        """ setModuleConfigMode(on: Bool) -> None
        Turn the module configuration panel on/off for all views
        
        """
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.setModuleConfigMode(on)
            
    def setVistrailVarsMode(self, on):
        """ setVistrailVarsMode(on: Bool) -> None
        Turn the vistrail variables panel on/off for all views
        
        """
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            vistrailView.setVistrailVarsMode(on)
            
    def ensureVistrail(self, locator):
        """ ensureVistrail(locator: VistrailLocator) -> QVistrailView        
        This will first find among the opened vistrails to see if
        vistrails from locator has been opened. If not, it will return None.
        
        """
        for i in xrange(self.count()):
            view = self.widget(i)
            if view.controller.vistrail.locator == locator:
                self.setCurrentWidget(view)
                return view
        return None
    
    def set_first_view(self, view):
        self._first_view = view

    def viewModeChanged(self, mode):
        """ viewModeChanged(mode: int) -> None
        
        """
        for viewIndex in xrange(self.count()):
            vistrailView = self.widget(viewIndex)
            if self.historyView!=None and mode>1:
                vistrailView.viewModeChanged(mode-1)
            else:
                vistrailView.viewModeChanged(mode)
    
    def changeCursor(self, mode):
        """ changeCursor(mode: Int) -> None
        
        """
        for viewIndex in xrange(self.count()):            
            vistrailView = self.widget(viewIndex)
            vistrailView.updateCursorState(mode)            
        
    def resetQuery(self):
        """ resetQwuery() -> None
        
        """
        self.queryVistrail(False)

    def queryVistrail(self, on=True):
        """ queryVistrail(on: bool) -> None
        
        """
        self.currentView().setFocus(QtCore.Qt.MouseFocusReason)
        self.currentView().queryVistrail(on)

    def executeCurrentPipeline(self):
        """ executeCurrentPipeline() -> None
        
        """
        self.currentView().setFocus(QtCore.Qt.MouseFocusReason)
        self.currentView().checkModuleConfigPanel()
        self.currentView().controller.execute_current_workflow()

    def executeCurrentExploration(self):
        """ executeCurrentExploration() -> None
        
        """
        self.currentView().setFocus(QtCore.Qt.MouseFocusReason)
        self.currentView().executeParameterExploration()
