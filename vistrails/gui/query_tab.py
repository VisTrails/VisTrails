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
""" The file describes the query tab widget to apply a query/filter to
the current pipeline/version view

QQueryTab
"""

from PyQt4 import QtCore, QtGui
from core.vistrail.vistrail import Vistrail
from gui.pipeline_tab import QPipelineTab
from gui.theme import CurrentTheme
from gui.vistrail_controller import VistrailController
from gui.method_dropbox import QMethodInputForm, QPythonValueLineEdit

################################################################################

class QQueryTab(QPipelineTab):
    """
    QQuery is the similar to the pipeline tab where we can interact
    with pipeline. However, no modules properties is accessibled. Just
    connections. Then we can apply this pipeline to be a query on both
    version and pipeline view
    
    """
    def __init__(self, parent=None):
        """ QQueryTab(parent: QWidget) -> QQueryTab
        Create an empty vistrail controller for this query tab
        
        """
        QPipelineTab.__init__(self, parent)
        self.pipelineView.setBackgroundBrush(
            CurrentTheme.QUERY_BACKGROUND_BRUSH)

        self.moduleMethods.vWidget.formType = QFunctionQueryForm
        
        controller = VistrailController()
        controller.setVistrail(Vistrail(), 'Query Vistrail')
        self.setController(controller)
        controller.changeSelectedVersion(0)
        self.connect(controller,
                     QtCore.SIGNAL('vistrailChanged()'),
                     self.vistrailChanged)

    def vistrailChanged(self):
        """ vistrailChanged() -> None
        Update the pipeline when the vistrail version has changed
        
        """
        self.updatePipeline(self.controller.currentPipeline)
        self.emit(QtCore.SIGNAL("queryPipelineChange"),
                  len(self.controller.currentPipeline.modules)>0)
        
################################################################################

class QFunctionQueryForm(QMethodInputForm):
    def __init__(self, parent=None):
        """ QFunctionQueryForm(parent: QWidget) -> QFunctionQueryForm
        Intialize the widget
        
        """
        QMethodInputForm.__init__(self, parent)
        self.function = None
        self.fields = []

    def updateFunction(self, function):
        """ updateFunction(function: ModuleFunction) -> None
        Auto create widgets to describes the function 'function'
        
        """
        self.function = function
        self.setTitle(function.name)
        gLayout = self.layout()
        for pIdx in range(len(function.params)):
            p = function.params[pIdx]
            field = QParameterQuery(p.strValue, p.type, p.queryMethod)
            self.fields.append(field)
            gLayout.addWidget(field, pIdx, 0)
        self.update()

    def updateMethod(self):
        """ updateMethod() -> None        
        Update the method values to vistrail. We only keep a monotonic
        version tree of the query pipeline, we can skip the actions
        here.
        
        """
        methodBox = self.parent().parent().parent()
        if methodBox.controller:
            paramList = []
            pipeline = methodBox.controller.currentPipeline
            f = pipeline.modules[methodBox.module.id].functions[self.fId]
            p = f.params
            for i in range(len(self.fields)):
                p[i].strValue = str(self.fields[i].editor.text())
                p[i].queryMethod = self.fields[i].selector.getCurrentMethod()

        # Go upstream to update the pipeline
        qtab = self
        while type(qtab)!=QQueryTab and qtab!=None:
            qtab = qtab.parent()
        if qtab:
            qtab.vistrailChanged()
            
################################################################################

class QParameterQuery(QtGui.QWidget):
    """
    QParameterQuery is a widget containing a line edit and a drop down
    menu allowing users to choose how they want to query a parameter
    
    """
    def __init__(self, pValue, pType, pMethod, parent=None):
        """ QParameterQuery(pValue: str, pType: str, parent: QWidget,
                            pMethod: int) -> QParameterQuery
        Construct the widget layout
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.value = pValue
        self.type = pType
        
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setLayout(layout)
        
        self.label = QtGui.QLabel('')
        layout.addWidget(self.label)
        
        self.selector = QParameterQuerySelector(pType)
        layout.addWidget(self.selector)        

        self.editor = QPythonValueLineEdit(pValue, pType)
        layout.addWidget(self.editor)

        self.connect(self.selector.operationActionGroup,
                     QtCore.SIGNAL('triggered(QAction*)'),
                     self.operationChanged)
        if pType=='String':            
            self.connect(self.selector.caseActionGroup,
                         QtCore.SIGNAL('triggered(QAction*)'),
                         self.caseChanged)
        self.selector.initAction(pMethod)

    def operationChanged(self, action):
        """ operationChanged(action: QAction) -> None
        Update the text to reflect the operation being used
        
        """
        self.label.setText(action.text())
        self.updateMethod()
        
    def caseChanged(self, action):
        """ caseChanged(action: QAction) -> None
        Update the text to reflect the case sensitivity being used
        
        """
        self.updateMethod()
        
    def updateMethod(self):
        """ updateMethod() -> None        
        Update the method values to vistrail. We only keep a monotonic
        version tree of the query pipeline, we can skip the actions
        here.
        
        """
        if self.parent():
            self.parent().updateMethod()
        
################################################################################

class QParameterQuerySelector(QtGui.QToolButton):
    """
    QParameterEditorSelector is a button with a down arrow allowing
    users to select which type of interpolator he/she wants to use
    
    """
    def __init__(self, pType, parent=None):
        """ QParameterEditorSelector(pType: str, parent: QWidget)
                                     -> QParameterEditorSelector
        Put a stacked widget and a popup button
        
        """
        QtGui.QToolButton.__init__(self, parent)
        self.type = pType
        self.setAutoRaise(True)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        menu = QtGui.QMenu(self)

        self.setPopupMode(QtGui.QToolButton.InstantPopup)        
        
        if pType=='String':
            self.setText(QtCore.QString(QtCore.QChar(0x25bc))) # Down triangle
            self.operationActionGroup = QtGui.QActionGroup(self)                    
            self.containAction = self.operationActionGroup.addAction('Contain')
            self.containAction.setCheckable(True)

            self.exactAction = self.operationActionGroup.addAction('Exact')
            self.exactAction.setCheckable(True)
            
            self.regAction = self.operationActionGroup.addAction('Reg Exp')
            self.regAction.setCheckable(True)
            menu.addActions(self.operationActionGroup.actions())
            menu.addSeparator()
            
            self.caseActionGroup = QtGui.QActionGroup(self)
            self.sensitiveAction = self.caseActionGroup.addAction(
                'Case Sensitive')
            self.sensitiveAction.setCheckable(True)
            
            self.insensitiveAction = self.caseActionGroup.addAction(
                'Case Insensitive')
            self.insensitiveAction.setCheckable(True)
            menu.addActions(self.caseActionGroup.actions())
            
        else:
            self.setText('') # Down triangle
            self.operationActionGroup = QtGui.QActionGroup(self)                    
            self.expAction = self.operationActionGroup.addAction('Expression')
            self.expAction.setCheckable(True)
            self.setEnabled(False)
            
        self.setMenu(menu)

    def initAction(self, pMethod):
        """ initAction(pMethod: int) -> None
        Select the first choice of selector based on self.type
        
        """
        if self.type=='String':
            opMap = {0: self.containAction,
                     1: self.exactAction,
                     2: self.regAction}
            caseMap = {0: self.insensitiveAction,
                       1: self.sensitiveAction}
            if pMethod>5:
                pMethod = 0
            opMap[pMethod/2].trigger()
            caseMap[pMethod%2].trigger()
        else:
            self.expAction.trigger()

    def getCurrentMethod(self):
        """ getCurrentMethod() -> int
        Get the current method based on the popup selection

        """
        if self.type=='String':
            opMap = {self.containAction: 0,
                     self.exactAction: 1,
                     self.regAction: 2}
            caseMap = {self.insensitiveAction: 0,
                       self.sensitiveAction: 1}
            method = (opMap[self.operationActionGroup.checkedAction()]*2 +
                      caseMap[self.caseActionGroup.checkedAction()])
            return method
        else:
            return 0
