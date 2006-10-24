from PyQt4 import QtCore, QtGui, QtOpenGL
from common import withIndex
from debug import DebugPrint, notify
import system
import macroicons_rc

################################################################################
class QPythonValueLineEdit(QtGui.QLineEdit):
    # contentType is 'int', 'float', 'string'
    def __init__(self, contents, groupBox, contentType, parent=None):
        QtGui.QLineEdit.__init__(self, contents, parent)
        self.groupBox = groupBox
        self.contentIsString = contentType=='string'

    def keyPressEvent(self, event):
        k = event.key()
        s = event.modifiers()

        if (k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return):
            if s & QtCore.Qt.ControlModifier:
                if self.contentIsString:
                    fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                                 "Use Filename as Value...",
                                                                 self.text(),
                                                                 "All files (*.*)")
                    if fileName != None:
                        self.setText(fileName)
                        self.update()
                        self.setFocus(QtCore.Qt.MouseFocusReason)
                        return
            else:
                self.updateText()
        QtGui.QLineEdit.keyPressEvent(self,event)

    def focusInEvent(self, event):
        self.groupBox.gotFocus()
        QtGui.QLineEdit.focusInEvent(self,event)

    def focusOutEvent(self, event):
        self.updateText()
        self.groupBox.lostFocus()
        QtGui.QLineEdit.focusOutEvent(self,event)

    def updateText(self):
        base = QPythonValueLineEdit.evaluateExpressions(self.text())
        if self.contentIsString:
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)

    @staticmethod
    def evaluateExpressions(expressions):
        (base, exps) = QPythonValueLineEdit.parseExpression(str(expressions))
        for e in exps:
            try:                        
                base = base[:e[0]] + str(eval(e[1],None,None)) + base[e[0]:]
            except:
                base = base[:e[0]] + '$' + e[1] + '$' + base[e[0]:]
        return base

    @staticmethod
    def parseExpression(expression):
        '''output = (simplified string, [(pos:exp),(pos:exp),...]
        simplified string: the string without any "$exp$". All $$ will
        be replace by a single $.
        (pos:exp): the expression to be computed and where it should be
                   inserted back to the simplified string, starting from
                   the end of the string.
        '''
        import re
        output = expression
        result = []
        p = re.compile(r'\$[^$]+\$')
        e = p.finditer(output)
        if e:
            offset = 0
            for s in e:
                exp = s.group()
                result.append((s.span()[0]-offset, exp[1:len(exp)-1]))
                offset += s.span()[1]-s.span()[0]
            result.reverse()
            output = p.sub('', output)
            output.replace('$$','$')
        return (output, result)

################################################################################

class QValueLineEdit(QtGui.QLineEdit):
    def __init__(self, contents, groupBox, parent=None):
        QtGui.QLineEdit.__init__(self, contents, parent)
        self.groupBox = groupBox

    def keyPressEvent(self, event):
        k = event.key()
        s = event.modifiers()

        if (k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return) and s & QtCore.Qt.ControlModifier:
            fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                         "Use Filename as Value...",
                                                         system.vistrailsDirectory(),
                                                         "All files (*.*)")
            if fileName != None:
                self.setText(fileName)
                self.update()
                self.setFocus(QtCore.Qt.MouseFocusReason)
                return
        QtGui.QLineEdit.keyPressEvent(self,event)

    def focusInEvent(self, event):
        self.groupBox.gotFocus()
        QtGui.QLineEdit.focusInEvent(self,event)

    def focusOutEvent(self, event):
        self.groupBox.lostFocus()
        QtGui.QLineEdit.focusOutEvent(self,event)
    
################################################################################

class QValuesLineEdit(QtGui.QLineEdit):
    """ Same as above, but allowing multiple files to be selected """
    def __init__(self, contents, groupBox, parent=None):
        QtGui.QLineEdit.__init__(self, contents, parent)
        self.groupBox = groupBox

    def keyPressEvent(self, event):
        k = event.key()
        s = event.modifiers()

        if (k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return) and s & QtCore.Qt.ControlModifier:
            fileNames = QtGui.QFileDialog.getOpenFileNames(self,
                                                         "Use Filenames as Values...",
                                                         system.vistrailsDirectory(),
                                                         "All files (*.*)")
            if not fileNames.isEmpty():
                self.setText(QtCore.QString("%1").arg(fileNames.join(",")))
                self.update()
                self.setFocus(QtCore.Qt.MouseFocusReason)
                return
        QtGui.QLineEdit.keyPressEvent(self,event)

    def focusInEvent(self, event):
        self.groupBox.gotFocus()
        QtGui.QLineEdit.focusInEvent(self,event)

    def focusOutEvent(self, event):
        self.groupBox.lostFocus()
        QtGui.QLineEdit.focusOutEvent(self,event)
    
################################################################################

class QClickableGroupBox(QtGui.QGroupBox):
    def __init__(self, caption, parent=None):
        QtGui.QGroupBox.__init__(self, caption, parent)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.frame = QtGui.QFrame(self)
        self.layout().addWidget(self.frame)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        sp = QtGui.QSizePolicy()
        sp.setHorizontalPolicy(QtGui.QSizePolicy.MinimumExpanding)
        sp.setVerticalPolicy(QtGui.QSizePolicy.MinimumExpanding)
        self.frame.setSizePolicy(sp)
        layout = QtGui.QGridLayout(self.frame)
        layout.setSpacing(2)
        layout.setMargin(2)
        self.frame.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]:
            self.emit(QtCore.SIGNAL("deleteMe"), self)
        else:
            event.ignore()

    def gotFocus(self):
        self.frame.setFrameShape(QtGui.QFrame.Panel)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)

    def lostFocus(self):
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)

    def focusInEvent(self, event):
        self.gotFocus()

    def focusOutEvent(self, event):
        self.lostFocus()

################################################################################

class QHoverParamLabel(QtGui.QLabel):
    def __init__(self, param, parent=None):
        self.param = param
        self.paramAlias = param.alias
        QtGui.QLabel.__init__(self, parent)
        self.updateText()
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.palette().setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        self.setToolTip(param.name)

    def updateText(self):
        if self.paramAlias:
            self.setText(self.paramAlias+': '+self.param.type)
        else:
            self.setText(self.param.type)

    def event(self, event):
        if event.type()==QtCore.QEvent.HoverEnter:
            self.palette().setColor(QtGui.QPalette.WindowText, QtCore.Qt.blue)
        if event.type()==QtCore.QEvent.HoverLeave:
            self.palette().setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        return QtGui.QLabel.event(self, event)

    def mousePressEvent(self, event):
        if event.button()==QtCore.Qt.LeftButton:
            (text, ok) = QtGui.QInputDialog.getText(self,
                                                    'Set Parameter Alias',
                                                    'Enter the parameter alias',
                                                    QtGui.QLineEdit.Normal,
                                                    self.paramAlias)
            if ok:
                self.paramAlias = str(text)
                self.updateText()

################################################################################

class QModuleFunctionGroupBox(QClickableGroupBox):
    def __init__(self, function, functionId, caption,
                 parent=None,
                 configureWidgetType=None,
                 paramList=None):
        QClickableGroupBox.__init__(self, caption, parent)
        self.function = function
        self.functionId = functionId
        self.fields = []
        self.aliases = []
        self.configureWidgetType = configureWidgetType
        self.createWidget(paramList)

    def parameterCount(self):
        return self.function.getNumParams()

    def value(self, paramId):
        return self.fields[paramId].text()

    def oldAlias(self, paramId):
        return self.function.params[paramId].alias

    def name(self, paramId):
        return self.function.params[paramId].name

    def alias(self, paramId):
        return self.aliases[paramId].paramAlias

    def type(self, paramId):
        return self.function.params[paramId].type

    def functionName(self):
        return self.function.name

    def apply(self, result):
        self.emit(QtCore.SIGNAL('applyConfiguration'), (self.function.name,result))
        
    def provideValueChanges(self):
        if self.configureWidgetType:
            self.apply(self.configureWidget.getParams())
        else:
            for i in range(len(self.function.params)):
                if self.value(i) != self.function.params[i].strValue or self.alias(i) != self.oldAlias(i):
                    self.emit(QtCore.SIGNAL("valuesHaveChanged(int)"),self.functionId)
                    return
              
    def createWidget(self, paramList=None):
        theLayout = self.frame.layout()
        if self.configureWidgetType:
            self.configureWidget = self.configureWidgetType(paramList)
            theLayout.addWidget(self.configureWidget, 0, 0)
            self.configureWidget.show()
            self.connect(self.configureWidget,
                         QtCore.SIGNAL('applyConfiguration'),
                         self.apply)
        else:
            for i,p in withIndex(self.function.params):
                lbl = QHoverParamLabel(p, self.frame)
                self.aliases.append(lbl)
                theLayout.addWidget(lbl, i, 0)
                valueEdit = QPythonValueLineEdit(QtCore.QString(p.strValue), self, str(p.type), self.frame)
                theLayout.addWidget(valueEdit, i, 1)
                self.fields.append(valueEdit)
                valueEdit.show()
        self.update()

    def lostFocus(self):
        self.provideValueChanges()
        QClickableGroupBox.lostFocus(self)

################################################################################

class QManyLineEdits(QtGui.QFrame):

    def __init__(self, row, count, groupBox, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setObjectName('ManyLineEdits')
        layout = QtGui.QVBoxLayout()
        self.groupBox = groupBox
        self.setLayout(layout)
        self.frame = self # hack to make qvaluelineedit happy
        self.lineEdits = []
        self.row = row
        self.setLineEdits(count)

    def makeLineEdit(self):
        result = QValuesLineEdit('', self.groupBox, self)
        self.layout().addWidget(result)
        return result

    def setLineEdits(self, count):
        self.setUpdatesEnabled(False)
        self.count = count
        oldvalues = []        
        for e in self.lineEdits:
            oldvalues.append(e.text())
            self.layout().removeWidget(e)
            e.deleteLater()
            del e
        self.lineEdits = [self.makeLineEdit() for c in range(count)]
        if self.count:
            sf = self.count
        else:
            sf = 1
        self.parent().layout().setRowStretch(self.row, sf)
        for e, v in zip(self.lineEdits, oldvalues):
            e.setText(v)
        self.setUpdatesEnabled(True)
        self.parent().adjustSize()
        self.parent().parent().parent().layout().invalidate()
        self.parent().parent().parent().validateLayout()

    def newSizeAsString(self, strCount):
        try:
            newCount = int(strCount)
        except ValueError:
            return
        self.setLineEdits(newCount)


################################################################################

class QRangeString(QtGui.QFrame):

    def __init__(self, row, groupBox, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setObjectName('RangeString')
        layout = QtGui.QVBoxLayout()
        self.groupBox = groupBox
        self.setLayout(layout)
        self.frame = self # hack to make qvaluelineedit happy
        self.strings = []
        self.row = row
        self.setLineEdits()

    
    def setLineEdits(self):
        self.setUpdatesEnabled(False)
        #oldvalues = []        
        #for e in self.lineEdits:
        #    oldvalues.append(e.text())
        #    self.layout().removeWidget(e)
        #    e.deleteLater()
        #    del e
        #self.lineEdits = [self.makeLineEdit() for c in range(count)]
        hl = QtGui.QHBoxLayout()
        
        self.lineEdit = QValuesLineEdit('', self.groupBox, self)
        hl.addWidget(self.lineEdit)
        self.addBtn = QtGui.QToolButton()
        self.addBtn.setToolTip(self.tr("Add string"))
        self.addBtn.setIcon(QtGui.QIcon(":/images/edit_add.png"))
        self.addBtn.setIconSize(QtCore.QSize(16,16))
        self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.addString)
        hl.addWidget(self.addBtn)
        hl.setSpacing(0)
        hl.setMargin(0)
        self.layout().addLayout(hl)
        self.layout().setSpacing(0)
        self.layout().setMargin(0)
        
        self.listWidget = MyStringsWidget(self.groupBox)        
        vl = QtGui.QVBoxLayout()
        vl.setSpacing(0)
        vl.setMargin(0)

        self.upBtn = QtGui.QToolButton()
        self.upBtn.setToolTip(self.tr("Move up"))
        self.upBtn.setIcon(QtGui.QIcon(":/images/up.png"))
        self.upBtn.setIconSize(QtCore.QSize(16,16))
        self.connect(self.upBtn, QtCore.SIGNAL("clicked()"), self.moveUp)
        vl.addWidget(self.upBtn)

        self.downBtn = QtGui.QToolButton()
        self.downBtn.setToolTip(self.tr("Move down"))
        self.downBtn.setIcon(QtGui.QIcon(":/images/down.png"))
        self.downBtn.setIconSize(QtCore.QSize(16,16))
        self.connect(self.downBtn, QtCore.SIGNAL("clicked()"), self.moveDown)
        vl.addWidget(self.downBtn)

        hl2 = QtGui.QHBoxLayout()
        hl2.setSpacing(0)
        hl2.setMargin(0)
        hl2.addWidget(self.listWidget)
        hl2.addLayout(vl)
        self.parent().layout().addLayout(hl2,self.row + 1, 1, 1, 2)
        
        
        #for e, v in zip(self.lineEdits, oldvalues):
        #    e.setText(v)
        self.setUpdatesEnabled(True)
        self.parent().adjustSize()
        self.parent().parent().parent().layout().invalidate()
        self.parent().parent().parent().validateLayout()

    def addString(self):
        if not self.lineEdit.text().isEmpty():
            slist = self.lineEdit.text().split(",",QtCore.QString.SkipEmptyParts)
            self.listWidget.addText(slist)

    def moveUp(self):
        row = self.listWidget.currentRow()
        if row > 0:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row-1,item)
            self.listWidget.setCurrentRow(row-1)

    def moveDown(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count()-1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row+1,item)
            self.listWidget.setCurrentRow(row+1)

    def newSizeAsString(self, strCount):
        try:
            newCount = int(strCount)
        except ValueError:
            return
        self.setLineEdits(newCount)


################################################################################

class MyStringsWidget(QtGui.QListWidget):

    def __init__(self,parent=None):
        QtGui.QListWidget.__init__(self,parent)
        

    def keyPressEvent(self, event):
        k = event.key()
        s = event.modifiers()
        if (k == QtCore.Qt.Key_Delete or k == QtCore.Qt.Key_Backspace) and s == QtCore.Qt.NoModifier:
            if self.currentRow() >= 0:
                self.takeItem(self.currentRow())
                self.updateCount()
        elif (k == QtCore.Qt.Key_Delete or k == QtCore.Qt.Key_Backspace) and s & QtCore.Qt.ControlModifier:
            self.clear()
            self.updateCount()
        else:
            QtGui.QListWidget.keyPressEvent(self,event)

    def sizeHint(self):
        #Return an invalid sizeHint
        return QtCore.QSize()

    def addText(self,slist):
        self.addItems(slist)
        self.updateCount()

    def updateCount(self):
        self.emit(QtCore.SIGNAL("changed(int)"),self.count())
    
        
################################################################################

class QRangeFunctionGroupBox(QClickableGroupBox):
    def __init__(self, function, selectedModule, caption, parent=None):
        QClickableGroupBox.__init__(self, caption, parent)
        self.function = function
        self.selectedModule = selectedModule
        self.fields = []
        self.createWidget()
  
    def parameterCount(self):
        return self.function.getNumParams()

    def type(self, paramId):
        return self.function.params[paramId].type

    def functionName(self):
        return self.function.name

    def stepCount(self):
        return self.parent().parent().parent().parent().sizeEdit.value()

    def updateStepCount(self, count):
        display = str(count)
        stepCount = self.stepCount()
        if count>stepCount:
            display = display + ' (Too many values)'
        if count<stepCount:
            display = display + ' (Need more values)'        
        self.el.setText(display)

    def createWidget(self):
        flayout = self.frame.layout()
        self.elLabel = QtGui.QLabel("Count")
        flayout.addWidget(self.elLabel,0,0)
        self.el = QtGui.QLineEdit(str(self.stepCount),self.frame)
        self.el.setEnabled(False)
        flayout.addWidget(self.el,0,1)
        self.lStart = QtGui.QLabel("Start",self.frame)
        flayout.addWidget(self.lStart,1,1)
        self.lEnd = QtGui.QLabel("End",self.frame)
        flayout.addWidget(self.lEnd,1,2)

        row = 2
        for p in self.function.params:
            self.createField(p, row)
            row += 1
        self.update()

    def createField(self, p, row):
        def dorange(Validator):
            self.lStart.setVisible(True)
            self.lEnd.setVisible(True)
            self.elLabel.setVisible(False)
            self.el.setVisible(False)

            valueEdit1 = QValueLineEdit(QtCore.QString(p.strValue), self, self.frame)
            flayout.addWidget(valueEdit1, row, 1)
            valueEdit2 = QValueLineEdit(QtCore.QString(p.strValue), self, self.frame)
            flayout.addWidget(valueEdit2, row, 2)
            self.fields.append((p.type,valueEdit1,valueEdit2))
            if Validator:
                valueEdit1.setValidator(Validator(self))
                valueEdit2.setValidator(Validator(self))

        def dolist(dummy):
           self.lStart.setVisible(False)
           self.lEnd.setVisible(False)
           self.elLabel.setVisible(True)
           self.el.setVisible(True)
           self.el.setText(str(0))
           wgt = QRangeString(row, self, self.frame)
           flayout.addWidget(wgt, row, 1, 1, 2)
           self.fields.append((p.type,wgt.listWidget))
           self.connect(wgt.listWidget,QtCore.SIGNAL("changed(int)"),self.updateStepCount)
           #self.connect(self.el, QtCore.SIGNAL("textEdited(QString)"), wgt.newSizeAsString)
           self.updateStepCount(wgt.listWidget.count())
        doit = {'Integer': [dorange,QtGui.QIntValidator],
                'Float': [dorange,QtGui.QDoubleValidator],
                'String': [dolist, None]}
        flayout = self.frame.layout()
        lbl = QtGui.QLabel(QtCore.QString(p.type),self.frame)
        flayout.addWidget(lbl, row, 0)
        doit[p.type][0](doit[p.type][1])
            
    
################################################################################
