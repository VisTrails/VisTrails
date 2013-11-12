import time
name = 'multithreading_test'
identifier = 'org.vistrails.tests.multithreading'
version = '0.1'


from vistrails.core.modules.vistrails_module import Module, NotCacheable, \
    parallelizable


@parallelizable(thread=True, process=True, systems={'ipython': True})
class WaiterThread(NotCacheable, Module):
    _input_ports = [
            ('value', '(org.vistrails.vistrails.basic:Module)')]
    _output_ports = [
            ('result', '(org.vistrails.vistrails.basic:Variant)')]

    def compute(self):
        time.sleep(3)
        value = self.getInputFromPort('value')
        self.setResult('result', value)


class BadWaiter(NotCacheable, Module):
    _input_ports = [
            ('value', '(org.vistrails.vistrails.basic:Module')]
    _output_ports = [
            ('result', '(org.vistrails.vistrails.basic:Variant')]

    def compute(self):
        time.sleep(3)
        value = self.getInputFromPort('value')
        self.setResult('result', value)


class Complicated(NotCacheable, Module):
    _input_ports = [
            ('condition1', '(org.vistrails.vistrails.basic:Boolean)'),
            ('condition2', '(org.vistrails.vistrails.basic:Boolean)'),
            ('if_true', '(org.vistrails.vistrails.basic:Integer)'),
            ('if_false', '(org.vistrails.vistrails.basic:Integer)')]
    _output_ports = [
            ('result', '(org.vistrails.vistrails.basic:Integer)')]

    def update(self):
        self.logging.begin_update(self)
        self.updateUpstream(
                self.conditions_ready,
                ['condition1', 'condition2'])

    def conditions_ready(self, connectors):
        self.__condition = (self.getInputFromPort('condition1') and
                            self.getInputFromPort('condition2'))
        if self.__condition:
            port = 'if_true'
        else:
            port = 'if_false'
        self.updateUpstream(
                self.input_ready,
                [port],
                priority=50)

    def input_ready(self, connectors):
        self.logging.begin_compute(self)
        if self.__condition:
            self.setResult('result', self.getInputFromPort('if_true'))
        else:
            self.setResult('result', self.getInputFromPort('if_false'))
        self.logging.end_update(self)
        self.logging.signalSuccess(self)
        self.done()


@parallelizable(thread=False, process=False, systems={'ipython-standalone': True})
class StandaloneDoubler(Module):
    _input_ports = [
            ('value', '(org.vistrails.vistrails.basic:Integer)')]
    _output_ports = [
            ('value', '(org.vistrails.vistrails.basic:Integer)')]

    def compute(self):
        i = self.getInputFromPort('value')
        self.setResult('value', i * 2)
        import os
        print os.getpid()


_modules = [WaiterThread, BadWaiter, Complicated, StandaloneDoubler]
