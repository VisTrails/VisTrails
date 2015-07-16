.. _chap-tej:

***********************************
Running commands on a remote server
***********************************

The ``tej`` tool provides a way to start job on any remote server through SSH, associate it with an identifier, and monitor its status. When the job is complete, it can download the resulting files through SCP.

In VisTrails, the subpipeline's signature is used as the job identifier. This means that once you have run your pipeline one and the job has been submitted, running it again will match it to the existing job, and will either wait for the job to complete or download the existing results without running it again.

Referencing a queue
===================

The first thing you need to do is setup a ``Queue`` module that indicates which server to connect to (and optionally, where on the filesystem should the jobs be stored).

No setup is required on the server (though VisTrails/tej needs to be able to connect to it via SSH, so you might want to setup public key authentication), the directory will be created on the server with the necessary structure and helpers.

Submitting a job
================

The ``SubmitJob`` module upload a job to a server if it doesn't exist there already (checking for the same subpipeline) and returns a Job object suitable for downloading its results. Regardless of whether the job is created or it already existed, VisTrails will wait for it to complete before carrying on executing your workflow; if you click "cancel" however, it will add the job to the job monitor and keep tabs on the server, alerting you when the job is done so you can resume executing the workflow.

The job is simply a directory that will be uploaded to the server, with a start.sh script that will be executed there (or whatever name is set on the ``script`` input port). Remember to use relative paths in there so that different jobs don't overwrite their files.

A different module, ``SubmitShellJob``, makes it easy to submit a job consisting of a single shell script that you can enter directory in the module configuration window. Its output (stdout, stderr) is downloaded and returned as files on the corresponding output ports.

Downloading output files
========================

You can connect SubmitJob's output to ``DownloadFile`` modules to retrieve generated files from the server and use them in the following steps of your pipeline. The module only needs a ``filename`` parameter, which is relative to the job's directory. The ``DownloadDirectory`` module works in the same way but downloads a whole subdirectory recursively.
