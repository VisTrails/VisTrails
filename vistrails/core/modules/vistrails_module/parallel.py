###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

import warnings

from .errors import ModuleError, ModuleErrors, ModuleSuspended
from .module import BaseModule, InputWrapper, Module


###############################################################################

class SeparateThread(BaseModule):
    """This mixin enables a Module's compute() method to be run in parallel.

    The compute() or compute_static() method will be run in a thread in
    parallel with the execution of other modules.
    Using compute() here is only safe because Python uses a Global Interpreter
    Lock (GIL). You should probably use compute_static() which is thread safe.

    Threads are best suited for tasks that are NOT CPU-intensive (for instance
    IO bound, manipulating large files or network connections...) or that use
    an extension library that unlocks the GIL (such as numpy).
    """

    # We want to be started before the "regular compute" tasks, because we run
    # in the background
    COMPUTE_PRIORITY = Module.COMPUTE_BACKGROUND_PRIORITY

    def do_compute(self):
        self._runner.run_thread(self.thread_done, self.compute)

    def thread_done(self, future):
        self.done()
        try:
            future.result()
            self.computed = True
        except ModuleSuspended, e:
            self.suspended = e.msg
            self._module_suspended = e
            self.logging.end_update(self, e, was_suspended=True)
            self.logging.signalSuspended(self)
            return
        except ModuleError, me:
            if hasattr(me.module, 'interpreter'):
                raise
            else:
                msg = "A dynamic module raised an exception: '%s'"
                msg %= str(me)
                raise ModuleError(self, msg)
        except ModuleErrors:
            raise
        except KeyboardInterrupt, e:
            raise ModuleError(self, 'Interrupted by user')
        except Exception, e:
            import traceback
            traceback.print_exc()
            raise ModuleError(self, 'Uncaught exception: "%s"' % str(e))
        if self.annotate_output:
            self.annotate_output_values()
        self.upToDate = True
        self.logging.end_update(self)
        self.logging.signalSuccess(self)


###############################################################################

class SeparateProcess(BaseModule):
    """This mixin executes the Module's compute_static() method in parallel.

    You mustn't use the compute() method but have to use compute_static()
    instead, as the Module object is not copied to the new processes.
    The compute_static() method will be run in parallel with the execution of
    other modules, via the multiprocessing library.

    Processes are more costly than threads but are best suited for tasks that
    require a lot of CPU power, as they will effectively execute in parallel
    with other Python code.
    """

    # We want to be started before the "regular compute" tasks, because we run
    # in the background
    COMPUTE_PRIORITY = Module.COMPUTE_BACKGROUND_PRIORITY

    def do_compute(self):
        if self.__class__.compute != Module.compute:
            warnings.warn("compute() was overridden! You should only use "
                          "compute_static with the SeparateProcess mixin",
                          UserWarning)

        inputs = InputWrapper(self)
        self._runner.run_process(self.process_done,
                                 self.compute_static, inputs)

    def process_done(self, future):
        self.done()
        try:
            outputs = future.result()
            for port, value in outputs.iteritems():
                self.setResult(port, value)
            self.computed = True
        except ModuleSuspended, e:
            self.suspended = e.msg
            self._module_suspended = e
            self.logging.end_update(self, e, was_suspended=True)
            self.logging.signalSuspended(self)
            return
        except ModuleError, me:
            if hasattr(me.module, 'interpreter'):
                raise
            else:
                msg = "A dynamic module raised an exception: '%s'"
                msg %= str(me)
                raise ModuleError(self, msg)
        except ModuleErrors:
            raise
        except KeyboardInterrupt, e:
            raise ModuleError(self, 'Interrupted by user')
        except Exception, e:
            import traceback
            traceback.print_exc()
            raise ModuleError(self, 'Uncaught exception: "%s"' % str(e))
        if self.annotate_output:
            self.annotate_output_values()
        self.upToDate = True
        self.logging.end_update(self)
        self.logging.signalSuccess(self)
