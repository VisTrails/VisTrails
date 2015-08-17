class BaseExecutionKernel(object):
    """Base class for execution kernels for VisTrails.

    A kernel is a process in which computation happens. It is a separate
    process from the one the VisTrails application lives in, allowing for
    safety (if execution aborts of crashes), responsiveness (the application's
    event loop can keep running) and parallelism (multiple kernels can be
    started). A kernel might be local or remote, and implemented in a variety
    of ways; VisTrails interacts with it through instances of
    BaseExecutionKernel subclasses, which know how to start/connect/communicate
    with them.
    """
    def __init__(self, name):
        self.kernel_name = name
        self.started = False

    def start(self):
        raise NotImplementedError
