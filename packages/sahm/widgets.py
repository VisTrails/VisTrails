from PyQt4 import QtCore, QtGui
import csv
import os

from core.modules.constant_configuration import ConstantWidgetMixin

class PredictorListConfigurationWidget(QtGui.QTreeWidget, ConstantWidgetMixin):
    
    def __init__(self, param, available_tree, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        Initialize the line edit with its contents. Content type is limited
        to 'int', 'float', and 'string'

        """
        QtGui.QTreeWidget.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        # assert param.namespace == None
        # assert param.identifier == 'edu.utah.sci.vistrails.basic'
        self.available_tree = available_tree
        self.setColumnCount(2)
        for source, file_list in self.available_tree.iteritems():
            source_item = QtGui.QTreeWidgetItem([source])
            self.addTopLevelItem(source_item)
            for (file, desc) in file_list:
                child_item = QtGui.QTreeWidgetItem([file, desc])
                child_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                    QtCore.Qt.ItemIsEnabled)
                child_item.setCheckState(0, QtCore.Qt.Unchecked)
                source_item.addChild(child_item)

        contents = param.strValue
        contentType = param.type

        # need to deserialize contents and set tree widget accordingly
        # self.setText(contents)
        self._contentType = contentType
#         self.connect(self,
#                      QtCore.SIGNAL('returnPressed()'),
#                      self.update_parent)

    def contents(self):
        """contents() -> str
        Re-implement this method to make sure that it will return a string
        representation of the value that it will be passed to the module
        As this is a QLineEdit, we just call text()

        """
        return 'abc'
#         self.update_text()
#         return str(self.text())

    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Re-implement this method so the widget can change its value after 
        constructed. If silent is False, it will propagate the event back 
        to the parent.
        As this is a QLineEdit, we just call setText(strValue)
        """
#         self.setText(strValue)
#         self.update_text()
#         if not silent:
#             self.update_parent()
        pass
            
    def update_text(self):
        """ update_text() -> None
        Update the text to the result of the evaluation

        """
        # FIXME: eval should pretty much never be used
        base = expression.evaluate_expressions(self.text())
        if self._contentType == 'String':
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)

    def sizeHint(self):
        return QtCore.QSize(512, 512)

#     def sizeHint(self):
#         metrics = QtGui.QFontMetrics(self.font())
#         width = min(metrics.width(self.text())+10,70)
#         return QtCore.QSize(width, 
#                             metrics.height()+6)
    
#     def minimumSizeHint(self):
#         return self.sizeHint()
    
    ###########################################################################
    # event handlers

#     def focusInEvent(self, event):
#         """ focusInEvent(event: QEvent) -> None
#         Pass the event to the parent

#         """
#         self._contents = str(self.text())
#         if self.parent():
#             QtCore.QCoreApplication.sendEvent(self.parent(), event)
#         QtGui.QLineEdit.focusInEvent(self, event)

#     def focusOutEvent(self, event):
#         self.update_parent()
#         QtGui.QLineEdit.focusOutEvent(self, event)
#         if self.parent():
#             QtCore.QCoreApplication.sendEvent(self.parent(), event)

class ClimatePredictorListConfig(PredictorListConfigurationWidget):
    def __init__(self, param, parent=None):
        layers_fname = os.path.join(os.path.dirname(__file__), 'layers.csv')
        csv_reader = csv.reader(open(layers_fname, 'rU'))
        # pass on header
        csv_reader.next()
        available_dict = {}
        for row in csv_reader:
            if row[0] == 'Climate':
                if row[1] not in available_dict:
                    available_dict[row[1]] = []
                available_dict[row[1]].append((row[3], row[2]))

        print available_dict
#         available_dict = {'test1': [('abc', 'def'), ('ghi', 'jkl')], 
#                           '2test': [('mno', 'pqr'), ('stu', 'vwx')]}
        PredictorListConfigurationWidget.__init__(self, param, available_dict, 
                                                  parent)
