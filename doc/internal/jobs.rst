..  _jobs:

Job submission
**************

Job submission is a method for executing external jobs asynchronously and in parallel. The execution engine in VisTrails is currently sequential, but multiple modules can execute in parallel by signaling that the results will be available later; this is done by throwing :class:`~vistrails.core.modules.vistrails_module.ModuleSuspended`, with enough info for VisTrails to retrieve the result later. The job can then continue executing in the background, and VisTrails can resume the workflow execution once the long-running jobs have finished.

When a module suspends, the interpreter will continue to execute other branches until only suspended modules are left. At this point the execution stops, but can be resumed later.

The Job Monitor
---------------

The interpreter records all suspended modules in the :class:`~vistrails.core.vistrail.job.JobMonitor`. The Job Monitor keeps track of all running jobs (with their module-supplied handle) and completed jobs and stores this information with the vistrail. It can check for completion of jobs using the handles.

An improvement to just raising :class:`~vistrails.core.modules.vistrails_module.ModuleSuspended` is to use the JobMonitor directly. This lets you access the job state and do things like: check if the job is running (:meth:`~vistrails.core.vistrail.job.JobMonitor.getJob`), if not start the job (:meth:`~vistrails.core.vistrail.job.JobMonitor.addJob`), ask if the user wants to wait for the job to complete or suspend (JobMonitor.checkJob), check if job has completed and get results (:meth:`~vistrails.core.vistrail.job.JobMonitor.getCache`).

Creating jobs with JobMixin
---------------------------

:class:`~vistrails.core.vistrail.job.JobMixin` is a helper mixin class that handles the job logic while providing you with template methods where the functionality for specific jobs should be implemented. Its main advantage is that it will not execute the upstream of already running jobs, and provides the basic framework for easily re-using the already started or completed job. This is usually the best way to implement jobs.

The Job Monitor GUI
-------------------

When executing a workflow with jobs in the VisTrails GUI, running and completed jobs will be shown in the Job Monitor GUI (:class:`~vistrails.gui.job_monitor.QJobView`). It contains a tree with vistrails/workflows/jobs. The jobs are put in a logical order using module names and submodule order (if jobs are part of groups or list executions). From here jobs can be deleted or force-checked.

Automatic job execution
-----------------------

Jobs can be executed in two modes, which can be toggled in the Job Monitor GUI. Either automatically: jobs will be suspended, polled, and resumed automatically without human intervention; or manually: the user will be asked before suspending workflow execution, and asked again to resume when jobs have finished. The user can then decide to run everything automatically or decide to resume the workflow execution at a later time.

Job Polling
-----------

The job monitor will check jobs at a specified interval that can be set in the Job Monitor GUI. This is done by a handle class provided by either :class:`~vistrails.core.modules.vistrails_module.ModuleSuspended` or :class:`~vistrails.core.vistrail.job.JobMixin`. The job should implement the handle with a ``finished()`` method that knows how to check the job. The handle can also be used for other things like killing the job, or fetch job state information like standard output.

How executions are monitored by JobMonitor
------------------------------------------

For jobs to be monitored, a controller or a JobMonitor needs to be passed to the interpreter. Also, a current workflow needs to be set by calling :meth:`~vistrails.core.vistrail.job.JobMonitor.startWorkflow`. This is because executions can execute subworkflows as sub-executions, but we only want to monitor it at the top level as a single wortkflow. After execution completes :meth:`~vistrails.core.vistrail.job.JobMonitor.finishWorkflow` is called which will update the tree and check the final state of the execution.

Job Monitor execution lock
--------------------------

Since the execution uses a current workflow to record the jobs to only one execution can be running at the same time. This is enforced by setting and clearing :meth:`~vistrails.gui.job_monitor.QJobView.updating_now`. TODO: It should be possible to get rid of this by passing the job_monitor and the current workflow to the interpreter recursively.

Job Types
---------

Jobs are typically tied to a workflow version in the vistrail. But jobs can also be tied to Parameter Explorations and Mashups. Currently, such jobs cannot be resumed automatically and need to be re-executed manually. Jobs will be shared between workflows. Deleting a job in one workflow will delete it from all workflows where it is used.
