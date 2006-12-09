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
                        self.vWidget.addFunction(item.module,
                                                 item.module.getNumFunctions(),
                                                 function)
                        self.scrollContentsBy(0, self.viewport().height())
                        self.lockUpdate()
                        if self.controller:
                            self.controller.previousModuleIds = [self.module.id]
                            self.controller.addMethod(self.module.id, function)
                        self.unlockUpdate()

    def updateModule(self, module):
        """ updateModule(module: Module)) -> None        
        Construct input forms with the list of functions of a module
        
        """
        if self.updateLocked: return
        self.module = module
        self.vWidget.clear()
        if module:
            fId = 0
            for f in module.functions:                
                self.vWidget.addFunction(module.id, fId, f)
                fId += 1

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
        
class QVerticalWidget(QtGui.QWidget):
    """
    QVerticalWidget is a widget holding other function widgets
    vertically
    
    """
    def __init__(self, parent=None):
        """ QVerticalWidget(parent: QWidget) -> QVerticalWidget
        Initialize with a vertical layout
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.formType = QMethodInputForm
        
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

    def clear(self):
        """ clear() -> None
        Clear and delete all widgets in the layout
        
        """
        self.setEnabled(False)
        while True:
            child = self.layout().takeAt(0)
            if child:
                child.widget().deleteLater()
                del child
            else:
                break
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
                                  self.function.params[i].type))
            methodBox.lockUpdate()
            methodBox.controller.previousModuleId = [methodBox.module.id]
            methodBox.controller.replaceFunction(methodBox.module,
                                                 self.fId,
                                                 paramList)
            methodBox.unlockUpdate()

    def updateFunction(self, function):
        """ updateFunction(function: ModuleFunction) -> None
        Auto create widgets to describes the function 'function'
        
        """
        self.setTitle(function.name)
        self.function = function
        self.lineEdits = []        
        for pIndex in range(len(function.params)):
            p = function.params[pIndex]
            label = QHoverAliasLabel(p.alias, p.type)
            lineEdit = QPythonValueLineEdit(p.strValue, p.type, self)            
            self.lineEdits.append(lineEdit)
            self.layout().addWidget(label, pIndex, 0)
            self.layout().addWidget(lineEdit, pIndex, 1)

    def keyPressEvent(self, e):
        """ keyPressEvent(e: QKeyEvent) -> None
        Handle Del/Backspace to delete the input form
        
        """
        if e.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            methodBox = self.parent().parent().parent()
            self.parent().layout().removeWidget(self)
            self.deleteLater()
            for i in range(self.parent().layout().count()):
                self.parent().layout().itemAt(i).widget().fId = i
            methodBox.lockUpdate()
            if methodBox.controller:
                methodBox.controller.previousModuleId = [methodBox.module.id]
                methodBox.controller.deleteMethod(self.fId,
                                                  methodBox.module.id)
            methodBox.unlockUpdate()
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
            if ok and str(text)!=self.alias:
                self.alias = str(text)
                self.updateText()
                self.parent().updateMethod()

class QPythonValueLineEdit(QtGui.QLineEdit):
    """
    QPythonValueLineEdit is a line edit that can be used to edit
    int/float/string contents. It supports expression evaluation as
    well by using a double '$$'
    
    """
    def __init__(self, contents, contentType, parent=None):
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

    def keyPressEvent(self, event):
        """ keyPressEvent(event) -> None        
        If this is a string line edit, we can use Ctrl+Enter to enter
        the file name
        
        """
        k = event.key()
        s = event.modifiers()

        if (k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return):
            if s & QtCore.Qt.ControlModifier:
                if self.contentIsString:
                    fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                                 'Use Filename '
                                                                 'as Value...',
                                                                 self.text(),
                                                                 'All files '
                                                                 '(*.*)')
                    if fileName != None:
                        self.setText(fileName)
                        self.update()
                        self.setFocus(QtCore.Qt.MouseFocusReason)
                        return
            else:
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
        self.updateText()
        if self.parent():
            self.parent().focusOutEvent(event)
            newText = str(self.text())
            if newText!=self.lastText:
                self.parent().updateMethod()
        QtGui.QLineEdit.focusOutEvent(self, event)

    def updateText(self):
        """ updateText() -> None
        Update the text to the result of the evaluation
        
        """
        base = expression.evaluateExpressions(self.text())
        if self.contentIsString:
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)
