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

from vistrails.core.utils import bisect, enum

from .errors import ModuleError, ModuleErrors, ModuleSuspended
from .module import BaseModule, InputWrapper, Module


###############################################################################

SchemeType = enum('SchemeType', [
        'THREAD', 'LOCAL_PROCESS', 'REMOTE_MACHINE', 'REMOTE_NO_VISTRAILS'])

def supports(scheme_type, name, thread, process, remote, standalone, systems):
    try:
        return systems[name]
    except KeyError:
        pass
    if scheme_type == SchemeType.THREAD and thread:
        return True
    elif scheme_type == SchemeType.LOCAL_PROCESS and process:
        return True
    elif scheme_type == SchemeType.REMOTE_MACHINE and remote:
        return True
    elif scheme_type == SchemeType.REMOTE_NO_VISTRAILS and standalone:
        return True
    else:
        return False


_parallelization_schemes = []

def register_parallelization_scheme(priority, scheme_type, name, scheme):
    """Registers a ParallelizationScheme to be used by parallelizable().
    """
    i = bisect(
            len(_parallelization_schemes),
            _parallelization_schemes.__getitem__,
            (priority, scheme_type, name, scheme),
            comp=lambda a, b: a[0] < b[0])
    _parallelization_schemes.insert(i, (priority, scheme_type, name, scheme))


def _do_compute(self):
    """This method is injected as do_compute in parallelizable modules.

    When the parallelizable() class decorator is used on a class, this method
    gets injected as do_compute. It uses the _parallelizable dict (also
    injected) to determine what parallelization schemes are supported.
    """
    for priority, scheme_type, name, scheme in _parallelization_schemes:
        if supports(scheme_type, name, **self._parallelizable):
            scheme(self)


def parallelizable(thread=True, process=False, remote=False, standalone=False,
        systems={}):
    """This decorator enables a Module's compute() method to run in parallel.

    Use this class decorator to mark a Module subclass as being able to execute
    in parallel. You can specify which kind of parallelism is supported using
    the keyword arguments:
      * thread: enabled by default if you use this decorator. This means that
      the compute() method can be run in a separate thread, in parallel with
      the execution of other modules.
      * process: means that compute() can be run in a separate process using
      multiprocessing from the standard library.
      * remote: means that compute() can be run on a different machine.
      * standalone: means that compute() can be run on a machine even if it
      doesn't have VisTrails.

    The requirements for your code are as follow (each type includes the
    constraints from the previous type as well):
      * thread: the module doesn't thread-unsafe global states or libraries.
      * process: the inputs and outputs for this module are pickleable between
      processes.
      * remote: the module doesn't use local files (that are not on the remote
      machines) or global variables (including imports! you should move them to
      the method's body).
      * standalone: means that no use is made of VisTrails's modules and
      functions, and that only the methods accessing inputs and setResult() are
      used on 'self' ('self' will be a pickled copy of a simplified Module
      instance).

    In addition, you may specify whether a specific system can be used by
    adding it to the 'system' dictionary.

    Example:
        @parallelizable(thread=False, remote=True, systems=dict(ipython=False))
        class MyModule(Module):
            ...
    """
    def decorator(klass):
        if not issubclass(klass, Module):
            raise TypeError("parallelizable should be used on Module "
                            "subclasses, not '%s'" % klass)
        klass.COMPUTE_PRIORITY = Module.COMPUTE_BACKGROUND_PRIORITY
        klass.do_compute_not_parallel = klass.do_compute
        klass.do_compute = _do_compute
        klass._parallelizable = dict(
                thread=thread,
                process=process,
                remote=remote,
                standalone=standalone,
                systems=systems)
        return klass
    return decorator
