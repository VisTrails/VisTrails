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

""" The file describes the parameter tree view that allows changing the alias
of parameters

QAliasParameterView
"""
from __future__ import division

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from vistrails.core.inspector import PipelineInspector
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.gui.common_widgets import QSearchTreeWindow, QSearchTreeWidget
from vistrails.gui.paramexplore.pe_pipeline import QAnnotatedPipelineView
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
from vistrails.gui.theme import CurrentTheme
from vistrails.core.utils import InstanceObject

################################################################################
class QAliasParameterView(QtGui.QWidget, QVistrailsPaletteInterface):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.set_title("Mashup Pipeline")
        layout = QtGui.QVBoxLayout()
        self.parameter_panel = QAliasParameterPanel()
        font = QtGui.QFont("Arial", 11, QtGui.QFont.Normal)
        font.setItalic(True)
        label = QtGui.QLabel("Double-click a parameter to change alias")
        label.setFont(font)
        param_group = QtGui.QGroupBox(self.parameter_panel.windowTitle())
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(2)
        g_layout.addWidget(label)
        g_layout.addWidget(self.parameter_panel)
        param_group.setLayout(g_layout)
        layout.addWidget(param_group)
        
        self.pipeline_view = QAnnotatedPipelineView()
        self.pipeline_view.setReadOnlyMode(True)
        p_view_group = QtGui.QGroupBox(self.pipeline_view.windowTitle())
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.pipeline_view)
        p_view_group.setLayout(g_layout)
        layout.addWidget(p_view_group)
        self.setLayout(layout)
        
        self.parameter_panel.treeWidget.aliasChanged.connect(self.aliasChanged)
        
    def updateMshpController(self, mshpController):
        from vistrails.gui.vistrails_window import _app
        self.mshpController = mshpController
        self.parameter_panel.set_pipeline(
                        self.mshpController.vtPipeline)
        self.pipeline_view.set_controller(self.mshpController.vtController)
        self.mshpController.vtController.current_pipeline_view = \
                                                            self.pipeline_view
        self.pipeline_view.scene().current_pipeline = self.mshpController.vtPipeline
        self.mshpController.vtController.current_pipeline = self.mshpController.vtPipeline
        
        #print "**** should update mashup pipeline view "
        
        #self.pipeline_view.scene().setupScene(self.mshpController.vtPipeline)
        self.pipeline_view.scene().clear()
        self.pipeline_view.version_changed()
        self.pipeline_view.zoomToFit()
        self.pipeline_view.updateAnnotatedIds(
                        self.mshpController.vtPipeline)
        #_app.notify('mashup_pipeline_view_set')
        
    def updateMshpVersion(self, version):
        #print "will update alias param view"
        self.parameter_panel.set_pipeline(
                        self.mshpController.vtPipeline)
        self.pipeline_view.version_changed()
        
    def zoomToFit(self):
        if self.pipeline_view:
            self.pipeline_view.zoomToFit()
            
    def aliasChanged(self, param):
        from vistrails.gui.vistrails_window import _app
        _app.notify('alias_changed', param)
        
################################################################################

class QAliasParameterPanel(QSearchTreeWindow):
    """
    QAliasParameterPanel is a special widget for displaying methods and 
    parameters inside a pipeline that allow changing aliases
    
    """
    def createTreeWidget(self):
        """ createTreeWidget() -> QModuleTreeWidget
        Return the search tree widget for this window
        
        """
        self.setWindowTitle("Parameter Aliases")
        return QAliasParameterTreeWidget(self)

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline
        self.treeWidget.updateFromPipeline(pipeline)
        
################################################################################
class QAliasParameterTreeWidget(QSearchTreeWidget):
    """
    QAliasParameterTreeWidget is a subclass of QSearchTreeWidget to display all
    Vistrails Module
    
    """
    #signals
    aliasChanged = pyqtSignal(InstanceObject)
    
    def __init__(self, parent=None):
        """ QAliasParameterTreeWidget(parent: QWidget) -> QParameterTreeWidget
        Set up size policy and header

        """
        QSearchTreeWidget.__init__(self, parent)
        self.header().hide()
        self.setRootIsDecorated(False)
        self.delegate = QAliasParameterTreeWidgetItemDelegate(self, self)
        self.setItemDelegate(self.delegate)
        self.aliasNames = []
        self.itemDoubleClicked.connect(self.changeAlias)
    def updateFromPipeline(self, pipeline):
        """ updateFromPipeline(pipeline: Pipeline) -> None
        Read the list of aliases and parameters from the pipeline
        
        """
        self.clear()
        if not pipeline:
            return

        # Update the aliases
#        if len(pipeline.aliases)>0:
#            aliasRoot = QParameterTreeWidgetItem(None, self, ['Aliases'])
#            aliasRoot.setFlags(QtCore.Qt.ItemIsEnabled,
#                               )
#            for (alias, info) in pipeline.aliases.iteritems():
#                ptype, pId, parentType, parentId, _ = info
#                parameter = pipeline.db_get_object(ptype, pId)
#                v = parameter.strValue
#                aType = parameter.type
#                aIdentifier = parameter.identifier
#                aNamespace = parameter.namespace
#                label = ['%s = %s' % (alias, v)]
#                pInfo = InstanceObject(type=aType,
#                                      identifier=aIdentifier,
#                                      namespace=aNamespace,
#                                      value=v,
#                                      id=pId,
#                                      dbtype=ptype,
#                                      parent_dbtype=parentType,
#                                      parent_id=parentId,
#                                      is_alias=True)
#                aliasItem = QParameterTreeWidgetItem((alias, [pInfo]),
#                                                     aliasRoot, label)
#            aliasRoot.setExpanded(True)
            
        # Now go through all modules and functions
        self.aliasNames = pipeline.aliases.keys()
        inspector = PipelineInspector()
        inspector.inspect_ambiguous_modules(pipeline)
        sortedModules = sorted(pipeline.modules.iteritems(),
                               key=lambda item: item[1].name)
        for mId, module in sortedModules:
            if len(module.functions)>0:
                mLabel = [module.name]
                moduleItem = None
                for fId in xrange(len(module.functions)):
                    function = module.functions[fId]
                    if len(function.params)==0: continue
                    if moduleItem==None:
                        if inspector.annotated_modules.has_key(mId):
                            annotatedId = inspector.annotated_modules[mId]
                            moduleItem = QAliasParameterTreeWidgetItem(annotatedId,
                                                                       self, mLabel)
                        else:
                            moduleItem = QAliasParameterTreeWidgetItem(None,
                                                                  self, mLabel)
                    #v = ', '.join([p.strValue for p in function.params])
                    label = ['%s'%function.name]
                    
                    pList = [InstanceObject(type=function.params[pId].type,
                                           identifier=function.params[pId].identifier,
                                           namespace=function.params[pId].namespace,
                                           value=function.params[pId].strValue,
                                           id=function.params[pId].real_id,
                                           dbtype=ModuleParam.vtType,
                                           parent_dbtype=function.vtType,
                                           parent_id=function.real_id,
                                           alias=function.params[pId].alias,
                                           mId=mId)
                             for pId in xrange(len(function.params))]
                    mName = module.name
                    if moduleItem.parameter!=None:
                        mName += '(%d)' % moduleItem.parameter
                    fName = '%s :: %s' % (mName, function.name)
                    mItem = QAliasParameterTreeWidgetItem((fName, pList),
                                                     moduleItem,
                                                     label)
                if moduleItem:
                    moduleItem.setExpanded(True)
                    
    @pyqtSlot(QtGui.QTreeWidgetItem, int)    
    def changeAlias(self, item, column ):
        """ itemClicked(item:  , column: int) -> None        
        If mouse click on the item, show up a dialog to change/add
        the alias name
        
        """
        if isinstance(item.parameter, InstanceObject):
            (text, ok) = QtGui.QInputDialog.getText(self,
                                                    'Set Parameter Alias',
                                                    'Enter the parameter alias',
                                                    QtGui.QLineEdit.Normal,
                                                    item.parameter.alias)
            while ok and str(text) in self.aliasNames:
                msg =" This alias is already being used.\
 Please enter a different parameter alias "
                (text, ok) = QtGui.QInputDialog.getText(self,
                                                        'Set Parameter Alias',
                                                        msg,
                                                        QtGui.QLineEdit.Normal,
                                                        text)
            if ok and item.parameter.alias != str(text):
                item.parameter.alias = str(text)
                item.updateAlias()
                self.aliasChanged.emit(item.parameter)
            
            
        
class QAliasParameterTreeWidgetItemDelegate(QtGui.QItemDelegate):
    """    
    QAliasParameterTreeWidgetItemDelegate will override the original
    QTreeWidget paint function to draw buttons for top-level item
    similar to QtDesigner. This mimics
    Qt/tools/designer/src/lib/shared/sheet_delegate, which is only a
    private class from QtDesigned.
    
    """
    def __init__(self, view, parent):
        """ QParameterTreeWidgetItemDelegate(view: QTreeView,
                                          parent: QWidget)
                                          -> QParameterTreeWidgetItemDelegate
        Create the item delegate given the tree view
        
        """
        QtGui.QItemDelegate.__init__(self, parent)
        self.treeView = view

    def paint(self, painter, option, index):
        """ painter(painter: QPainter, option QStyleOptionViewItem,
                    index: QModelIndex) -> None
        Repaint the top-level item to have a button-look style
        
        """
        model = index.model()
        if (model.parent(index).isValid()==False or 
            model.parent(index).parent().isValid()==False):
            style = self.treeView.style()
            r = option.rect
            textrect = QtCore.QRect(r.left() + 10,
                                    r.top(),
                                    r.width() - 10,
                                    r.height())
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            text = option.fontMetrics.elidedText(
                model.data(index, QtCore.Qt.DisplayRole),
                QtCore.Qt.ElideMiddle, 
                textrect.width()-10)
            style.drawItemText(painter,
                               textrect,
                               QtCore.Qt.AlignLeft,
                               option.palette,
                               self.treeView.isEnabled(),
                               text)
            painter.setPen(QtGui.QPen(QtCore.Qt.black))
            fm = QtGui.QFontMetrics(font)
            size = fm.size(QtCore.Qt.TextSingleLine, text)
            #painter.drawLine(textrect.left()-5,
            #                 textrect.bottom()-1,
            #                 textrect.left()+size.width()+5,
            #                 textrect.bottom()-1)

            annotatedId = model.data(index, QtCore.Qt.UserRole+1)            
            if annotatedId:
                idRect = QtCore.QRect(
                    QtCore.QPoint(textrect.left()+size.width()+5,
                                  textrect.top()),
                    textrect.bottomRight())
                QAnnotatedPipelineView.drawId(painter, idRect,
                                              annotatedId,
                                              QtCore.Qt.AlignLeft |
                                              QtCore.Qt.AlignVCenter)
        else:
            QtGui.QItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        """ sizeHint(option: QStyleOptionViewItem, index: QModelIndex) -> None
        Take into account the size of the top-level button
        
        """
        return (QtGui.QItemDelegate.sizeHint(self, option, index) +
                QtCore.QSize(2, 2))
            

class QAliasParameterTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    QParameterTreeWidgetItem represents module on QParameterTreeWidget
    
    """
    def __init__(self, info, parent, labelList):
        """ QAliasParameterTreeWidgetItem(info: (str, []),
                                     parent: QTreeWidgetItem
                                     labelList: string)
                                     -> QParameterTreeWidget
                                     
        Create a new tree widget item with a specific parent and
        labels. info describing a set of parameters as follow:
        (name, [InstanceObject]):
           name  = Name of the parameter set (alias or function)
        If this item is a top-level item, info can either be None or
        an integer specifying the annotated id of this module

        """
        self.parameter = info
        QtGui.QTreeWidgetItem.__init__(self, parent, labelList)
        if isinstance(self.parameter, int):
            self.setData(0, QtCore.Qt.UserRole+1, self.parameter)
        elif isinstance(self.parameter, tuple):
            for param in self.parameter[1]:
                label = ['']
                item = QAliasParameterTreeWidgetItem(param, self, label)
                item.setFlags(QtCore.Qt.ItemIsEnabled|
                              QtCore.Qt.ItemIsSelectable)
                item.updateAlias()
            self.setExpanded(True)
    
    def updateAlias(self):    
        if isinstance(self.parameter, InstanceObject):
            if self.parameter.alias != '':
                self.setText(0,'%s(%s):%s'%(self.parameter.alias, 
                                          self.parameter.type,
                                          self.parameter.value))
                self.setIcon(0,CurrentTheme.MASHUP_ALIAS_ICON)
            else:
                self.setText(0,'%s:%s'%(self.parameter.type,
                                      self.parameter.value))
                self.setIcon(0,QtGui.QIcon())
