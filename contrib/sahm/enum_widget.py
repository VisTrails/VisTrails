from PyQt5 import QtCore, QtGui, QtWidgets
from core.modules.constant_configuration import ConstantWidgetMixin

class EnumWidget(QtWidgets.QComboBox, ConstantWidgetMixin):
    param_values = []
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        """
        contents = param.strValue
        contentType = param.type
        QtWidgets.QComboBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        # want to look up in registry based on parameter type
        
        self.addItem('')
        for val in self.param_values:
            self.addItem(val)

        curIdx = self.findText(contents)
        if curIdx != -1:
            self.setCurrentIndex(curIdx)
        self._contentType = contentType
        self.currentIndexChanged[int].connect(self.update_parent)

    def contents(self):
        curIdx = self.currentIndex()
        if curIdx == -1:
            print '*** ""'
            return ''
        print '*** "%s"' % str(self.itemText(curIdx))
        return str(self.itemText(curIdx))

    def setContents(self, strValue, silent=True):
        curIdx = self.findText(contents)
        self.setCurrentIndex(curIdx)
        if not silent:
            self.update_parent()

def build_enum_widget(name, param_values):
    return type(name, (EnumWidget,), {'param_values': param_values})
