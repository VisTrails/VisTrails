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
        self._process_pool = None
        self._pool_size = None

    def process_pool(self, size):
        if not size or size < 0:
            size = multiprocessing.cpu_count()
        if self._process_pool is not None and self._pool_size != size:
            self._process_pool.shutdown(wait=True)
            self._process_pool = None
        if self._process_pool is None:
            self._process_pool = concurrent.futures.ProcessPoolExecutor(size)
            self._pool_size = size
        return self._process_pool

    def do_compute(self, target, module):
        size = target.get_annotation('pool_size')
        if size:
            size = int(size.value)
        else:
            size = 0

        inputs = get_pickled_module_inputs(module)
        pipeline, moduleId, connected_outputports = \
                module_to_serialized_pipeline(module)

        future = self.process_pool(size).submit(
                execute_serialized_pipeline,
                pipeline,
                moduleId,
                inputs,
                connected_outputports)
        async_task = module._runner.make_async_task()

        def get_results():
            results = future.result() # Might raise
            set_results(module, results, 'multiprocessing')
        def process_done():
            module.do_compute(compute=get_results)
        future.add_done_callback(lambda res: async_task.callback(process_done))

    def finalize(self):
        if self._process_pool is not None:
            self._process_pool.shutdown(wait=True)
            self._process_pool = None


Parallelization.register_parallelization_scheme(ProcessScheme)
