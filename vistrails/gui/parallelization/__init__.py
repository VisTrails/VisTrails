from PyQt4 import QtCore, QtGui

from vistrails.core.parallelization import Parallelization
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface


class QParallelizationSettings(QtGui.QTabWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        super(QParallelizationSettings, self).__init__(parent)

        self.setWindowTitle("Parallelization")

        def add(klass):
            scrollArea = QtGui.QScrollArea()
            scrollArea.setWidget(klass())
            scrollArea.setHorizontalScrollBarPolicy(
                    QtCore.Qt.ScrollBarAlwaysOff)
            scrollArea.setVerticalScrollBarPolicy(
                    QtCore.Qt.ScrollBarAsNeeded)
            self.addTab(scrollArea, klass.TAB_NAME)

        widgets = set()
        for scheme in Parallelization.parallelization_schemes:
            widget = scheme.get_gui_widget()
            if widget is not None and widget not in widgets:
                add(widget)
                widgets.add(widget)
