############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

""" This file contains the MedleyManager
   The MedleyManager is a singleton responsible for communication with
   VisTrails builder Window medleys management.
 classes:
   MedleyManagerSingleton
"""
from PyQt4 import QtCore, QtGui
from gui.medley_window import MedleyWindow

################################################################################

class MedleyManagerSingleton(QtCore.QObject):
    def __init__(self):
        """__init__() -> MedleyManagerSingleton
        Creates Medley manager 
        """
        QtCore.QObject.__init__(self)
        self.medleyWindow = None

    def __call__(self):
        """ __call__() -> MedleyManagerSingleton
        Return self for calling method
        
        """
        return self

    def find_medley_window(self):
        """ find_medley_window() -> QWidget
        Looking for medley window
        
        """
        if not self.medleyWindow:
            wList = QtGui.QApplication.topLevelWidgets()
            for w in wList:
                if type(w)==MedleyWindow:
                    self.medleyWindow = w
                    return w
        
        self.medleyWindow = MedleyWindow()
        return self.medleyWindow
        
    def show_medley_window(self):
        if not self.medleyWindow:
            self.find_medley_window()
        self.medleyWindow.show()
    
    def create_workflow_view_from_current_pipeline(self):
        """create_workflow_view_from_current_pipeline() -> None
        Obtain the current pipeline from the builder window, create a
        workflow for it and add it to the medleys.
        This is called from the Medleys menu in the builder window
        
        """
        builderWindow = self.get_builder_window()
        if builderWindow:
            current_vistrail_view = builderWindow.viewManager.currentWidget()
            if current_vistrail_view:
                controller = current_vistrail_view.pipelineTab.controller
                if controller:
                    pipeline = controller.current_pipeline
                    if pipeline.module_count() > 0:
                        self.emit(QtCore.SIGNAL('create_workflow_view_from_builder'), 
                                  pipeline)
                    
    def post_event_to_medley_window(self, event):
        """ post_event_to_medley_window(event: QEvent) -> None
        Post an event to the medley window to make thread-safe connection
        """
        medleyWindow = self.find_medley_window()
        if medleyWindow:
            QtCore.QCoreApplication.postEvent(medleyWindow, QtGui.QShowEvent())
            QtCore.QCoreApplication.postEvent(medleyWindow, event)

    def get_builder_window(self):
        """ get_builder_window() -> QWidget        
        Return the builder window of the application, or None if
        couldn't fine one
        
        """
        app = QtCore.QCoreApplication.instance()
        if hasattr(app, 'builderWindow'):
            return app.builderWindow
        else:
            return None
        
    def initMedleys(self):
        """initBookmarks(filename: str) -> None 
        Sets BookmarksManager's filename and tells it to load bookmarks from this
        file

        """
        #the bookmarks will be loaded only when first opening the bookmarks window

    def finalize(self):
        """finalize() -> None
        """
        if not self.medleyWindow:
            self.find_medley_window()
        self.medleyWindow.deleteLater()
        
    def add_bookmark(self, parent, locator, pipeline, name=''):
        """add_bookmark(parent: int, locator: Locator, pipeline: int,
                       name: str) -> None
        creates a bookmark with the given information and adds it to the 
        collection

        """
        MedleyController.add_bookmark(self, parent, locator, 
                                      pipeline, name)
        self.emit(QtCore.SIGNAL("updateBookmarksGUI"))
        self.collection.updateGUI = False
        
    def load_pipeline(self, id):
        """load_pipeline(id: int) -> None
        Given a bookmark id, loads its correspondent pipeline and include it in
        the ensemble 

        """
        MedleyController.load_pipeline(self,id)
        self.emit(QtCore.SIGNAL("updateAliasGUI"), self.ensemble.aliases)

    def load_all_pipelines(self):
        """load_all_pipelines() -> None
        Load all bookmarks' pipelines and sets an ensemble 

        """
        MedleyController.load_all_pipelines(self)
        self.emit(QtCore.SIGNAL("updateAliasGUI"), self.ensemble.aliases)

    def set_active_pipelines(self, ids):
        """ set_active_pipelines(ids: list) -> None
        updates the list of active pipelines 
        
        """
        MedleyController.set_active_pipelines(self, ids)
        self.emit(QtCore.SIGNAL("updateAliasGUI"), self.ensemble.aliases)

    def update(self):
        MedleyController.update(self)
        if self.collection.updateGUI:
            return True
        else:
            return False

    def set_update_gui(self, value):
        self.collection.updateGUI = value
        
###############################################################################
#singleton technique
MedleyManager = MedleyManagerSingleton()
del MedleyManagerSingleton
