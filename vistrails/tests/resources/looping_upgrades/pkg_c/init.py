from vistrails.core.modules.vistrails_module import Module


class C(Module):
    _output_ports = [('result', 'basic:String')]

    def compute(self):
        self.set_output('result', 'C')


_modules = [C]
