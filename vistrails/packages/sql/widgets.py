from __future__ import division

from vistrails.gui.modules.source_configure import SourceConfigurationWidget


class SQLSourceConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(
                self,
                module,
                controller,
                None,       # editor_class
                True,       # has_inputs
                False,      # has_outputs
                parent)
