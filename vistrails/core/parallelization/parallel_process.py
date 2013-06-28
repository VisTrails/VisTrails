import concurrent.futures

from vistrails.core.modules.vistrails_module.parallel import SchemeType, \
    register_parallelization_scheme, ParallelizationScheme
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

    def process_pool(self):
        if self._process_pool is None:
            self._process_pool = concurrent.futures.ProcessPoolExecutor()
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
        def process_done(runner):
            module.do_compute(compute=get_results)
        future.add_done_callback(lambda res: async_task.callback(process_done))


register_parallelization_scheme(ProcessScheme)
