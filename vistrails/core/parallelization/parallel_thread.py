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
        self._thread_pool = None
        self._pool_size = None

    def thread_pool(self, size):
        if not size or size < 0:
            size = max(multiprocessing.cpu_count(), 2)
                    # This thread count is somewhat arbitrary; Python code will
                    # not run in parallel anyway...
        if self._thread_pool is not None and self._pool_size != size:
            self._thread_pool.shutdown(wait=True)
            self._thread_pool = None
        if self._thread_pool is None:
            self._thread_pool = concurrent.futures.ThreadPoolExecutor(size)
            self._pool_size = size
        return self._thread_pool

    def do_compute(self, target, module):
        size = target.get_annotation('pool_size')
        if size:
            size = int(size.value)
        else:
            size = 0

        future = self.thread_pool(size).submit(module.compute)
        async_task = module._runner.make_async_task()

        def thread_done():
            def compute():
                try:
                    return future.result()
                finally:
                    module_exec = module.module_exec.do_copy(
                            new_ids=True,
                            id_scope=module.logging.log.log.id_scope,
                            id_remap={})
                    module.logging.log_remote_execution(
                            module, 'threading',
                            module_execs=[module_exec])
            module.do_compute(compute=compute)
        future.add_done_callback(lambda res: async_task.callback(thread_done))

    def finalize(self):
        if self._thread_pool is not None:
            self._thread_pool.shutdown(wait=True)
            self._thread_pool = None


Parallelization.register_parallelization_scheme(ThreadScheme)
