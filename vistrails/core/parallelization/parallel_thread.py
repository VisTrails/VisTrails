import concurrent.futures
import multiprocessing

from vistrails.core.modules.vistrails_module.parallel import SchemeType, \
    register_parallelization_scheme, ParallelizationScheme


@apply
class ThreadScheme(ParallelizationScheme):
    def __init__(self):
        ParallelizationScheme.__init__(self,
                200, # low priority
                SchemeType.THREAD,
                'threading')
        self._thread_pool = None

    def thread_pool(self):
        if self._thread_pool is None:
            self._thread_pool = concurrent.futures.ThreadPoolExecutor(
                    multiprocessing.cpu_count())
        return self._thread_pool

    def do_compute(self, module):
        future = self.thread_pool().submit(module.compute)
        async_task = module._runner.make_async_task()

        def thread_done(runner):
            module.do_compute(compute=future.result)
        future.add_done_callback(lambda res: async_task.callback(thread_done))


register_parallelization_scheme(ThreadScheme)
