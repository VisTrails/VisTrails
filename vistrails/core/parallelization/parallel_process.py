import warnings

from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.vistrails_module.parallel import \
    SchemeType, register_parallelization_scheme, InputWrapper


def process_do_compute(self):
    def process_done(future):
        def compute():
            outputs = future.result()
            for port, value in outputs.iteritems():
                self.setResult(port, value)
        self.do_compute_not_parallel(compute=compute)

    if self.__class__.compute != Module.compute:
        warnings.warn("compute() was overridden! You should only use "
                      "compute_static when using @parallelizable",
                      UserWarning)

    inputs = InputWrapper(self)
    self._runner.run_thread(
            process_done,
            self.compute_static, inputs)


register_parallelization_scheme(
        20, SchemeType.LOCAL_PROCESS, 'multiprocessing', process_do_compute)
