.. _chap-parallelization:

****************************
Parallelization in VisTrails
****************************

This chapters provides an internal view at the different parallel capabilities
of |vistrails|. These build on a number of different layers that are
described in this document.

Note that you are still free to use threading or multiprocessing in your
module's ``compute()`` method (or the new futures_ library). However you should
be careful not to interact with |vistrails| from other threads or processes.

.. _futures: http://docs.python.org/dev/library/concurrent.futures.html

Task system
===========

Since version 2.1, modules no longer directly call their upstream modules'
``update()`` method. The interpreter is based on a task system, in which
modules can add tasks to be executed asynchronously. For example:

.. code-block:: python
   :linenos:

   # The TaskRunner can be accessed with the _runner attribute of tasks
   self._runner.add([self.some_method, some_other_task], # tasks
                    callback=lambda runner: self.tasks_done(),
                    priority=40, # Priority for the tasks, lower is more urgent
                    cb_priority=10, # Priority for the callback, as it will be
                                    # in the queue like any other task

Every task still runs on the same thread, so that thread-unsafe routines still
work reliably with this new interpreter.

Tasks can either be simple callable, or ``Task`` subclasses. In this second
case, the task is allowed to recursively add new tasks itself, and must signal
its completion by calling ``done()``, which pushes the callback waiting for it
in the queue.

Modules and tasks
=================

Modules are now tasks. The sinks that are to be executed are initially added to
the TaskRunner and then the system is left to run until there is no more task
in the queue.

The base Module class already implements the basic behavior of modules. When
updating, it adds every upstream modules to the queue. When these are done, it
runs its actual code and signals its completion.

Note that if you are changing the behavior of your Module, by redefining
``update()``, ``on_upstream_ready()`` or ``do_compute()``, you'll need to
report the progress on the execution of your module to the logger yourself
(using ``self.logging``).

Multithreading
==============

The parallel capabilities of |vistrails| build on top of this asynchronous
interpreter. Tasks can start some computation in the background and return; if
they do, the TaskRunner will execute other tasks in the meantime. When doing
that, **you must get an AsyncTask** using ``make_async_task()``, so that:

* You can push a task on the TaskRunner's thread when the background
  computation is done (other methods are not thread-safe!).
* The TaskRunner can know tasks are still running in the background. Remember,
  it terminates automatically if no more tasks can be run.

If you want your multithreaded code to actually lower the execution time, you
need to make sure it is started before non-multithreaded tasks are run. This is
achieved via the task priorities.

When a module is first started, it adds its upstream module with the
"update upstream" priority, and adds it's actual computational task with a
less-urgent (i.e. higher) one. This allows every module to register before any
actual code runs. Standard "blocking" modules use the "compute" priority; if
your task is multithreaded, you want to run it with the "compute background"
priority, so that it gets started earlier -- allowing blocking modules to run
at the same time. For instance, you can do:

.. code-block:: python
   :linenos:

   class MyModule(Module):
       COMPUTE_PRIORITY = Module.COMPUTE_BACKGROUND_PRIORITY
       # ...

Parallelization schemes
=======================

|vistrails| provides simple ways of executing your whole module in parallel. It
takes care of dealing with the task system to execute your ``compute()`` method
in parallel for you. To do that, it uses a *parallel scheme*, which is a class
that describes a specific way of executing a module. For instance, there are:

* a 'threading' scheme, that uses standard Python threads to run the module. Be
  advised that because of the restrictions of the CPython interpreter, you
  might not improve performance much by using this type of parallelization: the
  interpreter has a lock, preventing two threads from execution Python code at
  the same time. However code waiting on I/O, network, or thread-enabled
  library functions (such as NumPy_) will benefit from this.
* a 'multiprocessing' scheme, that pushes a |vistrails| module to a different
  process, avoiding the issue of the interpreter lock.
* an 'ipython' scheme, that submits modules to an IPython cluster, allowing you
  to make use of multiple machines. Note that |vistrails| has to be installed
  on every engine.
* an 'ipython-standalone' scheme. This variation is meant to execute on
  clusters where |vistrails| is not available, by injecting the minimum logic
  required to do it. In this case you must be very careful what you use, as
  only the ``compute()`` method will be sent over to the nodes (as bytecode).

Note that, apart from the 'threading' scheme, modules and input/output object
are serialized using the pickle_ module.

For your module to be executed in parallel, you need to declare what kind of
schemes it supports. The base Module class will automatically look at the
available schemes to find the best one (according to their declared *scheme
priority*) that is enabled and the module supports, and use it. This is done
with the ``@parallelizable`` class decorator, on which you can activate each
specific type: threads (on by default), local processes, remote machines.
Should you need to, you can also enable or disable specific schemes:

.. code-block:: python
   :linenos:

   # This enables 'threading' and 'multiprocessing' schemes, disables all
   # remote-executing schemes, but explicitely allows the 'ipython' scheme
   @parallelizable(thread=True, process=True, remote=False,
                   systems={'ipython': True})
   class MyModule(Module):
       def compute(self):
           # ...

The user can then define specific instances of these schemes, called *targets*.
A target is simply the association of a scheme with its required parameters,
stored as key-value annotations in a separate "execution_configuration" file in
the .vt bundle.

.. _NumPy: http://www.numpy.org/
.. _pickle: http://docs.python.org/2/library/pickle.html

Preferred parallelization target
================================

If the ``@parallelizable`` decorator is used, by opposition to some other
runtime parallelization, the supported targets are extracted into the
ModuleDescriptor and the user can assign a specific *preferred target* to each
module. These associations are stored alongside the target configurations, and
shown with different colors on the pipeline view.

This allows the user to override the automatic target selection. Note that if
no preferred target is set, autoselection still happens, unless the
``autoselect`` parameter is set to False on ``@parallelizable``.
