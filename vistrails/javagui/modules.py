from javax.swing import JTextField
from java.awt import Dimension
from java.lang import Integer

from utils import InputValidationListener


class ConstantWidget(object):
    def __init__(self, portvalue, contents=None):
        self._portvalue = portvalue
        self._last_contents = contents

    def update_parent(self):
        new_contents = self.contents()
        if new_contents != self._last_contents:
            self._portvalue.value_changed(new_contents)
            self._last_contents = new_contents


# TODO : This only handles strings ATM
class StandardConstantWidget(JTextField, ConstantWidget):
    def __init__(self, portvalue, param):
        JTextField.__init__(self, param.strValue)
        ConstantWidget.__init__(self, portvalue, param.strValue)
        self.setMaximumSize(Dimension(
                Integer.MAX_VALUE,
                self.getPreferredSize().height))

        listener = InputValidationListener(self._validation)
        self.addKeyListener(listener)
        self.addFocusListener(listener)

    def contents(self):
        return self.getText()

    def _validation(self):
        self.update_parent()


def get_widget_class(module_class):
    klass = module_class.get_widget_class()
    if klass is None:
        return StandardConstantWidget
    if type(klass) == tuple:
        (path, class_name) = klass
        module = __import__(path, globals(), locals(), [class_name])
        return getattr(module, class_name)
    return klass
