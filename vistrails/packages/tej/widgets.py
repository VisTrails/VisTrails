from __future__ import division

from vistrails.gui.modules.source_configure import SourceConfigurationWidget
from vistrails.gui.modules.string_configure import TextEditor


class ShellSourceConfigurationWidget(SourceConfigurationWidget):
    """Configuration widget for SubmitShellJob.

    Allows the user to edit a shell script that will be run on the server.
    """
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller,
                                           TextEditor,
                                           has_inputs=False, has_outputs=False,
                                           parent=parent)
