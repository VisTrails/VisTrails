..  _jobs:

Job submission
**************

Job submission is a method for executing external jobs asynchronously and in parallel.
The execution engine in VisTrails is currently sequential, but multiple workflow branches can be executed in
parallel by suspending each branch by throwing :class:`~vistrails.core.modules.vistrails_module.ModuleSuspended`.
The job will then be executed in the background, and we can resume the workflow execution later once all running
jobs have finished.

When a module is suspended the interpreter will continue to execute other branches
until all branches has either completed or been suspended. At this point the execution
stops, but can be resumed later.

The Job Monitor
---------------
The interpreter records all suspended modules using the :class:`~vistrails.core.vistrail.job.JobMonitor`.
The Job Monitor keeps track of all running and completed jobs and stores this information with the vistrail.

An improvement to just raising ModuleSuspended is to use the JobMonitor directly.
This lets you access the job state and do things like: check if the job is running (`JobMonitor.getJob`),
if not start the job (`JobMonitor.addJob`), ask if the user wants to wait for the job to complete or
suspend (JobMonitor.checkJob), check if job has completed and get results (`JobMonitor.getCache`).

Creating jobs with JobMixin
---------------------------

:class:`~vistrails.core.vistrail.job.JobMixin` is a helper mixin class that handles the job logic
while providing you with template methods where the functionality for specific jobs should be
implemented. Its main advantage is that it will not execute the upstream of already running jobs.
This is usually the best way to implement jobs.

The Job Monitor GUI
-------------------

When executing a workflow with jobs in the VisTrails GUI, running and completed jobs will be shown in the Job Monitor GUI
(:class:`~vistrails.gui.job_monitor.QJobView`). It contains a tree with vistrails/workflows/jobs. The
jobs are put in a logical order using module names and submodule order (if jobs are part of groups or list executions).
From here jobs can be deleted or force-checked.

Automatic job execution
-----------------------

Jobs can be executed in two modes, which can be toggled in the Job Monitor GUI. Either automatically; where jobs
will be suspended, polled, and resumed automatically without human intervention. Or manually; where the user
will be asked before suspending jobs and asked again to resume the workflow when jobs have finished. The user can
then decide to run everything automatically or decide to resume the workflow execution to a later time.

Job Polling
-----------

The job monitor will check jobs at a specified interval that can be set in the Job Monitor GUI.
This is done by a handle class provided by either MioduleSuspended or JobMixin. The job should implement the handle
with a `finished()` method that knows how to check the job. The handle can also be used for other things like killing
the job, or fetch job state information like standard output.

How executions are monitored by JobMonitor
------------------------------------------
For jobs to be monitored, a controller or a JobMonitor needs to be passed to the interpreter. Also,
a current workflow needs to be set by calling `JobMonitor.startWorkflow`. This is because executions can execute
subworkflows as sub-executions, but we only want to monitor it at the top level as a single wortkflow.
After execution completes `JobMonitor.finishWorkflow` is called which will update the tree and check
the final state of the execution.

Job Monitor execution lock
--------------------------
Since the execution uses a current workflow to record the jobs to only one execution can be running at
the same time. This is enforced by setting and clearing `QJobView.updating_now`. TODO: It should be possible to get
rid of this by passing the job_monitor and the current workflow to the interpreter recursively.

Job Types
---------

Jobs are typically tied to a workflow version in the vistrail. But jobs can also be tied to Parameter
Explorations and Mashups. Currently, such jobs cannot be resumed automatically and need to be re-executed manually.
Jobs will be shared between workflows. Deleting a job in one workflow will delete it from all workflows where it is used.