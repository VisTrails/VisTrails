from IPython.parallel.error import RemoteError

from vistrails.core.modules.vistrails_module import ModuleError
from vistrails.core.parallelization import SchemeType, Parallelization, \
    ParallelizationScheme
from vistrails.core.parallelization.common import get_module_inputs_with_defaults

from .api import get_client
from .utils import print_remoteerror


def make_fake_module_and_execute(compute_code, inputs):
    global IPythonFakeModule

    from types import FunctionType

    try:
        IPythonFakeModule
    except NameError:
        # Inject a fake Module class
        class IPythonFakeModule(object):
            def __init__(self, i):
                self.inputPorts = i
                self.outputPorts = {}

            def getInputFromPort(self, inputPort, allowDefault=True):
                try:
                    value, is_default = self.inputPorts[inputPort]
                    if allowDefault or not is_default:
                        return value[0]
                except KeyError:
                    pass
                raise ValueError("Missing value from port %s" % inputPort)

            def hasInputFromPort(self, inputPort):
                try:
                    value, is_default = self.inputPorts[inputPort]
                    return not is_default
                except KeyError:
                    return False

            def checkInputFromPort(self, inputPort):
                if not self.hasInputFromPort(inputPort):
                    raise ValueError("'%s' is a mandatory port" % inputPort)

            def forceGetInputFromPort(self, inputPort, defaultValue=None):
                try:
                    value, is_default = self.inputPorts[inputPort]
                    if not is_default:
                        return value[0]
                except KeyError:
                    pass
                return defaultValue

            def getInputListFromPort(self, inputPort):
                try:
                    value, is_default = self.inputPorts[inputPort]
                    if not is_default:
                        return value
                except KeyError:
                    pass
                raise ValueError("Missing value from port %s" % inputPort)

            def forceGetInputListFromPort(self, inputPort):
                try:
                    value, is_default = self.inputPorts[inputPort]
                    if not is_default:
                        return value
                except KeyError:
                    pass
                return []

            def setResult(self, port, value):
                self.outputPorts[port] = value

    IPythonFakeModule.compute = FunctionType(compute_code, globals(), 'compute')

    m = IPythonFakeModule(inputs)
    m.compute()

    return m.outputPorts


@apply
class IPythonStandaloneScheme(ParallelizationScheme):
    def __init__(self):
        ParallelizationScheme.__init__(self,
                40, # higher than regular IPython
                SchemeType.REMOTE_NO_VISTRAILS,
                'ipython-standalone')

    def do_compute(self, module):
        # Connect to cluster
        try:
            rc = get_client(shared_client=True)
            engines = rc.ids
        except Exception, error:
            raise ModuleError(
                    module,
                    "Exception while loading IPython: %s" % error)
        if not engines:
            raise ModuleError(
                    module,
                    "Exception while loading IPython: No IPython engines "
                    "detected!")

        # Get inputs
        inputs = get_module_inputs_with_defaults(module)

        # Execute
        with rc.load_balanced_view() as ldview:
            func_module = make_fake_module_and_execute.__module__
            make_fake_module_and_execute.__module__ = '__main__'
            try:
                future = ldview.apply_async(
                        make_fake_module_and_execute,
                        module.compute.im_func.func_code,
                        inputs)
            finally:
                make_fake_module_and_execute.__module__ = func_module
        async_task = module._runner.make_async_task()

        def callback(res):
            def get_results():
                def compute():
                    try:
                        results = res.get()
                    except RemoteError, e:
                        print_remoteerror(e)
                        raise
                    else:
                        module.outputPorts.update(results)
                module.do_compute(compute=compute)
            async_task.callback(get_results)
        rc.add_callback(future, callback)


# IPython has some logic in pickleutil (class CannedFunction) to send the
# function's bytecode to the engines
Parallelization.register_parallelization_scheme(IPythonStandaloneScheme)
