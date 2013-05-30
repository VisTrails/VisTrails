from vistrails.core.modules.vistrails_module import Module

class MplObject(Module):
    _input_ports = [("subfigRow", "(org.vistrails.vistrails.spreadsheet:Integer)",
                     {"defaults": ["1"]}),
                    ("subfigCol", "(org.vistrails.vistrails.spreadsheet:Integer)",
                     {"defaults": ["1"]})]
    _output_ports = [("self", "(org.vistrails.vistrails.matplotlib:MplObject)")]

    def __init__(self):
        Module.__init__(self)
        self.figInstance = None

    def set_fig(self, fig):
        self.figInstance = fig

    def get_fig(self):
        if self.figInstance is None:
            self.figInstance = pylab.figure()
        return self.figInstance
