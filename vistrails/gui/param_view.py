############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
""" The file describes the parameter tree view

QParameterView
"""
from PyQt4 import QtCore, QtGui
from core.inspector import PipelineInspector
from gui.common_widgets import QSearchTreeWindow, QSearchTreeWidget, \
     QToolWindowInterface
from gui.pe_table import QParameterExplorationTable
from gui.virtual_cell import QVirtualCellWindow
from gui.pe_pipeline import QMarkPipelineView

################################################################################

class QParameterView(QSearchTreeWindow, QToolWindowInterface):
    """
    QParameterView is a special widget for displaying aliases and
    parameters inside a pipeline
    
    """
    def createTreeWidget(self):
        """ createTreeWidget() -> QModuleTreeWidget
        Return the search tree widget for this window
        
        """
        self.setWindowTitle('Parameters')
        return QParameterTreeWidget(self)

class QParameterTreeWidget(QSearchTreeWidget):
    """
    QParameterTreeWidget is a subclass of QSearchTreeWidget to display all
    Vistrails Module
    
    """
    def __init__(self, parent=None):
        """ QParameterTreeWidget(parent: QWidget) -> QParameterTreeWidget
        Set up size policy and header

        """
        QSearchTreeWidget.__init__(self, parent)
        self.header().hide()
        self.setRootIsDecorated(False)
        self.delegate = QParameterTreeWidgetItemDelegate(self, self)
        self.setItemDelegate(self.delegate)

    def updateFromPipeline(self, pipeline):
        """ updateFromPipeline(pipeline: Pipeline) -> None
        Read the list of aliases and parameters from the pipeline
        
        """
        self.clear()

        # Update the aliases
        if len(pipeline.aliases)>0:
            aliasRoot = QParameterTreeWidgetItem(None, self,
                                                 QtCore.QStringList('Aliases'))
            aliasRoot.setFlags(QtCore.Qt.ItemIsEnabled)
            for (alias, info) in pipeline.aliases.iteritems():
                (aType, mId, fId, pId) = info
                v = pipeline.modules[mId].functions[fId].params[pId].strValue
                label = QtCore.QStringList('%s = %s' % (alias, v))
                aliasItem = QParameterTreeWidgetItem(info, aliasRoot, label)
            aliasRoot.setExpanded(True)
            
        # Now go through all modules and functions
        for mId, module in pipeline.modules.iteritems():
            if len(module.functions)>0:
                label = QtCore.QStringList(module.name)
                moduleItem = QParameterTreeWidgetItem(None, self, label)
                for fId in range(len(module.functions)):
                    function = module.functions[fId]
                    v = ', '.join([p.strValue for p in function.params])
                    label = QtCore.QStringList('%s(%s)' % (function.name, v))
                    mItem = QParameterTreeWidgetItem((mId, fId),
                                                     moduleItem,
                                                     label)
                moduleItem.setExpanded(True)
                    
            
            
class QParameterTreeWidgetItemDelegate(QtGui.QItemDelegate):
    """    
    QParameterTreeWidgetItemDelegate will override the original
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
        if model.parent(index).isValid()==False:
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
                model.data(index,
                           QtCore.Qt.DisplayRole).toString(),
                QtCore.Qt.ElideMiddle, 
                textrect.width())
            style.drawItemText(painter,
                               textrect,
                               QtCore.Qt.AlignLeft,
                               option.palette,
                               self.treeView.isEnabled(),
                               text)
            painter.setPen(QtGui.QPen(QtCore.Qt.black))
            painter.drawLine(textrect.left()-5,
                             textrect.bottom(),
                             textrect.left()+textrect.width(),
                             textrect.bottom())
        else:
            QtGui.QItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        """ sizeHint(option: QStyleOptionViewItem, index: QModelIndex) -> None
        Take into account the size of the top-level button
        
        """
        return (QtGui.QItemDelegate.sizeHint(self, option, index) +
                QtCore.QSize(2, 2))
            

class QParameterTreeWidgetItem(QtGui.QTreeWidgetItem):
    """
    QParameterTreeWidgetItem represents module on QParameterTreeWidget
    
    """
    def __init__(self, info, parent, labelList):
        """ QParameterTreeWidgetItem(parent: QTreeWidgetItem
                                  labelList: QStringList)
                                  -> QParameterTreeWidget
        Create a new tree widget item with a specific parent and
        labels

        """
        self.info = info
        QtGui.QTreeWidgetItem.__init__(self, parent, labelList)
        
