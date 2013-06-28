from PyQt4 import QtGui

from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

from .parallel_thread import QParallelThreadSettings
from .parallel_process import QParallelProcessSettings
from .parallel_ipython import QParallelIPythonSettings


class QParallelizationSettings(QtGui.QTabWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        super(QParallelizationSettings, self).__init__(parent)

        self.setWindowTitle("Parallelization")

        def add(klass):
            self.addTab(klass(), klass.TAB_NAME)

        add(QParallelThreadSettings)
        add(QParallelProcessSettings)
        add(QParallelIPythonSettings)
