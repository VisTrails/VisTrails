from vistrails.core.modules.vistrails_module.parallel import \
    SchemeType, register_parallelization_scheme


def thread_do_compute(self):
    def thread_done(future):
        self.do_compute_not_parallel(compute=future.result)

    self._runner.run_thread(
            thread_done,
            self.compute)


register_parallelization_scheme(
        10, SchemeType.THREAD, 'threading', thread_do_compute)
