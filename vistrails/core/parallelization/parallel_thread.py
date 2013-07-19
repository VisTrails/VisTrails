import concurrent.futures
import multiprocessing

from vistrails.core.parallelization import SchemeType, Parallelization, \
    ParallelizationScheme


@apply
class ThreadScheme(ParallelizationScheme):
    def __init__(self):
        ParallelizationScheme.__init__(self,
                200, # low priority
                SchemeType.THREAD,
                'threading')
        self._enabled = True
        self._thread_pool = None
        self._pool_size = max(multiprocessing.cpu_count(), 2)
                # This initial thread count is somewhat arbitrary; Python code
                # will not run in parallel anyway...
                # It is adjustable via the GUI

    def thread_pool(self):
        if self._thread_pool is None:
            self._thread_pool = concurrent.futures.ThreadPoolExecutor(
                    self._pool_size)
        return self._thread_pool

    def do_compute(self, module):
        future = self.thread_pool().submit(module.compute)
        async_task = module._runner.make_async_task()

        def thread_done(runner):
            module.do_compute(compute=future.result)
        future.add_done_callback(lambda res: async_task.callback(thread_done))

    def enabled(self):
        return self._enabled

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_pool_size(self, nb):
        if self._pool_size != nb and self._thread_pool is not None:
            self._thread_pool.shutdown()
            self._thread_pool = None
        self._pool_size = nb

    def finalize(self):
        if self._thread_pool is not None:
            self._thread_pool.shutdown()
            self._thread_pool = None


Parallelization.register_parallelization_scheme(ThreadScheme)
