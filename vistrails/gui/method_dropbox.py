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
""" This file contains widgets that can be used for dropping
methods. It will construct an input form for that method

QMethodDropBox
QVerticalWidget
QMethodInputForm
QHoverAliasLabel
"""

from PyQt4 import QtCore, QtGui
from core.utils import expression
from core.vistrail.module_function import ModuleFunction
from gui.common_widgets import QPromptWidget
from gui.method_palette import QMethodTreeWidget
from gui.theme import CurrentTheme

################################################################################

class QMethodDropBox(QtGui.QScrollArea):
    """
    QMethodDropBox is just a widget such that method items from
    QMethodPalette can be dropped into its client rect. It then
    construct an input form based on the type of handling widget
    
    """
    def __init__(self, parent=None):
        """ QMethodPalette(parent: QWidget) -> QMethodPalette
        Initialize widget constraints
        
        """
        QtGui.QScrollArea.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.vWidget = QVerticalWidget()
        self.setWidget(self.vWidget)
        self.updateLocked = False
        self.controller = None
        self.module = None

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the method palette
        
        """
        if type(event.source())==QMethodTreeWidget:
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
        else:
            event.ignore()
        
    def dragMoveEvent(self, event):
        """ dragMoveEvent(event: QDragMoveEvent) -> None
        Set to accept drag move event from the method palette
        
        """
        if type(event.source())==QMethodTreeWidget:
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()

    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new method
        
        """
        if type(event.source())==QMethodTreeWidget:
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                for item in data.items:
                    if item.port:
                        function = ModuleFunction.fromSpec(item.port,
                                                           item.spec)
                        # FIXME need to get the position,
                        # but not sure if this is correct
                        function.id = item.module.getNumFunctions()
                        self.vWidget.addFunction(item.module,
                                                 item.module.getNumFunctions(),
                                                 function)
                        self.scrollContentsBy(0, self.viewport().height())
                        self.lockUpdate()
                        if self.controller:
                            self.controller.previousModuleIds = [self.module.id]
                            self.controller.addMethod(self.module.id, function)
                        self.unlockUpdate()
                self.emit(QtCore.SIGNAL("paramsAreaChanged"))

    def updateModule(self, module):
        """ updateModule(module: Module)) -> None        
        Construct input forms with the list of functions of a module
        
        """
        self.module = module
        if self.updateLocked: return
        self.vWidget.clear()
        if module:
            fId = 0
            for f in module.functions:
                self.vWidget.addFunction(module.id, fId, f)
                fId += 1
            self.vWidget.showPromptByChildren()
        else:
            self.vWidget.showPrompt(False)

    def lockUpdate(self):
        """ lockUpdate() -> None
        Do not allow updateModule()
        
        """
        self.updateLocked = True
        
    def unlockUpdate(self):
        """ unlockUpdate() -> None
        Allow updateModule()
        
        """
        self.updateLocked = False

class QVerticalWidget(QPromptWidget):
    """
    QVerticalWidget is a widget holding other function widgets
    vertically
    
    """
    def __init__(self, parent=None):
        """ QVerticalWidget(parent: QWidget) -> QVerticalWidget
        Initialize with a vertical layout
        
        """
        QPromptWidget.__init__(self, parent)
        self.setPromptText("Drag methods here to set parameters")
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.formType = QMethodInputForm
        self.setMinimumHeight(50)
        self._functions = []
        
    def addFunction(self, moduleId, fId, function):
        """ addFunction(moduleId: int, fId: int,
                        function: ModuleFunction) -> None
        Add an input form for the function
        
        """
        inputForm = self.formType(self)
        inputForm.moduleId = moduleId
        inputForm.fId = fId
        inputForm.updateFunction(function)
        self.layout().addWidget(inputForm)
        inputForm.show()
        self.setMinimumHeight(self.layout().minimumSize().height())
        self.showPrompt(False)
        self._functions.append(inputForm)

    def clear(self):
        """ clear() -> None
        Clear and delete all widgets in the layout
        
        """
        self.setEnabled(False)
        for v in self._functions:
            self.layout().removeWidget(v)
            v.deleteLater()
        self._functions = []
        self.setEnabled(True)

class QMethodInputForm(QtGui.QGroupBox):
    """
    QMethodInputForm is a widget with multiple input lines depends on
    the method signature
    
    """
    def __init__(self, parent=None):
        """ QMethodInputForm(parent: QWidget) -> QMethodInputForm
        Initialize with a vertical layout
        
        """
        QtGui.QGroupBox.__init__(self, parent)
        self.setLayout(QtGui.QGridLayout())
        self.layout().setMargin(5)
        self.layout().setSpacing(5)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.palette().setColor(QtGui.QPalette.Window,
                                CurrentTheme.METHOD_SELECT_COLOR)
        self.fId = -1
        self.function = None

    def focusInEvent(self, event):
        """ gotFocus() -> None
        Make sure the form painted as selected
        
        """
        self.setAutoFillBackground(True)

    def focusOutEvent(self, event):
        """ lostFocus() -> None
        Make sure the form painted as non-selected and then
        perform a parameter changes
        
        """
        self.setAutoFillBackground(False)

    def updateMethod(self):
        """ updateMethod() -> None
        Update the method values to vistrail
        
        """
        methodBox = self.parent().parent().parent()
        if methodBox.controller:
            paramList = []
            for i in range(len(self.lineEdits)):
                paramList.append((str(self.lineEdits[i].text()),
                                  self.function.params[i].type,
                                  str(self.labels[i].alias)))
            methodBox.lockUpdate()
            methodBox.controller.previousModuleIds = [methodBox.module.id]
            methodBox.controller.replace_method(methodBox.module,
                                                self.fId,
                                                paramList)
            methodBox.unlockUpdate()

    def checkAlias(self, name):
        """ checkAlias(name: str) -> Boolean
        Returns True if the current pipeline already has the alias name

        """
        methodBox = self.parent().parent().parent()
        if methodBox.controller:
            return methodBox.controller.checkAlias(name)
        return False

    def updateFunction(self, function):
        """ updateFunction(function: ModuleFunction) -> None
        Auto create widgets to describes the function 'function'
        
        """
        self.setTitle(function.name)
        self.function = function
        self.lineEdits = []
        self.labels = []
        for pIndex in range(len(function.params)):
            p = function.params[pIndex]
            label = QHoverAliasLabel(p.alias, p.type)
            lineEdit = QPythonValueLineEdit(p.strValue, p.type, self)            
            self.lineEdits.append(lineEdit)
            self.labels.append(label)
            self.layout().addWidget(label, pIndex, 0)
            self.layout().addWidget(lineEdit, pIndex, 1)
            # Ugly hack to add browse button to SetFileName strings
            if(function.name=='SetFileName'):
                browseButton = QMethodFileChooser(self, lineEdit)
                self.layout().addWidget(browseButton, pIndex, 2)

    def keyPressEvent(self, e):
        """ keyPressEvent(e: QKeyEvent) -> None
        Handle Del/Backspace to delete the input form
        
        """
        if e.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            methodBox = self.parent().parent().parent()
            self.parent().layout().removeWidget(self)
            self.parent()._functions.remove(self)
            self.deleteLater()
            self.parent().showPromptByChildren()
            for i in range(self.parent().layout().count()):
                self.parent().layout().itemAt(i).widget().fId = i
            methodBox.lockUpdate()
            if methodBox.controller:
                methodBox.controller.previousModuleIds = [methodBox.module.id]
                methodBox.controller.deleteMethod(self.fId,
                                                  methodBox.module.id)            
            methodBox.unlockUpdate()
            methodBox.emit(QtCore.SIGNAL("paramsAreaChanged"))
        else:
            QtGui.QGroupBox.keyPressEvent(self, e)

class QHoverAliasLabel(QtGui.QLabel):
    """
    QHoverAliasLabel is a QLabel that supports hover actions similar
    to a hot link
    """
    def __init__(self, alias='', text='', parent=None):
        """ QHoverAliasLabel(alias:str , text: str, parent: QWidget)
                             -> QHoverAliasLabel
        Initialize the label with a text
        
        """
        QtGui.QLabel.__init__(self, parent)
        self.alias = alias
        self.caption = text
        self.updateText()
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setToolTip(alias)
        self.palette().setColor(QtGui.QPalette.WindowText,
                                CurrentTheme.HOVER_DEFAULT_COLOR)

    def updateText(self):
        """ updateText() -> None
        Update the label text to contain the alias name when appropriate
        
        """
        if self.alias!='':
            self.setText(self.alias+': '+self.caption)
        else:
            self.setText(self.caption)

    def event(self, event):
        """ event(event: QEvent) -> Event Result
        Override to handle hover enter and leave events for hot links
        
        """
        if event.type()==QtCore.QEvent.HoverEnter:
            self.palette().setColor(QtGui.QPalette.WindowText,
                                    CurrentTheme.HOVER_SELECT_COLOR)
        if event.type()==QtCore.QEvent.HoverLeave:
            self.palette().setColor(QtGui.QPalette.WindowText,
                                    CurrentTheme.HOVER_DEFAULT_COLOR)
        return QtGui.QLabel.event(self, event)

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None        
        If mouse click on the label, show up a dialog to change/add
        the alias name
        
        """
        if event.button()==QtCore.Qt.LeftButton:
            (text, ok) = QtGui.QInputDialog.getText(self,
                                                    'Set Parameter Alias',
                                                    'Enter the parameter alias',
                                                    QtGui.QLineEdit.Normal,
                                                    self.alias)
            while ok and self.parent().checkAlias(str(text)):
                msg =" This alias is already being used.\
 Please enter a different parameter alias "
                (text, ok) = QtGui.QInputDialog.getText(self,
                                                        'Set Parameter Alias',
                                                        msg,
                                                        QtGui.QLineEdit.Normal,
                                                        text)
            if ok and str(text)!=self.alias:
                if not self.parent().checkAlias(str(text)):
                    self.alias = str(text).strip()
                    self.updateText()
                    self.parent().updateMethod()

                    

class QPythonValueLineEdit(QtGui.QLineEdit):
    """
    QPythonValueLineEdit is a line edit that can be used to edit
    int/float/string contents. It supports expression evaluation as
    well by using a double '$$'
    
    """
    def __init__(self, contents, contentType, parent=None, multiLines=False):
        """ QPythonValueLineEdit(contents: str,
                                 contentType: str,
                                 container: QWidget,
                                 parent: QWidget) -> QPythonValueLineEdit                                 
        Initialize the line edit with its container and
        contents. Content type is limited to 'int', 'float', and
        'string'
        
        """
        QtGui.QLineEdit.__init__(self, contents, parent)
        self.contentType = contentType
        self.contentIsString = contentType=='String'
        self.lastText = ''
        self.multiLines = multiLines
        self.connect(self,
                     QtCore.SIGNAL('returnPressed()'),
                     self.updateParent)                     

    def keyPressEvent(self, event):
        """ keyPressEvent(event) -> None        
        If this is a string line edit, we can use Ctrl+Enter to enter
        the file name
        
        """
        k = event.key()
        s = event.modifiers()
        if (k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return):
            if s & QtCore.Qt.ShiftModifier:
                event.accept()
                if self.contentIsString and not self.multiLines:
                    fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                                 'Use Filename '
                                                                 'as Value...',
                                                                 self.text(),
                                                                 'All files '
                                                                 '(*.*)')
                    if not fileName.isEmpty():
                        self.setText(fileName)
                        self.updateParent()
                        

                if self.contentIsString and self.multiLines:
                    fileNames = QtGui.QFileDialog.getOpenFileNames(self,
                                                                 'Use Filename '
                                                                 'as Value...',
                                                                 self.text(),
                                                                 'All files '
                                                                 '(*.*)')
                    fileName = fileNames.join(',')
                    if not fileName.isEmpty():
                        self.setText(fileName)
                        self.updateParent()
                        return
                
            else:
                event.accept()
                self.updateText()
        QtGui.QLineEdit.keyPressEvent(self,event)

    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent
        
        """
        self.lastText = str(self.text())
        if self.parent():
            self.parent().focusInEvent(event)
        QtGui.QLineEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        """ focusOutEvent(event: QEvent) -> None
        Update when finishing editing, then pass the event to the parent
        
        """
        self.updateParent()
        if self.parent():
            self.parent().focusOutEvent(event)
        QtGui.QLineEdit.focusOutEvent(self, event)

    def updateParent(self):
        """ updateParent() -> None
        Update parent parameters info if necessary
        
        """
        self.updateText()
        if self.parent():
            newText = str(self.text())
            if newText!=self.lastText:
                self.parent().updateMethod()

    def updateText(self):
        """ updateText() -> None
        Update the text to the result of the evaluation
        
        """
        base = expression.evaluate_expressions(self.text())
        if self.contentIsString:
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)

class QMethodFileChooser(QtGui.QToolButton):
    """ 
    QMethodFileChooser is a toolbar button that opens a browser for
    files.  The lineEdit is updated with the filename that is
    selected.  

    """
    def __init__(self, parent=None, lineEdit=None):
        """
        QMethodFileChooser(parent: QWidget, lineEdit: QPythonValueEdit) -> None

        """
        QtGui.QToolButton.__init__(self, parent)
        self.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DirOpenIcon)))
        self.setIconSize(QtCore.QSize(12,12))
        self.setToolTip('Open a file chooser')
        self.setAutoRaise(True)
        self.lineEdit = lineEdit
        self.connect(self,
                     QtCore.SIGNAL('clicked()'),
                     self.openChooser)
             

    def openChooser(self):
        """
        openChooser() -> None
        
        """
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Use Filename '
                                                     'as Value...',
                                                     self.text(),
                                                     'All files '
                                                     '(*.*)')
        if self.lineEdit and not fileName.isEmpty():
            self.lineEdit.setText(fileName)
            self.lineEdit.updateParent()
