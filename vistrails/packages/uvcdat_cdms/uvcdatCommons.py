###############################################################################
#                                                                             #
# Authors:      PCMDI Software Team                                           #
#               Lawrence Livermore National Laboratory:                       #
#                                                                             #
###############################################################################
from PyQt4 import QtCore, QtGui
import os

debug = True
## Ned to turn that back on if coming from vistraisl
useVistrails = False

blackColor = QtGui.QColor(0,0,0)
redColor = QtGui.QColor(255,0,0)
greenColor = QtGui.QColor(0,255,0)
defaultTemplatesColor = QtGui.QColor(108,198,105)
defaultGmsColor = QtGui.QColor(252,104,63)
defaultTemplatesColor = QtGui.QColor(58,79,108)
defaultGmsColor = QtGui.QColor(179,140,138)

plotTypes = {"VCS":['Boxfill', 'Isofill', 'Isoline', 'Meshfill', 
                     'Scatter', 'Taylordiagram', 'Vector', 'XvsY',
                     'Xyvsy', 'Yxvsx', '3D_Scalar', '3D_Vector', '3D_Dual_Scalar' ],
             }

gmInfos= {'Boxfill' :{'nSlabs':1},
          'Isofill' :{'nSlabs':1},
          'Isoline' :{'nSlabs':1},
          'Meshfill' :{'nSlabs':1},
          'Scatter' : {'nSlabs':2},
          'Taylordiagram' :{'nSlabs':1},
          'Vector' :{'nSlabs':2},
          'XvsY' :{'nSlabs':2},
          'Xyvsy' :{'nSlabs':1},
          'Yxvsx' :{'nSlabs':1},
          '3D_Scalar' :{'nSlabs':1},
          '3D_Dual_Scalar' :{'nSlabs':2},
          '3D_Vector' :{'nSlabs':2},
          }
noMargins = QtCore.QMargins(0,0,0,0)
indentSpacing = 10

class QDropLineEdit(QtGui.QLineEdit):
    def __init__(self,parent=None,types=["test",]):
        QtGui.QLineEdit.__init__(self,parent=parent)
        self.types=types

    def dragEnterEvent(self,event):
        ok = False
        for t in self.types:
            d = event.mimeData().data(t)
            if d.data() != "":
                ok =True
                break
        if ok:
            event.accept()
        else:
            event.ignore()
        
    def dropEvent(self,event):
        event.accept()
        self.setText(event.mimeData().text())
        self.emit(QtCore.SIGNAL("droppedInto"),self)
        
class QDragListWidget(QtGui.QListWidget):
    
    def __init__(self,parent=None,type="test",dropTypes=[]):
        QtGui.QListWidget.__init__(self,parent=parent)
        self.type=type
        self.dropTypes=dropTypes
        if self.dropTypes!=[]:
            self.setAcceptDrops(True)
        self.mouseMoved = False;

    def dragEnterEvent(self,event):
        ok = False
        for t in self.dropTypes:
            d = event.mimeData().data(t)
            if d.data() != "":
                ok =True
                break
        if ok:
            event.accept()
        else:
            event.ignore()
        
    def dragMoveEvent(self,event):
        event.accept()
        
    def dropEvent(self,event):
        #event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()
        #self.setText(event.mimeData().text())
        self.emit(QtCore.SIGNAL("droppedInto"),event)
        
    def mouseMoveEvent(self,e):
        self.mouseMoved = True    
        d =QtGui.QDrag(self)
        m = QtCore.QMimeData()
        a = QtCore.QByteArray()
        if self.currentItem() is None:
            return
        a.append(self.currentItem().text())
        m.setData("%s" % self.type,a)
        m.setText(self.currentItem().text())        
        d.setMimeData(m)
        d.start()
        
    def mousePressEvent(self, e):
        """
        Track mouse moved to prevent item deselection when initiating 
        drag and drop
        """
        self.mouseMoved = False
        QtGui.QListWidget.mousePressEvent(self, e)
        
class QLabeledWidgetContainer(QtGui.QWidget):
    """ Container widget for the 3 main widgets: QVariableView, QCDATFileWidget,
    and QDefinedVariable """

    def __init__(self, widget, label='', parent=None,margins=noMargins,labelAlign = QtCore.Qt.AlignCenter,frameStyle = QtGui.QFrame.Panel | QtGui.QFrame.Raised,labelSizePolicy=None,widgetSizePolicy=None):
        QtGui.QWidget.__init__(self, parent)

        vbox = QtGui.QVBoxLayout()
        #vbox.setMargin(0)
        
        self.label = QtGui.QLabel(label)
        self.label.setAutoFillBackground(False)
        self.label.setAlignment(labelAlign)
        self.label.setFrameStyle(frameStyle)
        if labelSizePolicy is not None:
            self.label.setSizePolicy(labelSizePolicy)
        vbox.addWidget(self.label)

        if widget!=None:
            self.widget = widget
        else:
            self.widget = QtGui.QWidget()
        if widgetSizePolicy is not None:
            self.setSizePolicy(widgetSizePolicy)
            self.widget.setSizePolicy(widgetSizePolicy)
        vbox.addWidget(self.widget, 1)
        vbox.setSpacing(0)
        self.setLayout(vbox)
        self.setContentsMargins(margins)

    def getWidget(self):
        return self.widget

    ## def event(self, e):
    ##     if e.type()==76: #QtCore.QEvent.LayoutRequest:
    ##         self.setMaximumHeight(min(self.label.height()+self.layout().spacing()+
    ##                                   self.widget.maximumHeight(), 16777215))
    ##     return False

        
            
class QRadioButtonFrame(QtGui.QFrame):
    """ Framed widget containing a label and list of radiobuttons """
    def __init__(self, labelText=None, buttonList=None, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Raised)
        self.setFrameShape(QtGui.QFrame.Box)

        self.hbox = QtGui.QHBoxLayout()
        self.setLayout(self.hbox)
        self.buttonGroup = QtGui.QButtonGroup()
        self.buttons = {}

        if labelText is not None:
            self.addLabel(QtGui.QLabel(labelText))
        if buttonList is not None:
            self.addButtonList(buttonList)

    def addLabel(self, label):
        self.hbox.addWidget(label)
        self.label = label

    def addButton(self, button):
        self.buttonGroup.addButton(button)
        self.hbox.addWidget(button)
        self.buttons[str(button.text())] = button

    def setChecked(self, buttonText):
        if buttonText in list(self.buttons):
            self.buttons[buttonText].setChecked(True)

    def isChecked(self, buttonText):
        if buttonText in list(self.buttons):
            return self.buttons[buttonText].isChecked()

        return False

    def getButton(self, buttonText):
        if buttonText in list(self.buttons):
            return self.buttons[buttonText]

        return None

    def addButtonList(self, buttonList):
        """ Create and add buttons from a list of strings """
        for buttonText in buttonList:
            button = QtGui.QRadioButton(buttonText)
            self.buttons[buttonText] = button
            self.addButton(button)

class QFramedWidget(QtGui.QGroupBox):
    def __init__(self, titleText=None, parent=None,margins=noMargins,alignment=QtCore.Qt.AlignLeft,flat=False):
        QtGui.QGroupBox.__init__(self, parent)    
## class QFramedWidget(QtGui.QFrame):
##     def __init__(self, titleText=None, parent=None,margins=noMargins,frameStyle = QtGui.QFrame.Panel | QtGui.QFrame.Raised, frameShape=QtGui.QFrame.Box):
##         QtGui.QFrame.__init__(self, parent)    
##         self.setFrameStyle(frameStyle)
##         self.setFrameShape(frameShape)
        self.setAlignment(alignment)
        self.setContentsMargins(margins)
        self.lineEditList = []
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self.indent = 10
        self.setFlat(flat)
        if titleText is not None:
            ## title = QtGui.QLabel(titleText)
            self.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
            self.setTitle(titleText)
        self.newRow()

    def setSpacing(self, spacing):
        self.vbox.setSpacing(spacing)

    def newRow(self):
        self.hbox = QtGui.QHBoxLayout()
        self.vbox.addLayout(self.hbox)

    def addCheckBox(self, text, indent=True, newRow=True):
        if newRow == True:
            self.newRow()
        if indent == True:
            self.hbox.addSpacing(indentSpacing)

        checkbox = QtGui.QCheckBox(text)
        self.addWidget(checkbox)
        return checkbox

    def addLabeledComboBox(self, text, comboStringList, indent=True, newRow=True):
        if newRow == True:
            self.newRow()
        if indent == True:
            self.hbox.addSpacing(indentSpacing)

        # Init combo box & set text to white on blue
        comboBox = QtGui.QComboBox()
        comboPalette = comboBox.view().palette()
        comboPalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)        
        comboPalette.setColor(QtGui.QPalette.Highlight, QtCore.Qt.blue)
        comboBox.view().setPalette(comboPalette)
        for string in comboStringList:
            comboBox.addItem(string)        
            
        comboBox.label = self.addLabel(text)
        self.addWidget(comboBox)
        return comboBox

    def addLabeledSpinBox(self, text, minValue=None, maxValue=None,
                          indent=True, newRow=True):
        if newRow == True:
            self.newRow()
        if indent == True:
            self.hbox.addSpacing(indentSpacing)

        spinbox = QtGui.QSpinBox()
        if maxValue is not None:
            spinbox.setMaximum(maxValue)
        if minValue is not None:
            spinbox.setMinimum(minValue)
        tmp = QtGui.QLabel(text)
        spinbox.label = tmp
        self.addWidget(tmp)
        self.addWidget(spinbox)
        
        return spinbox

    def addLabeledDoubleSpinBox(self, text, minValue=None, maxValue=None,
                                step=None, indent=True, newRow=True):
        if newRow == True:
            self.newRow()
        if indent == True:
            self.hbox.addSpacing(indentSpacing)

        spinbox = QtGui.QDoubleSpinBox()
        if maxValue is not None:
            spinbox.setMaximum(maxValue)
        if minValue is not None:
            spinbox.setMinimum(minValue)
        if step is not None:
            spinbox.setSingleStep(step)
            
        self.addWidget(QtGui.QLabel(text))
        self.addWidget(spinbox)
        return spinbox    

    def addButton(self, text, newRow=True, buttonType = "Tool",icon=None,iconSize=None):
        import customizeUVCDAT
        if newRow == True:
            self.newRow()
            
        if buttonType == "Tool":
            button = QtGui.QToolButton()
        else:
            button = QtGui.QPushButton()
        button.setText(text)
        if icon is not None:
            button.setIcon(QtGui.QIcon(icon))
            if iconSize is None:
                button.setIconSize(QtCore.QSize(customizeUVCDAT.iconsize, customizeUVCDAT.iconsize))
            else:
                button.setIconSize(QtCore.QSize(iconSize, iconSize))
        self.addWidget(button)
        return button

    def addRadioFrame(self, text, buttonList, newRow=True):
        if newRow == True:
            self.newRow()
            
        buttonGroup = QRadioButtonFrame(text, buttonList)            
        self.addWidget(buttonGroup)
        return buttonGroup

    def clearAllLineEdits(self):
        for lineEdit in self.lineEditList:
            lineEdit.setText('')

    def addLabeledLineEdit(self, text, indent=True, newRow=True, align=None):
        if newRow == True:
            self.newRow()
        if indent == True:
            self.hbox.addSpacing(indentSpacing)
            
        lineEdit = QtGui.QLineEdit()
        self.lineEditList.append(lineEdit)
        tmp = QtGui.QLabel(text)
        lineEdit.label = tmp
        self.addWidget(tmp)
        self.addWidget(lineEdit, align)

        if align is not None:
            self.vbox.setAlignment(self.hbox, align)
        
        return lineEdit

    def addLabelAndLineEdit(self, text, indent=True, newRow=True):
        if newRow == True:
            self.newRow()
        if indent == True:
            self.hbox.addSpacing(indentSpacing)

        lineEdit = QtGui.QLineEdit()
        self.lineEditList.append(lineEdit)
        label = QtGui.QLabel(text)
        
        self.addWidget(label)
        self.addWidget(lineEdit)
        return label, lineEdit        

    def addWidget(self, widget, align=None,newRow=False):
        if newRow == True:
            self.newRow()
        if align is None:
            self.hbox.addWidget(widget)
        else:
            self.hbox.addWidget(widget, alignment=align)

    def addLabel(self, text, newRow=False,align=None):
        if newRow:
            self.newRow()
        label = QtGui.QLabel(text)
        self.addWidget(label,align=align)
        self.label = label
        return label

    def addSlider(self,minimum=None,maximum=None):
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        if minimum is not None:
            slider.setMinimum(minimum)
        if maximum is not None:
            slider.setMaximum(maximum)
        self.addWidget(slider)
        return slider

    def addLabeledSlider(self, text, newRow=True,divider=1,minimum=None,maximum=None):
        if newRow == True:
            self.newRow()
            
        labeledSlider = QLabeledSlider(text,divider=divider,minimum=minimum,maximum=maximum)
        self.addWidget(labeledSlider)
        return labeledSlider.getSlider()
    
class QSimpleMessageBox(QtGui.QMessageBox):

    def __init__(self, text, parent):
        QtGui.QMessageBox.__init__(self, parent)
        self.setText(text)

class QLabeledSlider(QtGui.QWidget):
    def __init__(self, text, parent=None, divider=1,minimum=None,maximum=None):
        QtGui.QWidget.__init__(self, parent)
        vbox = QtGui.QVBoxLayout()
        vbox.setSpacing(10)
        self.setLayout(vbox)
        self.text = text
        self.label = QtGui.QLabel(text)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        if minimum is not None:
            self.slider.setMinimum(minimum)
        if maximum is not None:
            self.slider.setMaximum(maximum)
        self.divider=divider
        
        vbox.addWidget(self.label)
        vbox.addWidget(self.slider)

        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'),
                     self.updateLabel)

    def getSlider(self):
        return self.slider

    def updateLabel(self, value):
        val = float(value)/self.divider
        val = "%.2f" % val
        if val[-2:]=="00":
            val=val[:-3]
        self.label.setText("%s  %s" %(self.text, val))

def round_number( N ):
   import numpy
   P = 10.0 ** ( numpy.floor(numpy.log10(abs(N) ) ) )
   return( sign(N) * int( abs(N)/P + 0.5) * P )

def sign ( N ):
   if (N < 0): return -1
   else: return 1

        
class QCommandsFileWidget(QtGui.QDialog):
    def __init__(self,parent,title,readOnly=True,file=None):
        import customizeUVCDAT
        QtGui.QDialog.__init__(self,parent)
        self.root=parent.root
        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        self.setLayout(layout)
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setIconSize(QtCore.QSize(customizeUVCDAT.iconsize, customizeUVCDAT.iconsize))
        icon = QtGui.QIcon(os.path.join(customizeUVCDAT.ICONPATH, 'floppy_disk_blue.ico'))
        action = self.toolBar.addAction(icon, 'saveas',self.saveAs)
        action.setToolTip('Save to a new file.')
        icon = QtGui.QIcon(os.path.join(customizeUVCDAT.ICONPATH, 'run_copy.ico'))
        action = self.toolBar.addAction(icon, 'exec',self.execute)
        action.setToolTip('Execute commands.')
        self.toolBar.addSeparator()
        layout.addWidget(self.toolBar)

        self.text = QtGui.QTextEdit(self)
        self.text.setReadOnly(readOnly)
        self.text.ensureCursorVisible()
        
        layout.addWidget(self.text)

        self.setWindowTitle(title)

        self.setMinimumWidth(600)

        if file is not None:
            f=open(file)
            self.addText(f.read())
            f.close()
        self.connect(self.text, QtCore.SIGNAL("returnPressed(void)"),
                     self.refresh)
            
    def saveAs(self):
        cont = True
        while cont is True:
            fnm = str(QtGui.QFileDialog.getSaveFileName())
            try:
                f=open(fnm,'w')
                cont=False
            except:
                if fnm is None:
                    cont=False
                    return
        

        print >> f, self.text.toPlainText()
        f.close()

    def addText(self,textString):
        import customizeUVCDAT
        sp = textString.split("\n")
        for l in sp:
            st=l.strip()
            if len(st)>0 and st[0]=="#": # comment
                self.text.setTextColor( customizeUVCDAT.commentsColor )
                dtxt = str(self.text.toPlainText())
                if len(dtxt)>2 and dtxt[-2]!="\n":
                    self.text.insertPlainText('\n')
            else:
                self.text.setTextColor( customizeUVCDAT.defaultTextColor )
            
            self.text.insertPlainText(l+'\n')

    def execute(self):
        txt = self.text.toPlainText()
        for l in txt.split("\n"):
            self.root.tabView.widget(2).le.setText(l)
            self.root.tabView.widget(2).run_command()            

    def refresh(self):
        txt = self.text.toPlainText()
        self.text.clear()
        self.text.addText(txt)

        
def getAvailablePrinters():
    plist = []
    try:
        fn = os.path.join(os.environ['HOME'],'.uvcdat','HARD_COPY')
    except:
        return plist
    try:
        f=open(fn)
    except:
        return plist
    ln = f.readline()
    for ln in f.xreadlines():
        if ln[0] != '#':
            if (ln[0:9] == 'landscape'
                or ln[0:8] == 'portrait'
                or ln[0] == ' ' or ln[0] == '\n'):
                pass
            else:
                plist.append(ln[0:-1])
    f.close( )
    return plist

class CalcButton(QtGui.QToolButton):
    """Calculator button class - size change & emits clicked text signal"""
    def __init__(self, text, icon = None, tip = None, styles={}, parent=None,signal="clickedMyButton",minimumXSize=35,minimumYSize=35):
        QtGui.QToolButton.__init__(self, parent)
        import customizeUVCDAT
        if isinstance(styles,dict):
            st=""
            for k in styles.keys():
                val = styles[k]
                if isinstance(val,QtGui.QColor):
                    val = str(val.name())
                st+="%s:%s; " % (k,val)
            if len(st)>0: self.setStyleSheet(st)
        elif isinstance(styles,str):
            self.setStyleSheet(styles)
            
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        if icon is not None:
            icon = os.path.join(customizeUVCDAT.ICONPATH,icon)
            icon = QtGui.QIcon(icon)
            self.setIcon(icon)
            self.setIconSize(QtCore.QSize(customizeUVCDAT.iconsize,customizeUVCDAT.iconsize))
        self.setText(text)
        self.setMinimumSize(minimumXSize,minimumYSize)
        ## self.setMaximumSize(60, 50)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                             QtGui.QSizePolicy.Preferred))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        if tip is not None:
            self.setToolTip(tip)
            
        self.connect(self, QtCore.SIGNAL('clicked()'), self.clickEvent)
        self.sendSignal = signal
        
    def clickEvent(self):
        """Emits signal with button text"""
        self.emit(QtCore.SIGNAL(self.sendSignal), self)


class CustomFrame(QtGui.QLabel):
    def __init__(self, text, minimumXSize, minimumYSize, signal="clickedMyButton"):
        super(CustomFrame, self).__init__()
        self.setFrameShape(QtGui.QFrame.Panel)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.setText(text)
        self.setIndent(1)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(minimumXSize, minimumYSize)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sendSignal = signal

    def mousePressEvent(self, event):
        self.emit(QtCore.SIGNAL(self.sendSignal), self)

    def flipFrameShadow(self, lineWidth, midLineWidth):
        self.setLineWidth(lineWidth)
        self.setMidLineWidth(midLineWidth)
