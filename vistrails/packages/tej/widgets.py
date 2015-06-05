from PyQt4 import QtGui

from vistrails.gui.modules.source_configure import SourceConfigurationWidget


class ShellSourceConfigurationWidget(SourceConfigurationWidget):
    """Configuration widget for SubmitShellJob.

    Allows the user to edit a shell script that will be run on the server.
    """
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller,
                                           QtGui.QTextEdit,
                                           has_inputs=False, has_outputs=False,
                                           parent=parent)
