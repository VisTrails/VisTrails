.. _chap-parallelization:

***************************
Running modules in parallel
***************************

|vistrails| can now run the pipeline in a parallel fashion, provided that
modules support it.

You can configure *parallelization targets* from the "parallelization" toolbox.
Note that each module has a set of supported target types (called *schemes*) it
supports, so if you can't run a module on the target you want, you might need
to get in touch with the module's developer (or take a look at its source code
yourself).

The parallelization toolbox
===========================

.. _fig-toolbox:

.. figure:: /figures/parallelschemes/toolbox.png
   :height: 3.0in
   :align: center

   The parallelization toolbox

The parallelization toolbox has a list of configured targets for the current
vistrail. In it, you can:

* Enable and disable the 'threading' and 'multiprocessing' schemes. These are
  standard schemes which can only be instanciated once; you cannot have two
  distinct process pools, as that is not actually useful.
* Add other targets: click the "add" button and choose a scheme to add a target
  to the list.
* Delete a target (except for 'threading' and 'multiprocessing') using the "X"
  button in the top-right corner.
* Configure a specific target using its specific controls.

The configuration is stored in the current project, so long as you use the .vt
file format, but is global to every versions in the vistrail. Changing the
configuration does not create new versions.

The colored border around a target is used to show the preferred execution
target of a module in the pipeline view; you can set this preference using the
configuration menu. A parallelizable module can either:

* have no preferred target, in which case one will be selected automatically at
  runtime, unless autoselection has been disabled for it. The corner is then
  white.
* have a preferred target, in which case it will use it. The corner then has
  the same color as the target in the parallelization toolbox.
* have been explicitely opted-out from parallelization, by choosing "local
  execution". The corner is then grey with two black lines.

.. _fig-pipeline

.. figure:: /figures/parallelschemes/pipeline.png
   :height: 1.5in
   :align: center

   Example annotated pipeline

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

There are two variants of IPython executions: the standard onerequires
|vistrails| to be available on the nodes so as to push whole modules there. The
other one, called "standalone", is a workaround that executes modules by
injecting the minimum required code as bytecode on the nodes. It places a lot
of restrictions on what the Module's code can look like, so few modules support
it.

|vistrails| is capable of running the ``ipcontroller`` and ``ipengine``
commands for you to start a controller or a set of engines locally, but for
more complex setups, you can run ``ipcluster`` yourself from a terminal with
the necessary options.

Interacting with the cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The scheme's tab provides you with the following buttons:

Select profile
    Selects an IPython profile.

Show engines
    Lists the engines currently connected to the cluster. Also displays some
    basic information such as whether we are connected and which processes were
    started locally.

Start new engine processes (+)
    Uses ``ipengine`` to start multiple new workers on the machine, using the
    current IPython profile. These processes will be shutdown on exit, unless
    detached using "stop local processes"

Stop local processes
    Disconnects from the cluster and removes the processes that were started
    from |vistrails|. It is either possible to terminate them, or to leave them
    running in the background (for example, to be reused by the next
    |vistrails| session, or by other machines).

Shutdown cluster
    Sends the shutdown signal to the controller, regardless of whether it was
    started locally or not. If accepted, the controller will ask every
    connected engine to terminate and exit.

Note that when VisTrails is exited, it will shutdown the engines that it
started. If it started the controller, it will also be shutdown, along with
every engine that might have connected to it from other machines. To prevent
that, use the 'stop local processes' button and choose not to stop them; they
will detach from VisTrails and won't be killed automatically. You will still be
able to use the 'shutdown cluster' button explicitely.
