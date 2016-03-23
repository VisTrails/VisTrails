###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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
""" This modules builds a widget to interact with vistrail diff
operation """
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core import system, debug
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.core.utils import VistrailsInternalError
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.gui.pipeline_view import QPipelineView
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.utils import TestVisTrailsGUI
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
import vistrails.core.db.io

import copy
from itertools import chain

################################################################################

class QFunctionItemModel(QtGui.QStandardItemModel):
    """
    QFunctionItemModel is a item model that will allow item to be
    show as a disabled one on the table
    
    """
    def __init__(self, row, col, parent=None):
        """ QFunctionItemModel(row: int, col: int, parent: QWidget)
                              -> QFunctionItemModel                             
        Initialize with a number of rows and columns
        
        """
        QtGui.QStandardItemModel.__init__(self, row, col, parent)
        self.disabledRows = {}

    def flags(self, index):
        """ flags(index: QModelIndex) -> None
        Return the current flags of the item with the index 'index'
        
        """
        if index.isValid() and self.disabledRows.has_key(index.row()):
            return (QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled |
                    QtCore.Qt.ItemIsSelectable)
        return QtGui.QStandardItemModel.flags(self,index)

    def clearList(self):
        """ clearList() -> None
        Clear all items including the disabled ones
        
        """
        self.disabledRows = {}
        self.removeRows(0,self.rowCount())

    def disableRow(self,row):
        """ disableRow(row: int) -> None
        Disable a specific row on the table
        
        """
        self.disabledRows[row] = None

class QParamTable(QtGui.QTableView):
    """
    QParamTable is a widget represents a diff between two version
    as side-by-side comparisons
    
    """
    def __init__(self, v1Name=None, v2Name=None, parent=None):
        """ QParamTable(v1Name: str, v2Name: str, parent: QWidget)
                       -> QParamTable
        Initialize the table with two version names on the header view
        
        """
        QtGui.QTableView.__init__(self, parent)
        itemModel = QFunctionItemModel(0, 2, self)
        itemModel.setHeaderData(0, QtCore.Qt.Horizontal, v1Name)
        itemModel.setHeaderData(1, QtCore.Qt.Horizontal, v2Name)
        # self.setHorizontalHeaderLabels([v1Name, v2Name])
        self.setModel(itemModel)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)        
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)        
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)        
        self.setFont(CurrentTheme.VISUAL_DIFF_PARAMETER_FONT)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
    def set_names(self, v1_name, v2_name):
        self.model().setHeaderData(0, QtCore.Qt.Horizontal, v1_name)
        self.model().setHeaderData(1, QtCore.Qt.Horizontal, v2_name)
        # self.setHorizontalHeaderLabels([v1_name, v2_name])

class QParamInspector(QtGui.QWidget):
    """
    QParamInspector is a widget acting as an inspector vistrail modules
    in diff mode. It consists of a function inspector and annotation
    inspector
    
    """
    def __init__(self, v1Name='', v2Name='',
                 parent=None, f=QtCore.Qt.WindowFlags()):
        """ QParamInspector(v1Name: str, v2Name: str,
                            parent: QWidget, f: WindowFlags)
                            -> QParamInspector
        Construct a widget containing tabs: Functions and Annotations,
        each of them is in turn a table of two columns for two
        corresponding versions.
        
        """
        QtGui.QWidget.__init__(self, parent, f | QtCore.Qt.Tool)
        self.setWindowTitle('Parameter Inspector - None')
        self.firstTime = True        
        self.boxLayout = QtGui.QVBoxLayout()
        self.boxLayout.setMargin(0)
        self.boxLayout.setSpacing(0)
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Triangular)
        self.functionsTab = QParamTable(v1Name, v2Name)
        self.tabWidget.addTab(self.functionsTab, 'Functions')        
# FIXME add annotation support back in
#         self.annotationsTab = QParamTable(v1Name, v2Name)
#         self.annotationsTab.horizontalHeader().setStretchLastSection(True)
#         self.tabWidget.addTab(self.annotationsTab, 'Annotations')        
        self.boxLayout.addWidget(self.tabWidget)
        sizeGrip = QtGui.QSizeGrip(self)
        self.boxLayout.addWidget(sizeGrip)
        self.boxLayout.setAlignment(sizeGrip, QtCore.Qt.AlignRight)
        self.setLayout(self.boxLayout)

    def closeEvent(self, e):
        """ closeEvent(e: QCloseEvent) -> None        
        Doesn't allow the QParamInspector widget to close, but just hide
        instead
        
        """
        e.ignore()
        self.parent().showInspectorAction.setChecked(False)
        

class QLegendBox(QtGui.QFrame):
    """
    QLegendBox is just a rectangular box with a solid color
    
    """
    def __init__(self, brush, size, parent=None, f=QtCore.Qt.WindowFlags()):
        """ QLegendBox(color: QBrush, size: (int,int), parent: QWidget,
                      f: WindowFlags) -> QLegendBox
        Initialize the widget with a color and fixed size
        
        """
        QtGui.QFrame.__init__(self, parent, f)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette(self.palette())
        palette.setBrush(QtGui.QPalette.Window, brush)
        self.setPalette(palette)
        self.setFixedSize(*size)
        if system.systemType in ['Darwin']:
            #the mac's nice looking messes up with the colors
            if QtCore.QT_VERSION < 0x40500:
                self.setAttribute(QtCore.Qt.WA_MacMetalStyle, False)
            else:
                self.setAttribute(QtCore.Qt.WA_MacBrushedMetal, False)
        

class QLegendWindow(QtGui.QWidget):
    """
    QLegendWindow contains a list of QLegendBox and its description
    
    """
    def __init__(self, v1Name='', v2Name='', parent=None,
                 f=QtCore.Qt.WindowFlags()):
        """ QLegendWindow(v1Name: str, v2Name: str,
                          parent: QWidget, f: WindowFlags)
                          -> QLegendWindow
        Construct a window by default with 4 QLegendBox and 4 QLabels
        
        """
        QtGui.QWidget.__init__(self, parent, f | QtCore.Qt.Tool)
        self.setWindowTitle('Visual Diff Legend')
        self.firstTime = True
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(10)
        self.gridLayout.setSpacing(10)
        self.setFont(CurrentTheme.VISUAL_DIFF_LEGEND_FONT)
        
        parent = self.parent()
        
        self.legendV1Box = QLegendBox(
            CurrentTheme.VISUAL_DIFF_FROM_VERSION_BRUSH,
            CurrentTheme.VISUAL_DIFF_LEGEND_SIZE,
            self)        
        self.gridLayout.addWidget(self.legendV1Box, 0, 0)
        self.legendV1 = QtGui.QLabel(v1Name, self)
        self.gridLayout.addWidget(self.legendV1, 0, 1)
        
        self.legendV2Box = QLegendBox(
            CurrentTheme.VISUAL_DIFF_TO_VERSION_BRUSH,            
            CurrentTheme.VISUAL_DIFF_LEGEND_SIZE,
            self)        
        self.gridLayout.addWidget(self.legendV2Box, 1, 0)
        self.legendV2 = QtGui.QLabel(v2Name, self)
        self.gridLayout.addWidget(self.legendV2, 1, 1)
        
        self.legendV12Box = QLegendBox(CurrentTheme.VISUAL_DIFF_SHARED_BRUSH,
                                       CurrentTheme.VISUAL_DIFF_LEGEND_SIZE,
                                       self)
        self.gridLayout.addWidget(self.legendV12Box, 2, 0)
        self.legendV12 = QtGui.QLabel("Shared", self)
        self.gridLayout.addWidget(self.legendV12, 2, 1)
        
        self.legendParamBox = QLegendBox(
            CurrentTheme.VISUAL_DIFF_PARAMETER_CHANGED_BRUSH,
            CurrentTheme.VISUAL_DIFF_LEGEND_SIZE,
            self)
        self.gridLayout.addWidget(self.legendParamBox,3,0)
        self.legendParam = QtGui.QLabel("Parameter Changes", self)
        self.gridLayout.addWidget(self.legendParam,3,1)

        # self.legendMatchedBox = \
        #     QLegendBox(CurrentTheme.VISUAL_DIFF_MATCH_BRUSH,
        #                CurrentTheme.VISUAL_DIFF_LEGEND_SIZE,
        #                self)
        # self.gridLayout.addWidget(self.legendMatchedBox, 4, 0)
        # self.legendMatched = QtGui.QLabel("Matched", self)
        # self.gridLayout.addWidget(self.legendMatched, 4, 1)

        self.adjustSize()
        
    def set_names(self, v1_name, v2_name):
        self.legendV1.setText(v1_name)
        self.legendV2.setText(v2_name)

    def closeEvent(self,e):
        """ closeEvent(e: QCloseEvent) -> None
        Doesn't allow the Legend widget to close, but just hide
        instead
        
        """
        e.ignore()
        self.parent().showLegendsAction.setChecked(False)
        
class QDiffProperties(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.controller = None
        self.set_title("Diff Properties")
 
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.legend = QLegendWindow()
        legend_group = QtGui.QGroupBox("Legend")
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.legend)
        legend_group.setLayout(g_layout)
        layout.addWidget(legend_group)
        layout.setStretch(0,0)
        layout.addStretch(1)
        self.params = QParamTable()
        params_group = QtGui.QGroupBox("Parameter Changes")
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.params)
        params_group.setLayout(g_layout)
        layout.addWidget(params_group)
        layout.setStretch(2,1000)

        self.cparams = QParamTable()
        params_group = QtGui.QGroupBox("Control Parameter Changes")
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.cparams)
        params_group.setLayout(g_layout)
        layout.addWidget(params_group)
        layout.setStretch(3,1000)
        
        self.annotations = QParamTable()
        params_group = QtGui.QGroupBox("Annotation Changes")
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.annotations)
        params_group.setLayout(g_layout)
        layout.addWidget(params_group)
        layout.setStretch(3,1000)
        
        self.setLayout(layout)
        self.addButtonsToToolbar()

    def addButtonsToToolbar(self):
        # Add the create analogy action
        self.createAnalogyAction = QtGui.QAction(
            CurrentTheme.VISUAL_DIFF_CREATE_ANALOGY_ICON,
            'Create analogy', None, triggered=self.createAnalogy)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.createAnalogyAction)
        self.toolWindow().toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

    def createAnalogy(self):
        if not hasattr(self.controller, 'current_diff'):
            return
        ((vistrail_a, version_a), (vistrail_b, version_b)) = \
            self.controller.current_diff_versions
        # analogy only works on single vistrail
        if not vistrail_a == vistrail_b:
            return


        default = 'from %s to %s' % (self.v1_name, self.v2_name)
        (result, ok) = QtGui.QInputDialog.getText(None, "Enter Analogy Name",
                                                  "Name of analogy:",
                                                  QtGui.QLineEdit.Normal,
                                                  default)
        if not ok:
            return
        result = str(result)
        try:
            self.controller.add_analogy(result, version_a, version_b)
        except VistrailsInternalError:
            debug.critical("Analogy name already exists")

    def set_diff(self):
        if not hasattr(self.controller, 'current_diff'):
            return
        ((vistrail_a, version_a), (vistrail_b, version_b)) = \
            self.controller.current_diff_versions

        hideUpgrades = getattr(get_vistrails_configuration(), 'hideUpgrades',
                               True)
        # Set up the version name correctly
        v1_name = self.controller.get_tag(version_a)
        if not v1_name:
            v1_name = 'Version %d' % version_a
        v2_name = self.controller.get_tag(version_b)
        if not v2_name:
            v2_name = 'Version %d' % version_b

        # Add vistrail name if necessary
        if id(vistrail_a) != id(vistrail_b):
            if vistrail_a.locator is not None:
                v1_name = "%s : %s" % (vistrail_a.locator.short_name, v1_name)
            else:
                v1_name = "Vistrail A : %s" % v1_name
            if vistrail_b.locator is not None:
                v2_name = "%s : %s" % (vistrail_b.locator.short_name, v2_name)
            else:
                v2_name = "Vistrail B : %s" % v2_name

        self.v1_name, self.v2_name = v1_name, v2_name
        
        self.legend.set_names(v1_name, v2_name)
        self.params.set_names(v1_name, v2_name)
        self.cparams.set_names(v1_name, v2_name)
        self.annotations.set_names(v1_name, v2_name)
        self.update_module()

    def set_controller(self, controller=None):
        self.controller = controller
        if self.controller is not None:
            self.set_diff()
        
    def update_module(self, module=None):
        """ moduleSelected(id: int, selectedItems: [QGraphicsItem]) -> None
        When the user click on a module, display its parameter changes
        in the Inspector
        
        """
        if module is None or not hasattr(self.controller, 'current_diff'):
            self.params.model().clearList()
            self.params.parent().setVisible(False)
            self.cparams.model().clearList()
            self.cparams.parent().setVisible(False)
            self.annotations.model().clearList()
            self.annotations.parent().setVisible(False)
            return
        
        # Interpret the diff result and setup item models
        (p1, p2, v1Andv2, heuristicMatch, v1Only, v2Only, paramChanged,
         cparamChanged, annotChanged) = self.controller.current_diff

        # # Set the window title
        # if id>self.maxId1:
        #     self.inspector.setWindowTitle('Parameter Changes - %s' %
        #                                   p2.modules[id-self.maxId1-1].name)
        # else:
        #     self.inspector.setWindowTitle('Parameter Changes - %s' %
        #                                   p1.modules[id].name)

        # FIXME set the module name/package info?
            
        to_text = lambda x:'%s(%s)' % (x[0], ','.join(v[1] for v in x[1]))
        self.setTable(module, paramChanged, self.params, to_text)
        to_text = lambda x:'%s(%s)' % (x[0], x[1])
        self.setTable(module, cparamChanged, self.cparams, to_text)
        self.setTable(module, annotChanged, self.annotations, to_text)

    def setTable(self, module, changed, table, to_text):
        # Find the parameter changed module
        model = table.model()
        model.clearList()
        matching = None
        for ((m1id, m2id), paramMatching) in changed:
            if m1id == module.id:
                #print "found match"
                matching = paramMatching
                break

        #print "matching:", matching
        # If the module has no parameter changed, just display nothing
        if not matching:          
            table.parent().setVisible(False)
            return
        
        table.parent().setVisible(True)

        # Else just layout the diff on a table
        model.insertRows(0,len(matching))
        currentRow = 0
        for (f1, f2) in matching:
            if f1[0]!=None:
                model.setData(model.index(currentRow, 0), to_text(f1))
            if f2[0]!=None:
                model.setData(model.index(currentRow, 1), to_text(f2))
            if f1==f2:
                model.disableRow(currentRow)
            currentRow += 1

        table.resizeRowsToContents()

class QDiffView(QPipelineView):
    def __init__(self, parent=None):
        QPipelineView.__init__(self, parent)
        self.set_title("Diff")
        self.diff = None
        self.diff_versions = None
        self.controller = None
        self.setReadOnlyMode(True)
        
    def set_action_links(self):
        self.action_links = \
            {'copy': ('module_changed', self.has_selected_modules),
             'showGroup': ('module_changed', self.has_selected_group),
             'configureModule': ('module_changed', self.has_selected_module),
             'documentModule': ('module_changed', self.has_selected_module),
             }
            
    def set_action_defaults(self):
        self.action_defaults.update(
            {'execute'    : [('setEnabled', False, False)],
             'history'    : [('setEnabled', False, False)],
             'search'     : [('setEnabled', False, False)],
             'explore'    : [('setEnabled', False, False)],
             'provenance' : [('setEnabled', False, False)],
             'mashup'     : [('setEnabled', False, False)]
             })
            
    def set_to_current(self):
        self.controller.set_pipeline_view(self)
        self.controller.current_diff = self.diff
        self.controller.current_diff_versions = self.diff_versions

    def set_default_layout(self):
        from vistrails.gui.module_palette import QModulePalette
        self.set_palette_layout(
            {QtCore.Qt.LeftDockWidgetArea: QModulePalette,
             QtCore.Qt.RightDockWidgetArea: QDiffProperties,
             })
        
    def version_changed(self):
        pass

    def set_controller(self, controller):
        self.controller = controller
        self.scene().controller = controller

    def get_long_title(self):
        return self.long_title
    
    def set_diff_version_names(self):
        ((vistrail_a, version_a), (vistrail_b, version_b)) = self.diff_versions
        
        # Set up the version name correctly
        v1_name = vistrail_a.getVersionName(version_a)
        if not v1_name:
            v1_name = 'Version %d' % version_a
        v2_name = vistrail_b.getVersionName(version_b)
        if not v2_name:
            v2_name = 'Version %d' % version_b

        # Add vistrail name if necessary
        if id(vistrail_a) != id(vistrail_b):
            if vistrail_a.locator is not None:
                v1_name = "%s : %s" % (vistrail_a.locator.short_name, v1_name)
            else:
                v1_name = "Vistrail A : %s" % v1_name
            if vistrail_b.locator is not None:
                v2_name = "%s : %s" % (vistrail_b.locator.short_name, v2_name)
            else:
                v2_name = "Vistrail B : %s" % v2_name
            title = "Diff: %s x %s"%(v1_name, v2_name)
        else:
            title = "Diff: %s x %s from %s" % (v1_name, v2_name,
                                               self.vistrail_view.get_name())
        self.v1_name = v1_name
        self.v2_name = v2_name
        self.set_long_title(title)
        
    def set_diff(self, version_a, version_b, vistrail_b=None):
        # Interprete the diff result
        vistrail_a = self.controller.vistrail
        if vistrail_b is None:
            vistrail_b = self.controller.vistrail
        self.diff_versions = ((vistrail_a, version_a), 
                              (vistrail_b, version_b))
        self.set_diff_version_names()
        self.diff = vistrails.core.db.io.get_workflow_diff(*self.diff_versions)
            # self.controller.vistrail.get_pipeline_diff(version_a, version_b)
        (p1, p2, v1Andv2, heuristicMatch, v1Only, v2Only, paramChanged,
         cparamChanged, annotChanged) = self.diff
        # print "  $$$ v1Andv2:", v1Andv2
        # print "  $$$ heuristicMatch:", heuristicMatch
        # print "  $$$ v1Only", v1Only
        # print "  $$$ v2Only", v2Only
        # print "  $$$ paramChanged", paramChanged
        p1.validate(False)
        p2.validate(False)
        p_both = Pipeline()
        # the abstraction map is the same for both p1 and p2
        # p_both.set_abstraction_map(p1.abstraction_map)
        
        scene = self.scene()
        scene.clearItems()

        basic_pkg = get_vistrails_basic_pkg_id()

#         # FIXME HACK: We will create a dummy object that looks like a
#         # controller so that the qgraphicsmoduleitems and the scene
#         # are happy. It will simply store the pipeline will all
#         # modules and connections of the diff, and know how to copy stuff
#         class DummyController(object):
#             def __init__(self, pip):
#                 self.current_pipeline = pip
#                 self.search = None
#             def copy_modules_and_connections(self, module_ids, connection_ids):
#                 """copy_modules_and_connections(module_ids: [long],
#                                              connection_ids: [long]) -> str
#                 Serializes a list of modules and connections
#                 """

#                 pipeline = Pipeline()
# #                 pipeline.set_abstraction_map( \
# #                     self.current_pipeline.abstraction_map)
#                 for module_id in module_ids:
#                     module = self.current_pipeline.modules[module_id]
# #                     if module.vtType == Abstraction.vtType:
# #                         abstraction = \
# #                             pipeline.abstraction_map[module.abstraction_id]
# #                         pipeline.add_abstraction(abstraction)
#                     pipeline.add_module(module)
#                 for connection_id in connection_ids:
#                     connection = self.current_pipeline.connections[connection_id]
#                     pipeline.add_connection(connection)
#                 return core.db.io.serialize(pipeline)
                
#         controller = DummyController(p_both)
#         scene.controller = controller

        # Find the max version id from v1 and start the adding process
        self.maxId1 = 0
        for m1id in p1.modules.keys():
            if m1id>self.maxId1:
                self.maxId1 = m1id
        shiftId = self.maxId1 + 1

        # First add all shared modules, just use v1 module id
        sum1_x = 0.0
        sum1_y = 0.0
        sum2_x = 0.0
        sum2_y = 0.0
        for (m1id, m2id) in chain(v1Andv2, heuristicMatch):
        #     item = scene.addModule(p1.modules[m1id],
        #                            CurrentTheme.VISUAL_DIFF_SHARED_BRUSH)
        #     item.controller = self.controller
        #     p_both.add_module(copy.copy(p1.modules[m1id]))
        #     sum1_x += p1.modules[m1id].location.x
        #     sum1_y += p1.modules[m1id].location.y
        #     sum2_x += p2.modules[m2id].location.x
        #     sum2_y += p2.modules[m2id].location.y
        # for (m1id, m2id) in heuristicMatch:
            m1 = p1.modules[m1id]
            m2 = p2.modules[m2id]

            sum1_x += p1.modules[m1id].location.x
            sum1_y += p1.modules[m1id].location.y
            sum2_x += p2.modules[m2id].location.x
            sum2_y += p2.modules[m2id].location.y            

            #this is a hack for modules with a dynamic local registry.
            #The problem arises when modules have the same name but different
            #input/output ports. We just make sure that the module we add to
            # the canvas has the ports from both modules, so we don't have
            # addconnection errors.
            port_specs = dict(((p.type, p.name), p) for p in m1.port_spec_list)
            for p in m2.port_spec_list:
                p_key = (p.type, p.name)
                if not p_key in port_specs:
                    m1.add_port_spec(p)
                elif port_specs[p_key] != p:
                    #if we add this port, we will get port overloading.
                    #To avoid this, just cast the current port to be of
                    # Module or Variant type.
                    old_port_spec = port_specs[p_key]
                    m1.delete_port_spec(old_port_spec)
                    if old_port_spec.type == 'input':
                        m_sig = '(%s:Module)' % basic_pkg
                    else:
                        m_sig = '(%s:Variant)' % basic_pkg
                    new_port_spec = PortSpec(id=old_port_spec.id,
                                             name=old_port_spec.name,
                                             type=old_port_spec.type,
                                             sigstring=m_sig)
                    m1.add_port_spec(new_port_spec)

            item = scene.addModule(p1.modules[m1id],
                                   CurrentTheme.VISUAL_DIFF_SHARED_BRUSH)
            # item = scene.addModule(p1.modules[m1id],
            #                        CurrentTheme.VISUAL_DIFF_MATCH_BRUSH)
            item.controller = self.controller
            p_both.add_module(copy.copy(p1.modules[m1id]))

        # Then add parameter changed version
        inChanged = set(m for (m, matching)
                        in chain(paramChanged, cparamChanged, annotChanged))
        for (m1id, m2id) in inChanged:
            m1 = p1.modules[m1id]
            m2 = p2.modules[m2id]
            sum1_x += p1.modules[m1id].location.x
            sum1_y += p1.modules[m1id].location.y
            sum2_x += p2.modules[m2id].location.x
            sum2_y += p2.modules[m2id].location.y

            #this is a hack for modules with a dynamic local registry.
            #The problem arises when modules have the same name but different
            #input/output ports. We just make sure that the module we add to
            # the canvas has the ports from both modules, so we don't have
            # addconnection errors.
            port_specs = dict(((p.type, p.name), p) for p in m1.port_spec_list)
            for p in m2.port_spec_list:
                p_key = (p.type, p.name)
                if not p_key in port_specs:
                    m1.add_port_spec(p)
                elif port_specs[p_key] != p:
                    #if we add this port, we will get port overloading.
                    #To avoid this, just cast the current port to be of
                    # Module or Variant type.
                    old_port_spec = port_specs[p_key]
                    m1.delete_port_spec(old_port_spec)
                    if old_port_spec.type == 'input':
                        m_sig = '(%s:Module)' % basic_pkg
                    else:
                        m_sig = '(%s:Variant)' % basic_pkg
                    new_port_spec = PortSpec(id=old_port_spec.id,
                                             name=old_port_spec.name,
                                             type=old_port_spec.type,
                                             sigstring=m_sig)
                    m1.add_port_spec(new_port_spec)
                            
            item = scene.addModule(p1.modules[m1id],
                                   CurrentTheme.VISUAL_DIFF_PARAMETER_CHANGED_BRUSH)
            item.controller = self.controller
            p_both.add_module(copy.copy(p1.modules[m1id]))

        total_len = len(v1Andv2) + + len(heuristicMatch) + len(paramChanged)
        if total_len != 0:
            avg1_x = sum1_x / total_len
            avg1_y = sum1_y / total_len
            avg2_x = sum2_x / total_len
            avg2_y = sum2_y / total_len
        else:
            avg1_x = 0.0
            avg1_y = 0.0
            avg2_x = 0.0
            avg2_y = 0.0
#         avg1_x = sum1_x / total_len if total_len != 0 else 0.0
#         avg1_y = sum1_y / total_len if total_len != 0 else 0.0
#         avg2_x = sum2_x / total_len if total_len != 0 else 0.0
#         avg2_y = sum2_y / total_len if total_len != 0 else 0.0

        # Now add the ones only applicable for v1, still using v1 ids
        for m1id in v1Only:
            item = scene.addModule(p1.modules[m1id],
                                   CurrentTheme.VISUAL_DIFF_FROM_VERSION_BRUSH)
            item.controller = self.controller
            p_both.add_module(copy.copy(p1.modules[m1id]))

        # Now add the ones for v2 only but must shift the ids away from v1
        for m2id in v2Only:
            p2_module = copy.copy(p2.modules[m2id])
            p2_module.id = m2id + shiftId
            # p2.modules[m2id].id = m2id + shiftId
            p2_module.location.x -= avg2_x - avg1_x
            p2_module.location.y -= avg2_y - avg1_y
            item = scene.addModule(p2_module, #p2.modules[m2id],
                                   CurrentTheme.VISUAL_DIFF_TO_VERSION_BRUSH)
            item.controller = self.controller
            # p_both.add_module(copy.copy(p2.modules[m2id]))
            p_both.add_module(p2_module)
            

        # Create a mapping between share modules between v1 and v2
        v1Tov2 = {}
        v2Tov1 = {}
        for (m1id, m2id) in v1Andv2:
            v1Tov2[m1id] = m2id
            v2Tov1[m2id] = m1id
        for (m1id, m2id) in heuristicMatch:
            v1Tov2[m1id] = m2id
            v2Tov1[m2id] = m1id
        for (m1id, m2id) in inChanged:
            v1Tov2[m1id] = m2id
            v2Tov1[m2id] = m1id

        # Next we're going to add connections, only connections of
        # v2Only need to shift their ids
        if p1.connections.keys():
            connectionShift = max(p1.connections.keys())+1
        else:
            connectionShift = 0
        allConnections = copy.copy(p1.connections)
        sharedConnections = []
        v2OnlyConnections = []        
        for (cid2, connection2) in copy.copy(p2.connections.items()):
            if connection2.sourceId in v2Only:
                connection2.sourceId += shiftId
            else:
                connection2.sourceId = v2Tov1[connection2.sourceId]
                
            if connection2.destinationId in v2Only:
                connection2.destinationId += shiftId
            else:
                connection2.destinationId = v2Tov1[connection2.destinationId]

            # Is this connection also shared by p1?
            shared = False
            for (cid1, connection1) in p1.connections.items():
                if (connection1.sourceId==connection2.sourceId and
                    connection1.destinationId==connection2.destinationId and
                    connection1.source.name==connection2.source.name and
                    connection1.destination.name==connection2.destination.name):
                    sharedConnections.append(cid1)
                    shared = True
                    break
            if not shared:
                allConnections[cid2+connectionShift] = connection2
                connection2.id = cid2+connectionShift
                v2OnlyConnections.append(cid2+connectionShift)

        connectionItems = []
        for c in allConnections.values():
            p_both.add_connection(copy.copy(c))
            connectionItems.append(scene.addConnection(c))

        # Color Code connections
        for c in connectionItems:
            if c.id in sharedConnections:
                pass
            elif c.id in v2OnlyConnections:
                pen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
                pen.setBrush(CurrentTheme.VISUAL_DIFF_TO_VERSION_BRUSH)
                c.connectionPen = pen
            else:
                pen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
                pen.setBrush(CurrentTheme.VISUAL_DIFF_FROM_VERSION_BRUSH)
                c.connectionPen = pen

       
        scene.current_pipeline = p_both

        scene.updateSceneBoundingRect()
        scene.fitToView(self, True)

class QVisualDiff(QtGui.QMainWindow):
    """
    QVisualDiff is a main widget for Visual Diff containing a GL
    Widget to draw the pipeline
    
    """
    def __init__(self, vistrail, v1, v2,
                 controller,
                 parent=None, f=QtCore.Qt.WindowFlags()):
        """ QVisualDiff(vistrail: Vistrail, v1: str, v2: str,
                        parent: QWidget, f: WindowFlags) -> QVisualDiff
        Initialize with all
        
        """
        # Set up the version name correctly
        v1Name = vistrail.getVersionName(v1)
        if not v1Name: v1Name = 'Version %d' % v1
        v2Name = vistrail.getVersionName(v2)        
        if not v2Name: v2Name = 'Version %d' % v2
        
        # Actually perform the diff and store its result
        self.diff = vistrail.get_pipeline_diff(v1, v2)

        self.v1_name = v1Name
        self.v2_name = v2Name
        self.v1 = v1
        self.v2 = v2
        self.controller = controller

        # Create the top-level Visual Diff window
        windowDecors = f | QtCore.Qt.Dialog |QtCore.Qt.WindowMaximizeButtonHint
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle('Visual Diff - from %s to %s' % (v1Name, v2Name))
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))
        self.createPipelineView()
        self.createToolBar()
        self.createToolWindows(v1Name, v2Name)

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.ShortcutOverride and \
                event.key() == QtCore.Qt.Key_W and \
                event.modifiers() == QtCore.Qt.ControlModifier:
            event.accept()
            self.close()
        return QtGui.QMainWindow.eventFilter(self, object, event)

    def closeEvent(self, event):
        self.inspector.close()
        self.legendWindow.close()

    def createPipelineView(self):
        """ createPipelineView() -> None        
        Create a center pipeline view for Visual Diff and setup the
        view based on the diff result self.diff
        
        """
        # Initialize the shape engine
        self.pipelineView = QPipelineView()
        self.setCentralWidget(self.pipelineView)

        # Add all the shapes into the view
        self.createDiffPipeline()

        # Hook shape selecting functions
        self.connect(self.pipelineView.scene(), QtCore.SIGNAL("moduleSelected"),
                     self.moduleSelected)

    def createToolBar(self):
        """ createToolBar() -> None        
        Create the default toolbar of Visual Diff window with two
        buttons to toggle the Parameter Inspector and Legend window
        
        """
        # Initialize the Visual Diff toolbar
        self.toolBar = self.addToolBar('Visual Diff Toolbar')
        self.toolBar.setMovable(False)

        # Add the Show Parameter Inspector action
        self.showInspectorAction = self.toolBar.addAction(
            CurrentTheme.VISUAL_DIFF_SHOW_PARAM_ICON,
            'Show Parameter Inspector window')
        self.showInspectorAction.setCheckable(True)
        self.connect(self.showInspectorAction, QtCore.SIGNAL("toggled(bool)"),
                     self.toggleShowInspector)
        
        # Add the Show Legend window action
        self.showLegendsAction = self.toolBar.addAction(
            CurrentTheme.VISUAL_DIFF_SHOW_LEGEND_ICON,
            'Show Legends')
        self.showLegendsAction.setCheckable(True)
        self.connect(self.showLegendsAction, QtCore.SIGNAL("toggled(bool)"),
                     self.toggleShowLegend)

        # Add the create analogy action
        self.createAnalogyAction = self.toolBar.addAction(
            CurrentTheme.VISUAL_DIFF_CREATE_ANALOGY_ICON,
            'Create analogy')
        self.connect(self.createAnalogyAction, QtCore.SIGNAL("triggered()"),
                     self.createAnalogy)

    def createAnalogy(self):
        default = 'from %s to %s' % (self.v1_name, self.v2_name)
        (result, ok) = QtGui.QInputDialog.getText(None, "Enter Analogy Name",
                                                  "Name of analogy:",
                                                  QtGui.QLineEdit.Normal,
                                                  default)
        if not ok:
            return
        result = str(result)
        try:
            self.controller.add_analogy(result, self.v1, self.v2)
        except VistrailsInternalError:
            debug.critical("Analogy name already exists")
        
    def createToolWindows(self, v1Name, v2Name):
        """ createToolWindows(v1Name: str, v2Name: str) -> None
        Create Inspector and Legend window

        """
        self.inspector = QParamInspector(v1Name, v2Name, self)
        self.inspector.resize(QtCore.QSize(
            *CurrentTheme.VISUAL_DIFF_PARAMETER_WINDOW_SIZE))
        self.legendWindow = QLegendWindow(v1Name, v2Name,self)

    def moduleSelected(self, id, selectedItems):
        """ moduleSelected(id: int, selectedItems: [QGraphicsItem]) -> None
        When the user click on a module, display its parameter changes
        in the Inspector
        
        """
        if len(selectedItems)!=1 or id==-1:
            self.moduleUnselected()
            return
        
        # Interprete the diff result and setup item models
        (p1, p2, v1Andv2, heuristicMatch, v1Only, v2Only, paramChanged) = \
            self.diff

        # Set the window title
        if id>self.maxId1:
            self.inspector.setWindowTitle('Parameter Changes - %s' %
                                          p2.modules[id-self.maxId1-1].name)
        else:
            self.inspector.setWindowTitle('Parameter Changes - %s' %
                                          p1.modules[id].name)
            
        # Clear the old inspector
        functions = self.inspector.functionsTab.model()
#         annotations = self.inspector.annotationsTab.model()
        functions.clearList()
#         annotations.clearList()

        # Find the parameter changed module
        matching = None
        for ((m1id, m2id), paramMatching) in paramChanged:
            if m1id==id:
                matching = paramMatching
                break

        # If the module has no parameter changed, just display nothing
        if not matching:          
            return
        
        # Else just layout the diff on a table
        functions.insertRows(0,len(matching))
        currentRow = 0
        for (f1, f2) in matching:
            if f1[0]!=None:
                functions.setData(
                    functions.index(currentRow, 0),
                    '%s(%s)' % (f1[0], ','.join(v[1] for v in f1[1])))
            if f2[0]!=None:
                functions.setData(
                    functions.index(currentRow, 1),
                    '%s(%s)' % (f2[0], ','.join(v[1] for v in f2[1])))
            if f1==f2:                
                functions.disableRow(currentRow)
            currentRow += 1

        self.inspector.functionsTab.resizeRowsToContents()
#         self.inspector.annotationsTab.resizeRowsToContents()

    def moduleUnselected(self):
        """ moduleUnselected() -> None
        When a user selects nothing, make sure to display nothing as well
        
        """
#         self.inspector.annotationsTab.model().clearList()
        self.inspector.functionsTab.model().clearList()
        self.inspector.setWindowTitle('Parameter Changes - None')

    def toggleShowInspector(self):
        """ toggleShowInspector() -> None
        Show/Hide the inspector when toggle this button
        
        """
        if self.inspector.firstTime:
            max_geom = QtGui.QApplication.desktop().screenGeometry(self)
            if (self.frameSize().width() <
                max_geom.width() - self.inspector.width()):
                self.inspector.move(self.pos().x()+self.frameSize().width(),
                                    self.pos().y())
            else:
                self.inspector.move(self.pos().x()+self.frameSize().width()-
                                   self.inspector.frameSize().width(),
                                   self.pos().y() +
                                    self.legendWindow.frameSize().height())
            self.inspector.firstTime = False
        self.inspector.setVisible(self.showInspectorAction.isChecked())
            
    def toggleShowLegend(self):
        """ toggleShowLegend() -> None
        Show/Hide the legend window when toggle this button
        
        """
        if self.legendWindow.firstTime:
            self.legendWindow.move(self.pos().x()+self.frameSize().width()-
                                   self.legendWindow.frameSize().width(),
                                   self.pos().y())
        self.legendWindow.setVisible(self.showLegendsAction.isChecked())
        if self.legendWindow.firstTime:
            self.legendWindow.firstTime = False
            self.legendWindow.setFixedSize(self.legendWindow.size())            
                
    def createDiffPipeline(self):
        """ createDiffPipeline() -> None        
        Actually walk through the self.diff result and add all modules
        into the pipeline view
        
        """

        # Interprete the diff result
        (p1, p2, v1Andv2, heuristicMatch, v1Only, v2Only, paramChanged) = \
            self.diff
        self.controller.validate(p1, False)
        self.controller.validate(p2, False)
        p_both = Pipeline()
        # the abstraction map is the same for both p1 and p2
        # p_both.set_abstraction_map(p1.abstraction_map)
        
        scene = self.pipelineView.scene()
        scene.clearItems()

        basic_pkg = get_vistrails_basic_pkg_id()

        # FIXME HACK: We will create a dummy object that looks like a
        # controller so that the qgraphicsmoduleitems and the scene
        # are happy. It will simply store the pipeline will all
        # modules and connections of the diff, and know how to copy stuff
        class DummyController(object):
            def __init__(self, pip):
                self.current_pipeline = pip
                self.search = None
            def copy_modules_and_connections(self, module_ids, connection_ids):
                """copy_modules_and_connections(module_ids: [long],
                                             connection_ids: [long]) -> str
                Serializes a list of modules and connections
                """

                pipeline = Pipeline()
#                 pipeline.set_abstraction_map( \
#                     self.current_pipeline.abstraction_map)
                for module_id in module_ids:
                    module = self.current_pipeline.modules[module_id]
#                     if module.vtType == Abstraction.vtType:
#                         abstraction = \
#                             pipeline.abstraction_map[module.abstraction_id]
#                         pipeline.add_abstraction(abstraction)
                    pipeline.add_module(module)
                for connection_id in connection_ids:
                    connection = self.current_pipeline.connections[connection_id]
                    pipeline.add_connection(connection)
                return vistrails.core.db.io.serialize(pipeline)
                
        controller = DummyController(p_both)
        scene.controller = controller

        # Find the max version id from v1 and start the adding process
        self.maxId1 = 0
        for m1id in p1.modules.keys():
            if m1id>self.maxId1:
                self.maxId1 = m1id
        shiftId = self.maxId1 + 1

        # First add all shared modules, just use v1 module id
        sum1_x = 0.0
        sum1_y = 0.0
        sum2_x = 0.0
        sum2_y = 0.0
        for (m1id, m2id) in v1Andv2:
            item = scene.addModule(p1.modules[m1id],
                                   CurrentTheme.VISUAL_DIFF_SHARED_BRUSH)
            item.controller = controller
            p_both.add_module(copy.copy(p1.modules[m1id]))
            sum1_x += p1.modules[m1id].location.x
            sum1_y += p1.modules[m1id].location.y
            sum2_x += p2.modules[m2id].location.x
            sum2_y += p2.modules[m2id].location.y
        for (m1id, m2id) in heuristicMatch:
            m1 = p1.modules[m1id]
            m2 = p2.modules[m2id]

            sum1_x += p1.modules[m1id].location.x
            sum1_y += p1.modules[m1id].location.y
            sum2_x += p2.modules[m2id].location.x
            sum2_y += p2.modules[m2id].location.y            

            #this is a hack for modules with a dynamic local registry.
            #The problem arises when modules have the same name but different
            #input/output ports. We just make sure that the module we add to
            # the canvas has the ports from both modules, so we don't have
            # addconnection errors.
            port_specs = dict(((p.type, p.name), p) for p in m1.port_spec_list)
            for p in m2.port_spec_list:
                p_key = (p.type, p.name)
                if not p_key in port_specs:
                    m1.add_port_spec(p)
                elif port_specs[p_key] != p:
                    #if we add this port, we will get port overloading.
                    #To avoid this, just cast the current port to be of
                    # Module or Variant type.
                    old_port_spec = port_specs[p_key]
                    m1.delete_port_spec(old_port_spec)
                    if old_port_spec.type == 'input':
                        m_sig = '(%s:Module)' % basic_pkg
                    else:
                        m_sig = '(%s:Variant)' % basic_pkg
                    new_port_spec = PortSpec(id=old_port_spec.id,
                                             name=old_port_spec.name,
                                             type=old_port_spec.type,
                                             sigstring=m_sig)
                    m1.add_port_spec(new_port_spec)

            item = scene.addModule(p1.modules[m1id],
                                   CurrentTheme.VISUAL_DIFF_MATCH_BRUSH)
            item.controller = controller
            p_both.add_module(copy.copy(p1.modules[m1id]))

        # Then add parameter changed version
        for ((m1id, m2id), matching) in paramChanged:
            m1 = p1.modules[m1id]
            m2 = p2.modules[m2id]
            
            sum1_x += p1.modules[m1id].location.x
            sum1_y += p1.modules[m1id].location.y
            sum2_x += p2.modules[m2id].location.x
            sum2_y += p2.modules[m2id].location.y

            #this is a hack for modules with a dynamic local registry.
            #The problem arises when modules have the same name but different
            #input/output ports. We just make sure that the module we add to
            # the canvas has the ports from both modules, so we don't have
            # addconnection errors.
            port_specs = dict(((p.type, p.name), p) for p in m1.port_spec_list)
            for p in m2.port_spec_list:
                p_key = (p.type, p.name)
                if not p_key in port_specs:
                    m1.add_port_spec(p)
                elif port_specs[p_key] != p:
                    #if we add this port, we will get port overloading.
                    #To avoid this, just cast the current port to be of
                    # Module or Variant type.
                    old_port_spec = port_specs[p_key]
                    m1.delete_port_spec(old_port_spec)
                    if old_port_spec.type == 'input':
                        m_sig = '(%s:Module)' % basic_pkg
                    else:
                        m_sig = '(%s:Variant)' % basic_pkg
                    new_port_spec = PortSpec(id=old_port_spec.id,
                                             name=old_port_spec.name,
                                             type=old_port_spec.type,
                                             sigstring=m_sig)
                    m1.add_port_spec(new_port_spec)

            item = scene.addModule(p1.modules[m1id],
                                   CurrentTheme.VISUAL_DIFF_PARAMETER_CHANGED_BRUSH)
            item.controller = controller
            p_both.add_module(copy.copy(p1.modules[m1id]))

        total_len = len(v1Andv2) + + len(heuristicMatch) + len(paramChanged)
        if total_len != 0:
            avg1_x = sum1_x / total_len
            avg1_y = sum1_y / total_len
            avg2_x = sum2_x / total_len
            avg2_y = sum2_y / total_len
        else:
            avg1_x = 0.0
            avg1_y = 0.0
            avg2_x = 0.0
            avg2_y = 0.0
#         avg1_x = sum1_x / total_len if total_len != 0 else 0.0
#         avg1_y = sum1_y / total_len if total_len != 0 else 0.0
#         avg2_x = sum2_x / total_len if total_len != 0 else 0.0
#         avg2_y = sum2_y / total_len if total_len != 0 else 0.0

        # Now add the ones only applicable for v1, still using v1 ids
        for m1id in v1Only:
            item = scene.addModule(p1.modules[m1id],
                                   CurrentTheme.VISUAL_DIFF_FROM_VERSION_BRUSH)
            item.controller = controller
            p_both.add_module(copy.copy(p1.modules[m1id]))

        # Now add the ones for v2 only but must shift the ids away from v1
        for m2id in v2Only:
            p2_module = copy.copy(p2.modules[m2id])
            p2_module.id = m2id + shiftId
            # p2.modules[m2id].id = m2id + shiftId
            p2_module.location.x -= avg2_x - avg1_x
            p2_module.location.y -= avg2_y - avg1_y
            item = scene.addModule(p2_module, #p2.modules[m2id],
                                   CurrentTheme.VISUAL_DIFF_TO_VERSION_BRUSH)
            item.controller = controller
            # p_both.add_module(copy.copy(p2.modules[m2id]))
            p_both.add_module(p2_module)
            

        # Create a mapping between share modules between v1 and v2
        v1Tov2 = {}
        v2Tov1 = {}
        for (m1id, m2id) in v1Andv2:
            v1Tov2[m1id] = m2id
            v2Tov1[m2id] = m1id
        for (m1id, m2id) in heuristicMatch:
            v1Tov2[m1id] = m2id
            v2Tov1[m2id] = m1id
        for ((m1id, m2id), matching) in paramChanged:
            v1Tov2[m1id] = m2id
            v2Tov1[m2id] = m1id

        # Next we're going to add connections, only connections of
        # v2Only need to shift their ids
        if p1.connections.keys():
            connectionShift = max(p1.connections.keys())+1
        else:
            connectionShift = 0
        allConnections = copy.copy(p1.connections)
        sharedConnections = []
        v2OnlyConnections = []        
        for (cid2, connection2) in copy.copy(p2.connections.items()):
            if connection2.sourceId in v2Only:
                connection2.sourceId += shiftId
            else:
                connection2.sourceId = v2Tov1[connection2.sourceId]
                
            if connection2.destinationId in v2Only:
                connection2.destinationId += shiftId
            else:
                connection2.destinationId = v2Tov1[connection2.destinationId]

            # Is this connection also shared by p1?
            shared = False
            for (cid1, connection1) in p1.connections.items():
                if (connection1.sourceId==connection2.sourceId and
                    connection1.destinationId==connection2.destinationId and
                    connection1.source.name==connection2.source.name and
                    connection1.destination.name==connection2.destination.name):
                    sharedConnections.append(cid1)
                    shared = True
                    break
            if not shared:
                allConnections[cid2+connectionShift] = connection2
                connection2.id = cid2+connectionShift
                v2OnlyConnections.append(cid2+connectionShift)

        connectionItems = []
        for c in allConnections.values():
            p_both.add_connection(copy.copy(c))
            connectionItems.append(scene.addConnection(c))

        # Color Code connections
        for c in connectionItems:
            if c.id in sharedConnections:
                pass
            elif c.id in v2OnlyConnections:
                pen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
                pen.setBrush(CurrentTheme.VISUAL_DIFF_TO_VERSION_BRUSH)
                c.connectionPen = pen
            else:
                pen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
                pen.setBrush(CurrentTheme.VISUAL_DIFF_FROM_VERSION_BRUSH)
                c.connectionPen = pen

       

        scene.updateSceneBoundingRect()
        scene.fitToView(self.pipelineView, True)


################################################################################
# Testing


class TestDiffView(TestVisTrailsGUI):
    def setUp(self):
        try:
            import vtk
        except ImportError:
            self.skipTest("VTK is not available")
        from vistrails.tests.utils import enable_package
        enable_package('org.vistrails.vistrails.vtk')

    def test_diff(self):
        import vistrails.api
        import vistrails.core.system
        import os.path
        from vistrails.core.configuration import get_vistrails_configuration
        filename = os.path.join(
            vistrails.core.system.vistrails_root_directory(),
            'tests', 'resources', 'terminator.vt')
        view = vistrails.api.open_vistrail_from_file(filename)
        view.controller.change_selected_version(0)
        # get tags
        v1 = view.controller.vistrail.get_version_number('Volume Rendering HW')
        v2 = view.controller.vistrail.get_version_number('Volume Rendering SW')

        hideUpgrades = getattr(get_vistrails_configuration(), 'hideUpgrades', True)
        # without upgrades
        setattr(get_vistrails_configuration(), 'hideUpgrades', False)
        view.diff_requested(v1, v2)
        # with upgrades
        setattr(get_vistrails_configuration(), 'hideUpgrades', True)
        view.diff_requested(v1, v2)
        setattr(get_vistrails_configuration(), 'hideUpgrades', hideUpgrades)
