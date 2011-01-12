from PyQt4 import QtCore, QtGui
from core.modules.constant_configuration import ConstantWidgetMixin

class EnumWidget(QtGui.QComboBox, ConstantWidgetMixin):
    param_values = []
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        """
        contents = param.strValue
        contentType = param.type
        QtGui.QComboBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        # want to look up in registry based on parameter type
        
        self.addItem('')
        for val in self.param_values:
            self.addItem(val)

        curIdx = self.findText(contents)
        if curIdx != -1:
            self.setCurrentIndex(curIdx)
        self._contentType = contentType
        self.connect(self,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.update_parent)

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
