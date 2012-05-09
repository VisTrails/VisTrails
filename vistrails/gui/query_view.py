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

from PyQt4 import QtCore, QtGui

from core.collection import Collection
from core.collection.vistrail import VistrailEntity
from core.data_structures.bijectivedict import Bidict
from core.query.combined import CombinedSearch
from core.query.multiple import MultipleSearch
from core.query.version import SearchCompiler, SearchParseError, TrueSearch
from core.query.visual import VisualQuery
from core.vistrail.pipeline import Pipeline
from core.vistrail.vistrail import Vistrail

from gui.base_view import BaseView
from gui.common_widgets import QSearchBox
from gui.modules import get_query_widget_class
from gui.pipeline_view import QPipelineView
from gui.ports_pane import ParameterEntry
from gui.theme import CurrentTheme
from gui.version_view import QVersionTreeView
from gui.vistrail_controller import VistrailController

class QueryController(object):
    LEVEL_ALL = 0
    LEVEL_VISTRAIL = 1
    LEVEL_WORKFLOW = 2

    def __init__(self, query_view=None):
        self.query_view = query_view
        self.search = None
        self.search_str = None
        self.search_pipeline = None
        self.search_level = 3
        self.vt_controller = None
        self.level = QueryController.LEVEL_VISTRAIL
        self.workflow_version = None

    def set_level(self, level):
        self.query_view.query_box.setLevel(level)
        self.level_changed(level)

    def level_changed(self, level):
        self.query_view.set_result_level(level)
        if level >= QueryController.LEVEL_VISTRAIL and \
                self.query_view.query_box.backButton.isEnabled():
            self.query_view.query_box.editButton.setEnabled(True)
        else:
            self.query_view.query_box.editButton.setEnabled(False)
        self.level = level

    def set_query_view(self, query_view=None):
        self.query_view = query_view
    
    def set_vistrail_controller(self, vt_controller):
        self.vt_controller = vt_controller

    def set_search(self, search=None):
        self.search = search
        self.query_view.version_result_view.controller.search = search
        self.query_view.workflow_result_view.controller.search = search
        
    def run_search(self, search_str=None):
        """ set_search(search_str: str) -> None
        Change the currrent version tree search statement
        
        """
        search_pipeline = \
            self.query_view.pipeline_view.scene().current_pipeline
        if search_str is None:
            search_str = self.query_view.query_box.getCurrentText()
        self.query_view.update_controller()
        if self.search is None or \
                self.search.search_str != search_str or \
                self.search.queryPipeline != search_pipeline or \
                self.query_view.p_controller.changed or \
                self.search_level > self.level:
            self.search_str = search_str
            self.search_pipeline = search_pipeline
            self.search_level = self.level
            # reset changed here
            self.query_view.p_controller.set_changed(False)
            vt_controller = self.query_view.vt_controller
            current_vistrail = self.vt_controller.vistrail

            def do_search(only_current_vistrail=False, 
                          only_current_workflow=False):
                entities_to_check = {}
                open_col = Collection.getInstance()
                
                for entity in open_col.get_current_entities():
                    if entity.type_id == VistrailEntity.type_id and \
                            entity.is_open:
                        controller = entity._window.controller
                        if only_current_vistrail and \
                                controller.vistrail != vt_controller.vistrail:
                            continue
                        if only_current_workflow:
                            versions_to_check = controller.current_version
                        else:
                            graph = controller._current_terse_graph
                            versions_to_check = set(graph.vertices.iterkeys())
                        entities_to_check[entity] = versions_to_check
                self.set_search(MultipleSearch(search_str, search_pipeline,
                                               entities_to_check))
                self.search.run()
                return self.search.getResultEntities()
                
            if self.level == QueryController.LEVEL_VISTRAIL:
                result_entities = do_search(True)                
                self.show_vistrail_matches()
            elif self.level == QueryController.LEVEL_WORKFLOW:
                self.search_level = QueryController.LEVEL_VISTRAIL
                result_entities = do_search(True)
                self.update_version_tree()
                self.show_workflow_matches()
            elif self.level == QueryController.LEVEL_ALL:
                result_entities = do_search()
                self.show_global_matches()

            from gui.vistrails_window import _app
            _app.notify("search_changed", self.search, result_entities)
        else:
            self.query_view.set_to_result_mode()
            
    def set_refine(self, refine):
        """ set_refine(refine: bool) -> None
        Set the refine state to True or False
        
        """
        self.query_view.version_result_view.controller.set_refine(refine)

    def reset_search(self):
        self.search = None
        self.search_pipeline = None
        self.query_view.pipeline_view.controller.change_selected_version(0)
        self.query_view.pipeline_view.scene().setupScene(
            self.query_view.pipeline_view.controller.current_pipeline)
        self.query_view.set_to_search_mode()
        self.query_view.query_box.searchBox.clearSearch()
        self.query_view.vistrailChanged()

        from gui.vistrails_window import _app
        _app.notify("search_changed", None, None)

    def back_to_search(self):
        self.query_view.set_to_search_mode()

    def goto_edit(self):
        # get the version info and send it to open_vistrail call
        if self.level == QueryController.LEVEL_VISTRAIL:
            from gui.vistrails_window import _app
            _app.qactions['history'].trigger()
        elif self.level == QueryController.LEVEL_WORKFLOW:
            from gui.vistrails_window import _app
            version = self.query_view.vt_controller.current_version
            self.query_view.controller.change_selected_version(version, True)
            _app.qactions['pipeline'].trigger()

    def update_results(self):
        if self.workflow_version != \
                self.query_view.vt_controller.current_version:
            result_view = self.query_view.workflow_result_view
            result_view.scene().setupScene(
                result_view.controller.current_pipeline)
            result_view.scene().fitToView(result_view, True)
            self.workflow_version = \
                self.query_view.vt_controller.current_version

    def update_version_tree(self):
        result_view = self.query_view.version_result_view
        if result_view.controller.refine:
            result_view.controller.recompute_terse_graph()
        result_view.controller.invalidate_version_tree()

    def show_vistrail_matches(self, *args, **kwargs):
        if self.level != QueryController.LEVEL_VISTRAIL:
            self.set_level(QueryController.LEVEL_VISTRAIL)
        self.query_view.set_to_result_mode()
        result_view = self.query_view.version_result_view
        if result_view.controller.refine:
            result_view.controller.recompute_terse_graph()
        result_view.controller.invalidate_version_tree(*args, **kwargs)        

    def show_workflow_matches(self):
        if self.level != QueryController.LEVEL_WORKFLOW:
            self.set_level(QueryController.LEVEL_WORKFLOW)
        self.query_view.set_to_result_mode()
        result_view = self.query_view.workflow_result_view
        result_view.scene().setupScene(result_view.controller.current_pipeline)
        result_view.scene().fitToView(result_view, True)

    def show_global_matches(self):
        if self.level != QueryController.LEVEL_ALL:
            self.set_level(QueryController.LEVEL_ALL)
        self.query_view.set_to_result_mode()        

    # def invalidate_version_tree(self, *args, **kwargs):
    #     self.query_view.set_to_result_mode()
    #     result_view = self.query_view.version_result_view
    #     result_view.controller.search = self.search
    #     result_view.controller.search_str = self.search_str
    #     result_view.controller.invalidate_version_tree(*args, **kwargs)

    # def recompute_terse_graph(self, *args, **kwargs):
    #     self.query_view.set_to_result_mode()
    #     result_view = self.query_view.version_result_view
    #     result_view.controller.search = self.search
    #     result_view.controller.search_str = self.search_str
    #     result_view.controller.recompute_terse_graph(*args, **kwargs)


class QQueryPipelineView(QPipelineView):
    def __init__(self, parent=None):
        QPipelineView.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.QUERY_BACKGROUND_BRUSH)
        self.scene().current_pipeline = Pipeline()
        self.query_controller = None
      
    def set_query_controller(self, controller):
        self.query_controller = controller
  
    def execute(self):
        self.query_controller.run_search(None)
    
class QQueryResultGlobalView(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        label = QtGui.QLabel("See Workspace Window")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label, QtCore.Qt.AlignCenter)
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
        self.scene().set_read_only_mode(True)
    
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
        searchAll = QtGui.QRadioButton("Open Vistrails")
        searchCurrent = QtGui.QRadioButton("Current Vistrail")
        searchWorkflow = QtGui.QRadioButton("Current Workflow")
        self.level_group = QtGui.QButtonGroup()
        self.level_group.addButton(searchAll)
        self.level_group.addButton(searchCurrent)
        self.level_group.addButton(searchWorkflow)
        self.level_map = \
            Bidict([(QueryController.LEVEL_ALL, searchAll),
                    (QueryController.LEVEL_VISTRAIL, searchCurrent),
                    (QueryController.LEVEL_WORKFLOW, searchWorkflow)])
        radio_layout.addWidget(searchAll)
        radio_layout.addWidget(searchCurrent)
        radio_layout.addWidget(searchWorkflow)
        searchCurrent.setChecked(True)
        
        self.editButton = QtGui.QPushButton("Edit")
        self.editButton.setEnabled(False)
        self.backButton = QtGui.QPushButton("Back to Search")
        self.backButton.setEnabled(False)
        radio_layout.addStretch(1)
        radio_layout.addWidget(self.editButton, 0, QtCore.Qt.AlignRight)
        radio_layout.addWidget(self.backButton, 0, QtCore.Qt.AlignRight)
        layout.addLayout(radio_layout)
        self.setLayout(layout)

        self.connect(self.searchBox, QtCore.SIGNAL('resetSearch()'),
                     self.resetSearch)
        self.connect(self.searchBox, QtCore.SIGNAL('executeSearch(QString)'),
                     self.executeSearch)
        self.connect(self.searchBox, QtCore.SIGNAL('refineMode(bool)'),
                     self.refineMode)
        self.connect(self.backButton, QtCore.SIGNAL('clicked()'),
                     self.backToSearch)
        self.connect(self.editButton, QtCore.SIGNAL('clicked()'),
                     self.doEdit)
        self.connect(self.level_group, 
                     QtCore.SIGNAL('buttonClicked(QAbstractButton*)'),
                     self.levelChanged)

    def resetSearch(self, emit_signal=True):
        """
        resetSearch() -> None

        """
        if self.controller and emit_signal:
            self.controller.reset_search()
            self.emit(QtCore.SIGNAL('textQueryChange(bool)'), False)
        else:
            self.searchBox.clearSearch()

    def backToSearch(self):
        if self.controller:
            self.controller.back_to_search()

    def doEdit(self):
        if self.controller:
            self.controller.goto_edit()

    def levelChanged(self, button):
        self.controller.set_level(self.level_map.inverse[button])

    def setLevel(self, level):
        self.level_map[level].setChecked(True)

    def executeSearch(self, text):
        """
        executeSearch(text: QString) -> None

        """
        s = str(text)
        if self.controller:
            self.controller.run_search(s)
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

    RESULT_LEVEL_MAP = \
        Bidict([(QueryController.LEVEL_ALL, GLOBAL_RESULT_VIEW),
                (QueryController.LEVEL_VISTRAIL, VERSION_RESULT_VIEW),
                (QueryController.LEVEL_WORKFLOW, WORKFLOW_RESULT_VIEW)])

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        BaseView.__init__(self)
        self.build_widget()
        self.set_title("Search")

    def set_controller(self, controller=None):
        if self.controller:
            self.disconnect(self.controller,
                     QtCore.SIGNAL('stateChanged'),
                     self.update_controller)
        self.controller = controller
        if controller:
            self.connect(self.controller,
                         QtCore.SIGNAL('stateChanged'),
                         self.update_controller)
        self.vt_controller.vistrail_view = self.version_result_view
        self.vt_controller.current_pipeline_view = \
            self.workflow_result_view.scene()
        # self.vt_controller.vistrail_view.set_controller(self.vt_controller)
        self.vt_controller.set_vistrail(controller.vistrail, None,
                                        set_log_on_vt=False)
        self.vt_controller.change_selected_version(controller.current_version)
        self.version_result_view.set_controller(self.vt_controller)
        self.workflow_result_view.set_controller(self.vt_controller)
        self.query_controller.set_vistrail_controller(controller)

    def update_controller(self):
        self.vt_controller.set_vistrail(self.controller.vistrail, None,
                                        set_log_on_vt=False)
        self.vt_controller.change_selected_version(
            self.controller.current_version)

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
        self.connect(self.version_result_view.scene(), 
                     QtCore.SIGNAL('versionSelected(int,bool,bool,bool,bool)'),
                     self.result_version_selected)
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
        self.current_display = QQueryView.VISUAL_SEARCH_VIEW
        self.current_result_view = QQueryView.VERSION_RESULT_VIEW

    def set_default_layout(self):
        from gui.module_palette import QModulePalette
        from gui.module_info import QModuleInfo
        self.set_palette_layout(
            {QtCore.Qt.LeftDockWidgetArea: QModulePalette,
             QtCore.Qt.RightDockWidgetArea: QModuleInfo,
             })
            
    def set_action_links(self):
        self.action_links = \
            { 'execute': ('query_pipeline_changed', self.set_execute_action) }

        # also add other notification here...
        from gui.vistrails_window import _app
        _app.register_notification('query_pipeline_changed', 
                                   self.set_reset_button)

    def set_reset_button(self, pipeline):
        self.query_box.setManualResetEnabled(self.pipeline_non_empty(pipeline))

    def set_result_level(self, level):
        view_idx = QQueryView.RESULT_LEVEL_MAP[level]
        if self.current_display != QQueryView.VISUAL_SEARCH_VIEW:
            self.set_display_view(view_idx)
        self.current_result_view = view_idx
        self.query_controller.update_results()
            
    def set_to_search_mode(self):
        self.set_display_view(QQueryView.VISUAL_SEARCH_VIEW)
        self.query_box.backButton.setEnabled(False)
        self.query_box.editButton.setEnabled(False)
        self.set_reset_button(self.p_controller.current_pipeline)

        from gui.vistrails_window import _app
        _app.notify('query_pipeline_changed', 
                    self.p_controller.current_pipeline)

    def set_to_result_mode(self):
        self.set_display_view(self.current_result_view)
        self.query_box.backButton.setEnabled(True)
        if self.query_controller.level >= QueryController.LEVEL_VISTRAIL:
            self.query_box.editButton.setEnabled(True)
        self.query_box.setManualResetEnabled(True)

        from gui.vistrails_window import _app
        _app.notify('query_pipeline_changed', 
                    self.p_controller.current_pipeline)

    def set_display_view(self, view_type):
        self.current_display = view_type
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
    
    def set_execute_action(self, pipeline=None):
        if not self.vt_controller:
            return False
        if pipeline is None:
            pipeline = self.p_controller.current_pipeline            
        if self.current_display == QQueryView.VISUAL_SEARCH_VIEW:
            return self.pipeline_non_empty(pipeline)
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

    def version_changed(self, version_id):
        self.vt_controller.change_selected_version(version_id)
        
    def result_version_selected(self, version_id, by_click, do_validate=True,
                                from_root=False, double_click=False):
        if by_click:
            self.query_controller.search.setCurrentVistrail(
                self.vt_controller.vistrail)
            self.vt_controller.change_selected_version(version_id, by_click, 
                                                       do_validate, from_root)
            if double_click:
                self.query_controller.set_level(QueryController.LEVEL_WORKFLOW)
                self.query_controller.show_workflow_matches()

class QueryEntry(ParameterEntry):
    def __init__(self, port_spec, function=None, parent=None):
        ParameterEntry.__init__(self, port_spec, function, parent)

    def get_widget(self):
        return self.build_widget(get_query_widget_class, False)
