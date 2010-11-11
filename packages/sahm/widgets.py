from PyQt4 import QtCore, QtGui
import os

from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.constant_configuration import ConstantWidgetMixin

class PredictorListWidget(QtGui.QTreeWidget):
    def __init__(self, p_value, available_tree, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.available_tree = available_tree
        self.setColumnCount(2)
        self.tree_items = {}
        for source, file_list in self.available_tree.iteritems():
            source_item = QtGui.QTreeWidgetItem([source])
            self.addTopLevelItem(source_item)
            for (file, desc, categorical) in file_list:
                child_item = QtGui.QTreeWidgetItem([file, desc])
                child_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                    QtCore.Qt.ItemIsEnabled)
                child_item.setCheckState(0, QtCore.Qt.Unchecked)
                source_item.addChild(child_item)
                self.tree_items[(source, file)] = child_item
        self.set_values(p_value)

    def set_values(self, str_value):
        print 'set_values:', str_value
        values = []
        if str_value:
            values = eval(str_value)
        for value in values:
            if value in self.tree_items:
                self.tree_items[value].setCheckState(0, QtCore.Qt.Checked)
    
    def get_values(self):
        values = []
        for value, item in self.tree_items.iteritems():
            if item.checkState(0) == QtCore.Qt.Checked:
                values.append(value)
        return str(values)

class PredictorListConfigurationWidget(PredictorListWidget, 
                                       ConstantWidgetMixin):
    
    def __init__(self, param, available_tree, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        Initialize the line edit with its contents. Content type is limited
        to 'int', 'float', and 'string'

        """
        PredictorListWidget.__init__(self, param.strValue, available_tree, 
                                     parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        # assert param.namespace == None
        # assert param.identifier == 'edu.utah.sci.vistrails.basic'
#         self.available_tree = available_tree
#         self.setColumnCount(2)
#         for source, file_list in self.available_tree.iteritems():
#             source_item = QtGui.QTreeWidgetItem([source])
#             self.addTopLevelItem(source_item)
#             for (file, desc) in file_list:
#                 child_item = QtGui.QTreeWidgetItem([file, desc])
#                 child_item.setFlags(QtCore.Qt.ItemIsUserCheckable |
#                                     QtCore.Qt.ItemIsEnabled)
#                 child_item.setCheckState(0, QtCore.Qt.Unchecked)
#                 source_item.addChild(child_item)

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
        return self.get_values()
#         return 'abc'
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
        self.set_values(strValue)
#         self.update_text()
        if not silent:
            self.update_parent()
            
#     def update_text(self):
#         """ update_text() -> None
#         Update the text to the result of the evaluation

#         """
#         # FIXME: eval should pretty much never be used
#         base = expression.evaluate_expressions(self.text())
#         if self._contentType == 'String':
#             self.setText(base)
#         else:
#             try:
#                 self.setText(str(eval(str(base), None, None)))
#             except:
#                 self.setText(base)

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

    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        self._contents = self.get_values()
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QTreeWidget.focusInEvent(self, event)

    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QTreeWidget.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)

class PredictorListConfiguration(StandardModuleConfigurationWidget):
    # FIXME add available_dict as parameter to allow config
    def __init__(self, module, controller, available_tree, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, 
                                                   parent)

        # set title
        if module.has_annotation_with_key('__desc__'):
            label = module.get_annotation_by_key('__desc__').value.strip()
            title = '%s (%s) Module Configuration' % (label, module.name)
        else:
            title = '%s Module Configuration' % module.name
        self.setWindowTitle(title)
        self.build_gui(available_tree)

    def build_gui(self, available_tree):
        layout = QtGui.QVBoxLayout()
        # precompute tree so we only load once
 
        # factor PredictorListConfigurationWidget so that it can be reused in
        # both cases
        self.p_value = ''
        for function in self.module.functions:
            if function.name == 'value':
                self.p_value = function.parameters[0].strValue
        # should just be able to pass this across to the PredictorList config
        self.list_config = PredictorListWidget(self.p_value, available_tree)
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
                     self.close)
        self.setLayout(layout)

    def okTriggered(self):
        str_value = self.list_config.get_values()
        if str_value != self.p_value:
            print 'okTriggered:', str_value
            functions = [('value', [str_value])]
            self.controller.update_functions(self.module, functions)
        self.close()

    def sizeHint(self):
        return QtCore.QSize(512, 512)

def get_predictor_widget(class_name, tree):
    def __init__(self, param, parent=None):
        PredictorListConfigurationWidget.__init__(self, param, tree, parent)
    class_name += "PredictorListWidget"
    widget_class = type(class_name, (PredictorListConfigurationWidget,),
                        {'__init__': __init__})
    return widget_class

def get_predictor_config(class_name, tree):
    def __init__(self, module, controller, parent=None):
        PredictorListConfiguration.__init__(self, module, controller, tree, 
                                            parent)
    class_name += "PredictorListConfig"
    widget_class = type(class_name, (PredictorListConfiguration,),
                        {'__init__': __init__})
    return widget_class
