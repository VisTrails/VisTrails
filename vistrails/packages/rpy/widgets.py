from core.modules.source_configure import SourceConfigurationWidget, \
    SourceEditor

class RSourceConfigurationWidget(SourceConfigurationWidget):

    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, None,
                                           True, True, parent)

class RFigureConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        SourceConfigurationWidget.__init__(self, module, controller, None,
                                           True, False, parent)
