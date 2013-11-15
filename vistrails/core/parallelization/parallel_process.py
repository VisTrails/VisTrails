import concurrent.futures
import multiprocessing

from vistrails.core.parallelization import SchemeType, Parallelization, \
    ParallelizationScheme
from vistrails.core.parallelization.common import get_pickled_module_inputs, \
    execute_serialized_pipeline, module_to_serialized_pipeline, set_results


@apply
class ProcessScheme(ParallelizationScheme):
    def __init__(self):
        ParallelizationScheme.__init__(self,
                100,
                SchemeType.LOCAL_PROCESS,
                'multiprocessing')
        self._enabled = True
        self._process_pool = None
        self._pool_size = multiprocessing.cpu_count()

    def process_pool(self):
        if self._process_pool is None:
            self._process_pool = concurrent.futures.ProcessPoolExecutor(
                    self._pool_size)
        return self._process_pool

    def do_compute(self, module):
        inputs = get_pickled_module_inputs(module)
        pipeline, moduleId, connected_outputports = \
                module_to_serialized_pipeline(module)

        future = self.process_pool().submit(
                execute_serialized_pipeline,
                pipeline,
                moduleId,
                inputs,
                connected_outputports)
        async_task = module._runner.make_async_task()

        def get_results():
            results = future.result() # Might raise
            set_results(module, results)
        def process_done():
            module.do_compute(compute=get_results)
        future.add_done_callback(lambda res: async_task.callback(process_done))

    def enabled(self):
        return self._enabled

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_pool_size(self, nb):
        if self._pool_size != nb and self._process_pool is not None:
            self._process_pool.shutdown()
            self._process_pool = None
        self._pool_size = nb

    def finalize(self):
        if self._process_pool is not None:
            self._process_pool.shutdown()
            self._process_pool = None


Parallelization.register_parallelization_scheme(ProcessScheme)
