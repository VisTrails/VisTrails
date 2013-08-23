.. _chap-parallelization:

***************************
Running modules in parallel
***************************

|vistrails| can now run the pipeline in a parallel fashion, provided that
modules support it.

You can enable and configure the available *parallelization schemes* from the
"parallelization" toolbox; each module that supports parallel execution will
automatically choose the best enabled scheme that it supports.

Threading
=========

This basic scheme uses a pool of threads to execute modules. Because of the
restrictions of the CPython interpreter, this might not improve performance
considerably, because plain Python code cannot be run concurrently. However
modules that use the network or thread-enabled libraries will benefit from
this.

Multiprocessing
===============

This is a standard Python library that aims at circumventing the interpreter
lock issue by starting new python processes. Modules that support it will be
able to execute in these separate processes, allowing true parallelism.

IPython
=======

IPython is a Python framework that allows to execute jobs on remote machines.

Setting up an IPython cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This package uses the standard IPython.parallel machinery to execute jobs. You
will need to create and configure the IPython profile that you want |vistrails|
to use.

|vistrails| is capable of running the ``ipcontroller`` and ``ipengine``
commands for you to start a controller or a set of engines locally, but for
more complex setups, you can run ``ipcluster`` yourself from a terminal with
the necessary options.

Interacting with the cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The scheme's tab provides you with the following buttons:

Start new engine processes
    Uses ``ipengine`` to start multiple new workers on the machine, using the
    current IPython profile. These processes will be shutdown on exit, unless
    detached using Cleanup

Show information on the cluster
    Indicates whether we are connected to an IPython controller, the number of
    engines in the cluster, and which processes were started locally. Lists
    some basic information on each engine.

Change profile
    Selects a different IPython profile. Performs cleanup first if a cluster
    was connected.

Cleanup started processes
    Disconnects from the cluster and "forgets" the processes that were started
    from |vistrails|. It is either possible to terminate them, or to leave them
    running in the background (for example, to be reused by the next
    |vistrails| session, or by other machines).

Request cluster shutdown
    Sends the shutdown signal to the controller, regardless of whether it was
    started locally or not. If accepted, the controller will ask every
    connected engine to terminate and exit.

Note that when VisTrails is exited, it will shutdown the engines that it
started. If it started the controller, it will also be shutdown, along with
every engine that might have connected to it from other machines. To prevent
that, use the 'cleanup' button and choose not to stop them; they will detach
from VisTrails and won't be killed automatically. You will still be able to use
the 'cluster shutdown' button explicitely.
