""" This file describe the module methods box that user can drop
methods from method palette into it

"""
from PyQt4 import QtCore, QtGui
from gui.method_dropbox import QMethodDropBox
from gui.common_widgets import QToolWindowInterface

################################################################################

class QModuleMethods(QMethodDropBox, QToolWindowInterface):
    """
    QModuleMethods is showing methods of a single module, it also
    support drop actions of method items from the method palette
    
    """
    def __init__(self, parent=None):
        """ QModuleMethods(parent: QWidget) -> QModuleMethods
        Initialize widget constraints
        
        """
        QMethodDropBox.__init__(self, parent)
        self.setWindowTitle('Properties')
