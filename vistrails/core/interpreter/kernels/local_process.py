import multiprocessing
import os

from .base import BaseExecutionKernel


def remote(pipe):
    pass


class LocalProcessExecutionKernel(BaseExecutionKernel):
    """A local kernel using the multiprocessing module.

    This starts a process using multiprocessing, and communicates with it
    through pipes.
    """
    def __init__(self):
        pid = os.getpid()
        BaseExecutionKernel.__init__(self, "Local process, pid=%d" % pid)

    def start(self):
        self.pipe, otherpipe = multiprocessing.Pipe()
        self.process = multiprocessing.Process(target=remote,
                                               args=(otherpipe,))
        self.process.start()
