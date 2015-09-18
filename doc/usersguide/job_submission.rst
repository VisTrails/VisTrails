.. _chap-job_submission:

**************
Job Submission
**************

|vistrails| provides a mechanism for running external jobs. This is used for
long-running executions and jobs that are run in parallel. These jobs are
executed asynchronously in the background while the workflow execution suspends
on the client side. The state of running jobs are persisted in the vistrail
file, so that workflows with running jobs can be resumed even after restarting
|vistrails|.

To use the Job mechanism, it needs to be implemented by Modules. |vistrails|
will then detect the jobs and handle it accordingly. Jobs are implemented either
using :ref:`JobMixin <sec-jobmixin>` (recommended) or
:ref:`raising ModuleSuspended directly <sec-modulesuspended>`.


.. note:: To run the examples, first install the example package by copying it from `vistrails/tests/resources/myjob.py` to `~/.vistrails/userpackages` (:vtl:`Or run a workflow that does this automatically <jobsubmission1.vt>`)

.. _sec-monitoring_jobs:

Monitoring Jobs
===============

Jobs are tracked by the Job Monitor when started from the VisTrails GUI. It
keeps track of all jobs and enables you to:

* Check jobs - Checks if the job has completed through the handle mechanism, either the selected workflow/module or all.
* Pause jobs - A paused workflow will not be checked by the timer or `Check All` button.
* View standard output/error for running jobs - If implemented by the handle.
* Delete running workflows/modules.
* Set time interval for automatic job checking.
* Set flag for waiting for job to finish (Automatic job execution).

.. _fig-list_job-monitor:

.. figure:: figures/job_submission/job_monitor.png
   :align: center
   :width: 7in

   The Job Monitor with one running and one finished workflow.

.. _sec-handle:

Job Handles
===========

A handle is used by the the Job Monitor to poll the job. This is a
class instance with a `finished()` method that knows how to check the job.
Below is an example with a simple time condition.

.. code-block:: python

   class TimedJobMonitor(object):
       """ Example that will complete when the specified time have passed

       """
       def __init__(self, start_time, how_long=10):
           self.start_time = start_time
           self.how_long = how_long

       def finished(self):
           return (time.time()-self.start_time) > self.how_long


.. _sec-modulesuspended:

Using ModuleSuspended
=====================

`ModuleSuspended` (found in `vistrails.core.modules.vistrails_module`) is a low-level
method to use the job mechanism. It is mainly used as a simple method to suspend
`PythonSource`s`. (The preferred way is to use :ref:`JobMixin <sec-jobmixin>`). Raising
`ModuleSuspended` will detach the job execution and suspend that branch of the workflow.

A Module that implements a job needs to:

* Check if the job is already running and if not, start it.
* Check if the job has completed, and raise `ModuleSuspended` if it has not.

Raising `ModuleSuspended` will suspend the module execution (unless a flag is set
to wait for each job to finish). Other workflow branches will continue to be executed
until all branches are either suspended or completed, until finally the workflow stops
execution and enter a suspended state.

ModuleSuspended takes a :ref:`handle <sec-handle>` that is used to check the job. Below
is an example using the TimedJobMonitor above. (:vtl:`Open in vistrails <jobsubmission2.vt>`)


.. code-block:: python

    handle = TimedJobMonitor(start_time)
    if not handle.finished():
        raise ModuleSuspended(self, 'Time interval not reached yet.', handle)

.. warning::

   The drawback with this method is that the upstream of the suspended modules will be
   executed each time the workflow is resumed. So make sure the upstream can be executed
   multiple times without creating a new job each time.


.. _sec-jobmixin:

Using JobMixin
==============

`JobMixin` (in `vistrails.core.vistrails.job`) is the preferred method to create job modules.
It exposes a set of methods to implement that is needed to handle the job. One advantage of `JobMixin`
is that it will resume jobs without re-executing the upstream of the module, as opposed to
`ModuleSuspended`. This means the upstream will only be executed once for each job. Below is an
example from the package `MyJobs` (vistrails.packages.myjob). (:vtl:`Open in vistrails <jobsubmission3.vt>`)

.. code-block:: python

    class TimedJob(JobMixin, Module):
        """ A module that suspends until 'how_long' seconds have passed

        """
        _input_ports = [IPort("how_long", "basic:Integer", default=10)]
        _output_ports = [OPort("finished", "basic:Boolean")]

        def job_read_inputs(self):
            """ Implemented by modules to read job parameters from input ports.

            Returns the `params` dictionary used by subsequent methods.
            """
            return {'how_long': self.force_get_input('how_long') or 10}

        def job_start(self, params):
            """ Implemented by modules to submit the job.

            Gets the `params` dictionary and returns a new dictionary, for example
            with additional info necessary to check the status later.
            """

            # this example gets the current time and stores it
            # this time represents the information necessary to check the status of the job

            params['start_time'] = time.time()
            return params

        def job_finish(self, params):
            """ Implemented by modules to get info from the finished job.

            This is called once the job is finished to get the results. These can
            be added to the `params` dictionary that this method returns.

            This is the right place to clean up the job from the server if they are
            not supposed to persist.
            """
            return params

        def job_set_results(self, params):
            """ Implemented by modules to set the output ports.

            This is called after job_finished() or after getting the cached results
            to set the output ports on this module, from the `params` dictionary.
            """
            self.set_output('finished', True)

        def job_get_handle(self, params):
            """ Implemented by modules to return the JobHandle object.

            This returns an object following the JobHandle interface. The
            JobMonitor will use it to check the status of the job and call back
            this module once the job is done.

            JobHandle needs the following method:
              * finished(): returns True if the job is finished
            """
            return TimedJobMonitor(params['start_time'], params['how_long'])
