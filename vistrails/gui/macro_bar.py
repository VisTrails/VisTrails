from PyQt4 import QtCore, QtGui
from core.enum import enum
from core.vis_macro import ExternalModuleNotSet, InvalidActionFound

##################################################################

class QMacroBar(QtGui.QWidget):
    def __init__(self, builder, parent=None, controller=None):
        QtGui.QDialog.__init__(self,parent)
        self.builder = builder
        self.controller = controller
        self.createWidgets()

        self.connect(builder,
                     QtCore.SIGNAL("controllerChanged"),
                     self.changeController)
        if self.controller:
            self.connect(self.macroDetails, QtCore.SIGNAL("actedOnMacro"),
                         self.controller.macroChanged)
            self.connect(self,QtCore.SIGNAL("recordMacroNow"),
                     self.controller.recordMacro)
            self.connect(self.controller, QtCore.SIGNAL("updateMacro"),
                         self.macroDetails.updateMacro)

    def createWidgets(self):
        self.newMacroBtn = QtGui.QToolButton()
        self.newMacroBtn.setToolTip(self.tr("Create a new macro"))
        self.newMacroBtn.setIcon(QtGui.QIcon(":/images/macro_new.png"))
        self.newMacroBtn.setIconSize(QtCore.QSize(26,26))
        self.connect(self.newMacroBtn, QtCore.SIGNAL("clicked()"), self.newMacro)

        self.recMacroBtn = QtGui.QToolButton()
        self.recMacroBtn.setCheckable(True)
        self.recMacroBtn.setChecked(False)
        self.recMacroBtn.setToolTip(self.tr("Starting recording a macro"))
        self.recMacroBtn.setIcon(QtGui.QIcon(":/images/macro.png"))
        self.recMacroBtn.setIconSize(QtCore.QSize(26,26))
        self.connect(self.recMacroBtn, QtCore.SIGNAL("toggled(bool)"),
                     self.recordMacro)
        self.recMacroBtn.setVisible(False)

        self.viewMacroBtn = QtGui.QToolButton()
        self.viewMacroBtn.setToolTip(self.tr("Show available macros"))
        self.viewMacroBtn.setIcon(QtGui.QIcon(":/images/macro_view.png"))
        self.viewMacroBtn.setIconSize(QtCore.QSize(26,26))
        self.connect(self.viewMacroBtn, QtCore.SIGNAL("clicked()"),
                     self.viewMacros)

        self.infoMacroBtn = QtGui.QToolButton()
        self.infoMacroBtn.setToolTip(self.tr("Show macro actions"))
        self.infoMacroBtn.setIcon(QtGui.QIcon(":/images/macro_info.png"))
        self.infoMacroBtn.setIconSize(QtCore.QSize(26,26))
        self.connect(self.infoMacroBtn, QtCore.SIGNAL("clicked()"),
                     self.showMacroInfo)
        self.infoMacroBtn.setVisible(False)

        self.applyMacroBtn = QtGui.QToolButton()
        self.applyMacroBtn.setToolTip(self.tr("Apply Macro"))
        self.applyMacroBtn.setIcon(QtGui.QIcon(":/images/macro_play.png"))
        self.applyMacroBtn.setIconSize(QtCore.QSize(26,26))
        self.connect(self.applyMacroBtn, QtCore.SIGNAL("clicked()"),
                     self.applyMacro)
        self.applyMacroBtn.setVisible(False)
        
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        buttonslayout = QtGui.QHBoxLayout()
        buttonslayout.setSpacing(0)
        buttonslayout.setMargin(0)
        buttonslayout.addWidget(self.newMacroBtn,0,QtCore.Qt.AlignLeft)
        buttonslayout.addWidget(self.recMacroBtn,0,QtCore.Qt.AlignLeft)
        buttonslayout.addWidget(self.viewMacroBtn,0,QtCore.Qt.AlignLeft)
        buttonslayout.addWidget(self.infoMacroBtn,0,QtCore.Qt.AlignLeft)
        buttonslayout.addWidget(self.applyMacroBtn,0,QtCore.Qt.AlignLeft)
        buttonslayout.addStretch(1)

        self.macrosList = QMacrosList()
        self.connect(self.macrosList.list, QtCore.SIGNAL("currentTextChanged(QString)"),
                     self.macroChanged)
        self.connect(self.macrosList, QtCore.SIGNAL("macroUnselected"),
                     self.macroUnselected)
        
        self.macroDetails = QMacroDetails()
        self.connect(self.macroDetails, QtCore.SIGNAL("macroNameChanged"),
                     self.macroNameDefined)

        self.connect(self.builder, QtCore.SIGNAL("moduleSelected(int)"),
                     self.macroDetails.setComponent)
        
        self.connect(self.builder, QtCore.SIGNAL("connectionSelected(int)"),
                     self.macroDetails.setConnection)
                        
        self.stackedWidget = QtGui.QStackedWidget()
        self.stackedWidget.addWidget(self.macrosList)
        self.stackedWidget.addWidget(self.macroDetails)

        layout.addLayout(buttonslayout)
        layout.addWidget(self.stackedWidget)

        self.currentMacro = None

    def newMacro(self):
        self.recMacroBtn.setVisible(True)
        self.recMacroBtn.setEnabled(False)
        self.stackedWidget.setCurrentIndex(1)
        self.macroDetails.newMacro()
        macro = self.controller.createMacro()
        self.macroDetails.setCurrentMacro(macro)
        
    def macroNameDefined(self, ok):
        self.recMacroBtn.setEnabled(ok)

    def recordMacro(self, toggled):
        if toggled:
            self.recMacroBtn.setIcon(QtGui.QIcon(":/images/macro_stop.png"))
            self.recMacroBtn.setToolTip(self.tr("Stop recording macro"))
            self.newMacroBtn.setVisible(False)
            self.applyMacroBtn.setVisible(False)
            self.emit(QtCore.SIGNAL("recordMacroNow"),True)
        else:
            self.recMacroBtn.setIcon(QtGui.QIcon(":/images/macro.png"))
            self.recMacroBtn.setToolTip(self.tr("Start recording macro"))
            self.recMacroBtn.setVisible(False)
            self.emit(QtCore.SIGNAL("recordMacroNow"),False)
            self.newMacroBtn.setVisible(True)
            self.applyMacroBtn.setVisible(True)

    def viewMacros(self):
        self.stackedWidget.setCurrentIndex(0)
        if self.controller != None:
            self.reloadMacros()

    def showMacroInfo(self):
        if self.currentMacro != None and self.currentMacro != '':
            self.loadMacroInfo(self.currentMacro)
            self.stackedWidget.setCurrentIndex(1)
    
    def showEvent(self, event):
        self.viewMacros()

    def changeController(self, controller):
        if self.controller != controller:
            if self.controller:
                self.disconnect(self.macroDetails, QtCore.SIGNAL("actedOnMacro"),
                                self.controller.macroChanged)
                self.disconnect(self,QtCore.SIGNAL("recordMacroNow"),
                                self.controller.recordMacro)
                self.disconnect(self.controller, QtCore.SIGNAL("updateMacro"),
                                self.macroDetails.updateMacro)
                
            self.controller = controller
            self.connect(self.macroDetails, QtCore.SIGNAL("actedOnMacro"),
                         self.controller.macroChanged)
            self.connect(self,QtCore.SIGNAL("recordMacroNow"),
                     self.controller.recordMacro)
            self.connect(self.controller, QtCore.SIGNAL("updateMacro"),
                         self.macroDetails.updateMacro)
            
            self.reloadMacros()
            
    def reloadMacros(self):
        macro_names = self.controller.getMacroNames()
        self.macrosList.list.clear()

        for m in macro_names:
            self.macrosList.list.addItem(self.tr(m))

    def loadMacroInfo(self, name):
        """ """
        macro = self.controller.getMacro(name)
        self.macroDetails.setCurrentMacro(macro)

    def applyMacro(self):
        macro = self.controller.getMacro(self.currentMacro)
        try:
            macro.applyMacro(self.controller,
                             self.controller.currentPipeline, 
                             self.macroDetails.checkForce())
        except ExternalModuleNotSet, e:
            QtGui.QMessageBox.information(self, "VisTrails", str(e))
        except InvalidActionFound, i:
            QtGui.QMessageBox.information(self, "VisTrails", str(i))

    def macroUnselected(self):
        self.macroChanged(None)
            
    def macroChanged(self, text):
        if text != None:
            self.infoMacroBtn.setVisible(True)
            self.currentMacro = str(text)
            self.applyMacroBtn.setVisible(True)
        else:
            self.currentMacro = None
            self.infoMacroBtn.setVisible(False)
            self.applyMacroBtn.setVisible(False)


class QMacrosList(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        label = QtGui.QLabel("Macros")
        self.list= QtGui.QListWidget()
        self.list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        
        self.connect(self.list, QtCore.SIGNAL("itemSelectionChanged()"),
                     self.macroSelectionChanged)
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.addWidget(label)
        layout.addWidget(self.list)
        self.setLayout(layout)

    def macroSelectionChanged(self):
        if len(self.list.selectedItems()) == 0:
            self.emit(QtCore.SIGNAL("macroUnselected"))
            
class QMacroDetails(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.currentMacro = None
        
        label1 = QtGui.QLabel("Name: ",self)
        self.nameEdit = QtGui.QLineEdit(self)
        
        label2 = QtGui.QLabel("Description: ",self)
        self.descEdit = QtGui.QLineEdit(self)

        hl1 = QtGui.QHBoxLayout()
        hl1.setSpacing(0)
        hl1.setMargin(0)
        hl1.addWidget(label1)
        hl1.addWidget(self.nameEdit)

        hl2 = QtGui.QHBoxLayout()
        hl2.setSpacing(0)
        hl2.setMargin(0)
        hl2.addWidget(label2)
        hl2.addWidget(self.descEdit)
        
        self.cbForce = QtGui.QCheckBox("Automatically disable inconsistent actions")
        label3 = QtGui.QLabel("Macro actions")
        self.table = QMacroTable(0,4)
        labels = QtCore.QStringList()
        labels << self.tr("Play?") << self.tr("Action") << self.tr("Source Object") << self.tr("Destination Object")
        self.table.setHorizontalHeaderLabels(labels)
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.settingAssoc = False

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.addLayout(hl1)
        layout.addLayout(hl2)
        layout.addWidget(self.cbForce)
        layout.addWidget(label3)
        layout.addWidget(self.table)
        self.setLayout(layout)

        #creating action for the contextMenu
        self.setAct = QtGui.QAction(self.tr("Set Association"), self)
        self.connect(self.setAct, QtCore.SIGNAL("triggered()"),self.setAssociation)
        
        #signals and slots
        self.connect(self.nameEdit, QtCore.SIGNAL("textChanged(QString)"),
                     self.nameChanged)
        self.connect(self.nameEdit, QtCore.SIGNAL("editingFinished()"),
                     self.setName)
        self.connect(self.descEdit, QtCore.SIGNAL("editingFinished()"),
                     self.setDesc)
        self.connect(self.table, QtCore.SIGNAL("menuRequested"),
                     self.requestMenu)
    
    def checkForce(self):
        """ Convert Qt Nomenclature to True or False """

        if self.cbForce.checkState() == QtCore.Qt.Unchecked:
            return False
        else:
            return True

    def requestMenu(self,item,event):
        if item:
            if item.type == VisMacroItemType.Source:
                if str(item.action.sourceType) == 'External':
                    self.selectedMacroItem = item
                    self.showMenu(event.globalPos())
            elif item.type == VisMacroItemType.Destination:
                if str(item.action.destType) == 'External':
                    self.selectedMacroItem = item
                    self.showMenu(event.globalPos())
            elif item.type == VisMacroItemType.Undefined and item.action.endAction.type == 'DeleteConnection':
                if str(item.action.sourceType) == 'External':
                    self.selectedMacroItem = item
                    self.showMenu(event.globalPos())
        else:
            self.selectedMacroItem = None

    def showMenu(self,pos):
        menu = QtGui.QMenu(self)
        menu.addAction(self.setAct)
        menu.exec_(pos)

    def setAssociation(self):
        self.settingAssoc = True

    def setComponent(self,id):
        if id == -1:
            self.settingAssoc = False
        else:
            if self.settingAssoc:
               if not self.selectedMacroItem.action.baseAction.type in ['DeleteConnection']:
                   self.currentMacro.modules[self.selectedMacroItem.eId] = id
                   self.showActions(self.currentMacro, False)
                   self.settingAssoc = False
                   

    def setConnection(self,id):
        if id == -1:
            self.settingAssoc = False
        else:
            if self.settingAssoc:
               if self.selectedMacroItem.action.baseAction.type in ['DeleteConnection']:
                   self.currentMacro.connections[self.selectedMacroItem.eId] = id
                   self.showActions(self.currentMacro, False)
                   self.settingAssoc = False
                
    def showActions(self, macro, reload=True):
        if reload == True:
            macro.loadActions()
        self.table.setRowCount(0)
        
        for id in macro.actionList:
            a = macro.actions[id]
            row = self.table.rowCount()
            self.table.insertRow(row)
            info = a.info()
            
            action = info[0]
            item = QMacroItem("",a,a.baseAction.timestep,VisMacroItemType.CheckState)
            item.setFlags(QtCore.Qt.ItemIsEnabled | 
                          QtCore.Qt.ItemIsUserCheckable)
            if a.enabled:
                state = QtCore.Qt.Checked
            else:
                state = QtCore.Qt.Unchecked

            item.setCheckState(state)
            self.table.setItem(row,0,item)
            if a:
                a.connect(a, QtCore.SIGNAL("enabledChanged"), self.table.updateEnabled)
            if(len(info) > 1):
                sourceObj = info[1]
                if a.endAction.type == 'DeleteConnection':
                    item  = QMacroItem(self.tr(action),a,a.id,VisMacroItemType.Undefined)
                else:
                    item = QMacroItem(self.tr(action),a,-1,VisMacroItemType.Undefined)
                    item.setFlags(QtCore.Qt.ItemIsEnabled)

                if str(a.sourceType) == 'External' and a.endAction.type == 'DeleteConnection':
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    if a.macro.checkExternalConnection(a.id):
                        item.setTextColor(QtCore.Qt.black)
                        item.setIcon(QtGui.QIcon(":/images/lightcheck.png"))
                    else:
                        item.setTextColor(QtCore.Qt.red)
                        item.setIcon(QtGui.QIcon(":/images/info.png"))
                self.table.setItem(row,1,item)

                item  = QMacroItem(self.tr(sourceObj),a,a.sourceId,VisMacroItemType.Source)
                if str(a.sourceType) == 'External':
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    if a.endAction.type != 'DeleteConnection':
                        if a.macro.checkExternalModule(a.sourceId):
                            item.setTextColor(QtCore.Qt.black)
                            item.setIcon(QtGui.QIcon(":/images/lightcheck.png"))
                        else:
                            item.setTextColor(QtCore.Qt.red)
                            item.setIcon(QtGui.QIcon(":/images/info.png"))
                        if not a.verifyNumModules():
                            print "more than one external module referenced"
                    
                self.table.setItem(row,2,item)
            
            if(len(info) > 2):
                destObj = info[2]
                item  = QMacroItem(self.tr(destObj),a,a.destId,VisMacroItemType.Destination)

                if a.endAction.type != 'DeleteConnection' and str(a.destType) == 'External':
                    item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

                    
                    if a.macro.checkExternalModule(a.destId):
                        item.setIcon(QtGui.QIcon(":/images/lightcheck.png"))
                        item.setTextColor(QtCore.Qt.black)
                    else:
                        item.setIcon(QtGui.QIcon(":/images/info.png"))
                        item.setTextColor(QtCore.Qt.red)
                    if not a.verifyNumModules():
                        print "more than one external module referenced"
                    
                self.table.setItem(row,3,item)
                             
    def setCurrentMacro(self, macro):
        self.removeSignals()
        self.currentMacro = macro
        self.nameEdit.setText(self.tr(macro.name))
        self.descEdit.setText(self.tr(macro.description))
        self.showActions(macro)

    def removeSignals(self):
        if self.currentMacro and self.table:
            for id in self.currentMacro.actionList:
                action = self.currentMacro.actions[id]
                self.disconnect(action, QtCore.SIGNAL("enabledChanged"),
                                self.table.updateEnabled)

    def newMacro(self):
        self.nameEdit.clear()
        self.descEdit.clear()
        self.nameEdit.setFocus()
        self.removeSignals()
        self.table.setRowCount(0)
        
    def nameChanged(self, text):
        result = False
        if str(text) != "":
            result = True
        self.emit(QtCore.SIGNAL("macroNameChanged"),result)

    def setName(self):
        if self.currentMacro:
            oldname = self.currentMacro.name
            self.currentMacro.name =  str(self.nameEdit.text())
            if oldname != self.currentMacro.name:
                self.emit(QtCore.SIGNAL("actedOnMacro"),oldname)

    def setDesc(self):
        if self.currentMacro:
            self.currentMacro.description = str(self.descEdit.text())

    def updateMacro(self, name):
        if self.currentMacro.name == name:
            self.showActions(self.currentMacro)

VisMacroItemType = enum('VisMacroItemType',
                       ['Undefined', 'Source', 'Destination', 'CheckState'])

class QMacroTable(QtGui.QTableWidget):
    def __init__(self,rows,cols,parent=None):
        QtGui.QTableWidget.__init__(self,rows,cols,parent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            item = self.itemAt(event.x(),event.y())
            self.emit(QtCore.SIGNAL("menuRequested"),item, event)
        else:
            if event.button() == QtCore.Qt.LeftButton:
                item = self.itemAt(event.x(),event.y())
                if item.type == VisMacroItemType.CheckState:
                    if item.checkState() == QtCore.Qt.Checked:
                        #we disable the action because the state is going to 
                        # change from Checked to Unchecked
                        item.setActionEnabled(False)
                    else:
                        # now from Unchecked to Checked
                        item.setActionEnabled(True)
            
            QtGui.QTableWidget.mousePressEvent(self,event)

    def updateEnabled(self, eId, value):
        """ Event handler when the action the item contains 
            changes its enabled property """
        item = self.getItemById(eId)
        
        if value:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    def getItemById(self, id):
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.item(i,j)
                if item:
                    if item.eId == id:
                        return item

class QMacroItem(QtGui.QTableWidgetItem):
    def __init__(self, text, action, id, type):
        QtGui.QTableWidgetItem.__init__(self,text)
        self.action = action
        self.eId = id
        self.type = type

    def setExternal(self, extId):
        """ Sets the module correspondence. Returns True if successful.
        Parameters
        ----------
        - extId : 'int'
          external module id

        Returns
        -------

        - 'boolean'
        
        """
        #TODO: verify if the correspondence is valid
        if self.action.endAction.type != 'DeleteConnection':
            self.action.macro.modules[self.eId] = extId
        else:
            self.action.macro.connections[self.eId] = extId

    def setActionEnabled(self, enabled):
        """ Set if the corresponding macro action will be performed.
        Parameters
        ----------
        - enabled : 'bool'

        """
        self.action.setEnabled(enabled)
