'''
Created on Sep 17, 2010

@author: talbertc
'''
from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui

class SelectListWidget(QtGui.QTreeWidget):

    def __init__(self, available_list, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.tree_items = {}
        for file in available_list:
            child_item = QtGui.QTreeWidgetItem([file.name,])
            child_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                QtCore.Qt.ItemIsEnabled)
            child_item.setCheckState(0, QtCore.Qt.Checked)
            self.addTopLevelItem(child_item)
            self.tree_items[file] = child_item

    def getSelected(self):
        values = []
        for file,item in self.tree_items.iteritems():
            if item.checkState(0) == QtCore.Qt.Checked:
                values.append(file)
        return values

class SelectListDialog(QtGui.QDialog):
    def __init__(self, predictorList, parent=None):
        self.outputList= []
        QtGui.QDialog.__init__(self,parent)
        layout = QtGui.QVBoxLayout()
        
        self.list_config = SelectListWidget(predictorList)
        layout.addWidget(self.list_config)

        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(self.buttonLayout)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'),
                     self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'),
                     self.cancel)
        self.setLayout(layout)

    def okTriggered(self):

        self.outputList=self.list_config.getSelected()
        self.done(0)

    def cancel(self):
        self.done(1)

class SelectPredictorsLayers(Module):
    '''
    select from a list of processessed predictor layers for inclusion in the module
    '''

    _input_ports = [("Predictors", "(gov.usgs.sahm:PredictorList:DataInput)")]
    _output_ports = [("SelectedPredictors",'(edu.utah.sci.vistrails.basic:Boolean)')]

    def compute(self):
        print "Starting compute"
        predictorList = self.getInputFromPort("Predictors")
        outputPredictorList = []

        outputPredictorList = self.callPredictorList(predictorList)

        self.setResult("SelectedPredictors",outputPredictorList)
        print "Finished compute"

    def callPredictorList(self, predictorList):
        outputPredictorList = []
        dialog = SelectListDialog(predictorList)
        retVal = dialog.exec_()
        if retVal == 0:
            outputPredictorList = dialog.outputList
        else:
            outputPredictorList =  predictorList
        return outputPredictorList

