from IPython.parallel.error import RemoteError
import re
import sys

from vistrails.core.modules.vistrails_module.parallel import SchemeType, \
    register_parallelization_scheme, ParallelizationScheme
from vistrails.core.parallelization.common import get_pickled_module_inputs, \
    execute_serialized_pipeline, module_to_serialized_pipeline, set_results
from vistrails.core.modules.vistrails_module.errors import ModuleError

from .api import get_client
from .engine_manager import EngineManager


_ansi_code = re.compile(r'%s(?:(?:\[[^A-Za-z]*[A-Za-z])|[^\[])' % '\x1B')

def strip_ansi_codes(s):
    return _ansi_code.sub('', s)


def print_remoteerror(e):
    sys.stderr.write("Got exception from IPython engine:\n")
    sys.stderr.write("%s: %s\n" % (e.ename, e.evalue))
    sys.stderr.write("Traceback:\n%s\n" % strip_ansi_codes(e.traceback))


def initialize_then_execute_serialized_pipeline(*args):
    global init
    global app

    try:
        init
    except NameError:
        init = False

    if not init:
        import vistrails.core.application

        # Start a VisTrails application
        app = vistrails.core.application.init(args=[])

        init = True

    return execute_serialized_pipeline(*args)


@apply
class IPythonScheme(ParallelizationScheme):
    def __init__(self):
        ParallelizationScheme.__init__(self,
                50, # rather high priority; if the user connected to an IPython
                    # cluster, he probably wants to use it
                SchemeType.REMOTE_MACHINE,
                'ipython')
        self._enabled = False
        self._process_pool = None

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

        # Build the pipeline
        inputs = get_pickled_module_inputs(module)
        pipeline, moduleId, connected_outputports = \
                module_to_serialized_pipeline(module)

        # Start execution
        with rc.lock():
            ldview = rc.load_balanced_view(targets=engines)
            future = ldview.apply_async(
                    initialize_then_execute_serialized_pipeline,
                    pipeline,
                    moduleId,
                    inputs,
                    connected_outputports)
        async_task = module._runner.make_async_task()

        # IPython currently doesn't have a callback mechanism, so we start a
        # thread that blocks on AsyncResult#get()
        # Moreover, ZeroMQ sockets are NOT thread-safe, meaning that we cannot
        # just start a thread here to wait on the AsyncResult, as it would be
        # invalid to perform any other operation on the Client while it is
        # pending
        def callback(res):
            def get_results(runner):
                def compute():
                    try:
                        set_results(module, res.get())
                    except RemoteError, e:
                        print_remoteerror(e)
                        raise
                module.do_compute(compute=compute)
            async_task.callback(get_results)
        rc.add_callback(future, callback)

    def enabled(self):
        return self._enabled

    def set_enabled(self, enabled):
        self._enabled = enabled

    def finalize(self):
        EngineManager.cleanup()


register_parallelization_scheme(IPythonScheme)
