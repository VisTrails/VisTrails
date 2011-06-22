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

from PyQt4 import QtCore, QtGui

from core.query.combined import CombinedSearch
from core.query.version import SearchCompiler, SearchParseError, TrueSearch
from core.query.visual import VisualQuery
from core.vistrail.pipeline import Pipeline
from core.vistrail.vistrail import Vistrail

from gui.base_view import BaseView
from gui.common_widgets import QSearchBox
from gui.pipeline_view import QPipelineView
from gui.theme import CurrentTheme
from gui.version_view import QVersionTreeView
from gui.vistrail_controller import VistrailController

class QueryController(object):
    def __init__(self, query_view=None):
        self.query_view = query_view
        self.refine = False
        self.search = None
        self.search_str = None
        self.search_pipeline = None
        self.vistrail = None

    def set_query_view(self, query_view=None):
        self.query_view = query_view
    
    def set_vistrail(self, vistrail):
        self.vistrail = vistrail

    def set_search(self, search_str=None):
        """ set_search(search_str: str) -> None
        Change the currrent version tree search statement
        
        """
        search_pipeline = \
            self.query_view.pipeline_view.scene().current_pipeline
        if search_str is None:
            search_str = self.query_view.query_box.getCurrentText()
        if self.search_str != search_str or \
                self.search_pipeline != search_pipeline:
            self.search_str = search_str
            self.search_pipeline = search_pipeline
            vt_controller = self.query_view.vt_controller
            versions_to_check = \
                set(vt_controller._current_terse_graph.vertices.iterkeys())
            self.search = CombinedSearch(search_str, search_pipeline,
                                         versions_to_check)
            self.search.run(self.vistrail, '')
            if self.refine:
                self.recompute_terse_graph()
            self.invalidate_version_tree(True)
            
            result_entities = []
            entity = self.search.getResultEntity(self.vistrail,
                                                 versions_to_check)
            if entity is not None:
                result_entities.append(entity)

            from gui.vistrails_window import _app
            _app.notify("search_changed", result_entities)

        # if self.search != search or self.search_str != text:
        #     self.search = search
        #     self.search_str = text
        #     if self.search:
        #         self.search.run(self.vistrail, '')
        #         self.invalidate_version_tree(True)
        #     if self.refine:
        #         # need to recompute the graph because the refined items might
        #         # have changed since last time
        #         self.recompute_terse_graph()
        #         self.invalidate_version_tree(True)
        #     else:
        #         self.invalidate_version_tree(False)
            
        #     # self.emit(QtCore.SIGNAL('searchChanged'))

    def set_refine(self, refine):
        """ set_refine(refine: bool) -> None
        Set the refine state to True or False
        
        """
        if self.refine != refine:
            self.refine = refine
            # need to recompute the graph because the refined items might
            # have changed since last time
            self.recompute_terse_graph()
            self.invalidate_version_tree(True)

    def reset_search(self):
        self.search = None
        self.search_pipeline = None
        self.query_view.pipeline_view.controller.change_selected_version(0)
        self.query_view.pipeline_view.scene().setupScene(
            self.query_view.pipeline_view.controller.current_pipeline)
        self.query_view.set_display_view(self.query_view.VISUAL_SEARCH_VIEW)
        self.query_view.query_box.searchBox.clearSearch()

        from gui.vistrails_window import _app
        _app.notify("search_changed", None)

    def invalidate_version_tree(self, *args, **kwargs):
        self.query_view.set_display_view(self.query_view.VERSION_RESULT_VIEW)
        self.query_view.query_box.setManualResetEnabled(True)
        result_view = self.query_view.version_result_view
        result_view.controller.search = self.search
        result_view.controller.search_str = self.search_str
        result_view.controller.invalidate_version_tree(*args, **kwargs)

    def recompute_terse_graph(self, *args, **kwargs):
        self.query_view.set_display_view(self.query_view.VERSION_RESULT_VIEW)
        self.query_view.query_box.setManualResetEnabled(True)
        result_view = self.query_view.version_result_view
        result_view.controller.search = self.search
        result_view.controller.search_str = self.search_str
        result_view.controller.recompute_terse_graph(*args, **kwargs)

class QQueryPipelineView(QPipelineView):
    def __init__(self, parent=None):
        QPipelineView.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.QUERY_BACKGROUND_BRUSH)
        self.scene().current_pipeline = Pipeline()
        self.query_controller = None
      
    def set_query_controller(self, controller):
        self.query_controller = controller
  
    def execute(self):
        self.query_controller.set_search(None)
    
class QQueryResultGlobalView(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(QtGui.QLabel("FIXME: Global Results"))
        self.setLayout(layout)
        # self.setBackgroundBrush(CurrentTheme.QUERY_RESULT_BACKGROUND_BRUSH)

class QQueryResultVersionView(QVersionTreeView):
    def __init__(self, parent=None):
        QVersionTreeView.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.QUERY_RESULT_BACKGROUND_BRUSH)

class QQueryResultWorkflowView(QPipelineView):
    def __init__(self, parent=None):
        QPipelineView.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.QUERY_RESULT_BACKGROUND_BRUSH)
    
class QQueryBox(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.build_widget()
        self.controller = None

    def set_controller(self, controller=None):
        self.controller = controller

    def build_widget(self):
        layout = QtGui.QVBoxLayout()
        layout.setMargin(4)
        layout.setSpacing(2)
        self.searchBox = QSearchBox(True, False, self)
        layout.addWidget(self.searchBox)
        radio_layout = QtGui.QHBoxLayout()
        radio_layout.setSpacing(5)
        radio_layout.setAlignment(QtCore.Qt.AlignLeft)
        radio_layout.addWidget(QtGui.QLabel("Search:"))
        self.searchAll = QtGui.QRadioButton("All Vistrails")
        self.searchCurrent = QtGui.QRadioButton("Current Vistrail")
        self.searchWorkflow = QtGui.QRadioButton("Current Workflow")
        radio_layout.addWidget(self.searchAll)
        radio_layout.addWidget(self.searchCurrent)
        radio_layout.addWidget(self.searchWorkflow)
        self.searchCurrent.setChecked(True)
        layout.addLayout(radio_layout)
        self.setLayout(layout)

        self.connect(self.searchBox, QtCore.SIGNAL('resetSearch()'),
                     self.resetSearch)
        self.connect(self.searchBox, QtCore.SIGNAL('executeSearch(QString)'),
                     self.executeSearch)
        self.connect(self.searchBox, QtCore.SIGNAL('refineMode(bool)'),
                     self.refineMode)

    def resetSearch(self, emit_signal=True):
        """
        resetSearch() -> None

        """
        if self.controller and emit_signal:
            self.controller.reset_search()
            self.emit(QtCore.SIGNAL('textQueryChange(bool)'), False)
        else:
            self.searchBox.clearSearch()
    
    def executeSearch(self, text):
        """
        executeSearch(text: QString) -> None

        """
        s = str(text)
        if self.controller:
            self.controller.set_search(s)
            # try:
            #     search = CombinedSearch(s, 
            #     search = SearchCompiler(s).searchStmt
            # except SearchParseError, e:
            #     debug.warning("Search Parse Error", str(e))
            #     search = None
            # self.controller.set_search(search, s)
            # self.emit(QtCore.SIGNAL('textQueryChange(bool)'), s!='')

    def refineMode(self, on):
        """
        refineMode(on: bool) -> None
        
        """
        if self.controller:
            self.controller.set_refine(on)

    def getCurrentText(self):
        return self.searchBox.getCurrentText()

    def setManualResetEnabled(self, boolVal):
        self.searchBox.setManualResetEnabled(boolVal)

class QQueryView(QtGui.QWidget, BaseView):
    VISUAL_SEARCH_VIEW = 0
    GLOBAL_RESULT_VIEW = 1
    VERSION_RESULT_VIEW = 2
    WORKFLOW_RESULT_VIEW = 3

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        BaseView.__init__(self)
        self.build_widget()
        self.set_title("Search")

    def set_controller(self, controller=None):
        self.controller = controller
        self.vt_controller.vistrail_view = self.version_result_view
        self.vt_controller.current_pipeline_view = \
            self.workflow_result_view.scene()
        # self.vt_controller.vistrail_view.set_controller(self.vt_controller)
        self.vt_controller.set_vistrail(controller.vistrail, None)
        self.version_result_view.set_controller(self.vt_controller)
        self.workflow_result_view.set_controller(self.vt_controller)
        self.query_controller.set_vistrail(controller.vistrail)

    def build_widget(self):
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)

        self.query_controller = QueryController(self)
        self.vt_controller = VistrailController(auto_save=False)
        self.p_controller = VistrailController(Vistrail(), auto_save=False)
        
        self.connect(self.p_controller,
                     QtCore.SIGNAL('vistrailChanged()'),
                     self.vistrailChanged)

        self.query_box = QQueryBox()
        self.query_box.set_controller(self.query_controller)
        layout.addWidget(self.query_box)

        self.stacked_widget = QtGui.QStackedWidget()
        self.pipeline_view = QQueryPipelineView()
        self.p_controller.current_pipeline_view = self.pipeline_view.scene()
        self.pipeline_view.set_controller(self.p_controller)
        self.pipeline_view.set_query_controller(self.query_controller)
        QQueryView.VISUAL_SEARCH_VIEW = \
            self.stacked_widget.addWidget(self.pipeline_view)
        self.global_result_view = QQueryResultGlobalView()
        QQueryView.GLOBAL_RESULT_VIEW = \
            self.stacked_widget.addWidget(self.global_result_view)
        self.version_result_view = QQueryResultVersionView()
        # self.version_result_view.set_controller(self.vt_controller)
        QQueryView.VERSION_RESULT_VIEW = \
            self.stacked_widget.addWidget(self.version_result_view)
        self.workflow_result_view = QQueryResultWorkflowView()
        # self.workflow_result_view.set_controller(self.vt_controller)
        QQueryView.WORKFLOW_RESULT_VIEW = \
            self.stacked_widget.addWidget(self.workflow_result_view)
        self.stacked_widget.setCurrentWidget(self.pipeline_view)
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)

    def set_default_layout(self):
        from gui.module_palette import QModulePalette
        from gui.module_info import QModuleInfo
        self.layout = \
            {QtCore.Qt.LeftDockWidgetArea: QModulePalette,
             QtCore.Qt.RightDockWidgetArea: QModuleInfo,
             }
            
    def set_action_links(self):
        self.action_links = \
            { 'execute': ('query_pipeline_changed', self.pipeline_non_empty) }

        # also add other notification here...
        from gui.vistrails_window import _app
        _app.register_notification('query_pipeline_changed', 
                                   self.set_reset_button)

    def set_reset_button(self, pipeline):
        self.query_box.setManualResetEnabled(self.pipeline_non_empty(pipeline))

    def set_display_view(self, view_type):
        self.stacked_widget.setCurrentIndex(view_type)

    def get_current_view(self):
        return self.stacked_widget.currentWidget()
    
    def set_action_defaults(self):
        self.action_defaults = \
            {
             'execute': [('setEnabled', True, self.set_execute_action),
                          ('setIcon', False, CurrentTheme.VISUAL_QUERY_ICON),
                          ('setToolTip', False, 'Execute a visual query')],
             'publishWeb': [('setEnabled', False, False)],
             'publishPaper': [('setEnabled', False, False)],
            }
    
    def set_execute_action(self):
        if self.vt_controller:
            return self.pipeline_non_empty(self.p_controller.current_pipeline)
        return False
        
    def pipeline_non_empty(self, pipeline):
        return pipeline is not None and len(pipeline.modules) > 0
    
    def vistrailChanged(self):
        from gui.vistrails_window import _app
        self.p_controller.current_pipeline.ensure_connection_specs()
        _app.notify('query_pipeline_changed', self.p_controller.current_pipeline)

    def query_changed(self, query=None):
        if query is None:
            self.query_controller.reset_search()
        # FIXME add support for changing the query to something specific
