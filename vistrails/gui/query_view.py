############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

    def query_by_example(self, pipeline):
        """ query_by_example(pipeline: Pipeline) -> None
        Perform visual query on the current vistrail
        
        """
        if len(pipeline.modules)==0:
            search = TrueSearch()
        else:
            if not self._current_terse_graph:
                self.recompute_terse_graph()
            versions_to_check = \
                set(self._current_terse_graph.vertices.iterkeys())
            search = VisualQuery(pipeline, versions_to_check)

        self.set_search(search, '') # pipeline.dump_to_string())

    def invalidate_version_tree(self, *args, **kwargs):
        self.query_view.set_display_view(self.query_view.VERSION_RESULT_VIEW)
        result_view = self.query_view.version_result_view
        result_view.controller.search = self.search
        result_view.controller.search_str = self.search_str
        result_view.controller.invalidate_version_tree(*args, **kwargs)

    def recompute_terse_graph(self, *args, **kwargs):
        self.query_view.set_display_view(self.query_view.VERSION_RESULT_VIEW)
        result_view = self.query_view.version_result_view
        result_view.controller.search = self.search
        result_view.controller.search_str = self.search_str
        result_view.controller.recompute_terse_graph(*args, **kwargs)

class QQueryPipelineView(QPipelineView):
    def __init__(self, parent=None):
        QPipelineView.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.QUERY_BACKGROUND_BRUSH)
        self.scene().current_pipeline = Pipeline()

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
        self.vt_controller = VistrailController()
        self.p_controller = VistrailController(Vistrail())

        self.query_box = QQueryBox()
        self.query_box.set_controller(self.query_controller)
        layout.addWidget(self.query_box)

        self.stacked_widget = QtGui.QStackedWidget()
        self.pipeline_view = QQueryPipelineView()
        self.p_controller.current_pipeline_view = self.pipeline_view.scene()
        self.pipeline_view.set_controller(self.p_controller)        
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
        self.action_links = {}

    def set_display_view(self, view_type):
        self.stacked_widget.setCurrentIndex(view_type)

    def get_current_view(self):
        return self.stacked_widget.currentWidget()
