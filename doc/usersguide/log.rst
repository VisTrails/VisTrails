.. _chap-log:

***************************
Accessing the Execution Log
***************************

.. index:: log

The code responsible for storing execution information is located in the "core/log" directories, and the code that generates much of that information is in "core/interpreter/cached.py". Modules can add execution-specific annotations to provenance via annotate() calls during execution, but much of the data (like timing and errors) is captured by the LogController and CachedInterpreter (the execution engine) objects. To analyze the log from a vistrail (.vt) file, you might have something like the following::

   import core.log.log
   import db.services.io
 
::

 def run(fname):
  # open the .vt bundle specified by the filename "fname"
  bundle = db.services.io.open_vistrail_bundle_from_zip_xml(fname)[0]
  # get the log filename
  log_fname = bundle.vistrail.db_log_filename
  if log_fname is not None:
      # open the log
      log = db.services.io.open_log_from_xml(log_fname, True)
      # convert the log from a db object
      core.log.log.Log.convert(log)
      for workflow_exec in log.workflow_execs:
          print 'workflow version:', workflow_exec.parent_version
          print 'time started:', workflow_exec.ts_start
          print 'time ended:', workflow_exec.ts_end
          print 'modules executed:', [i.module_id 
                                      for i in workflow_exec.item_execs]
 if __name__ == '__main__':
    run("some_vistrail.vt")

You should be able to see what information is available by looking at the "core/log" classes.