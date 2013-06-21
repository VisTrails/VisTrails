.. _chap-parallelflow:

**************************
Parallel Flow in VisTrails
**************************

When dealing with large datasets, the ability to leverage multiple cores or
machines allows to speed up workflow execution time.  VisTrails provides
support for parallelization of tasks using IPython_.

.. _IPython: http://ipython.org/

Setting up an IPython cluster
=============================

This package uses the standard IPython.parallel machinery to execute jobs. You
will need to create and configure the IPython profile that you want |vistrails|
to use.

|vistrails| is capable of running the ``ipcontroller`` and ``ipengine``
commands for you to start a controller or a set of engines locally, but for
more complex setups, you can run ``ipcluster`` yourself from a terminal with
the necessary options.

Interacting with the cluster
============================

In the ``Packages/Parallel Flow`` menu, you will find the following options:

Start new engine processes
    Use ``ipengine`` to start multiple new workers on the machine, using the
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
    running in the background (for example, to be reuse by the next |vistrails|
    session).

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

The ``Map`` module
==================

``Map`` allows you to execute a single module or a ``Group`` in parallel using
input values taken from a list. It works in exactly the same way as the regular
``Map`` module from the :ref:`Control Flow <chap-controlflow>` package.

Contrary to the standard ``Map`` module, the elements of the list will be
submitted to the IPython controller which will execute them in a load-balanced
manner on the engines currently connected.
