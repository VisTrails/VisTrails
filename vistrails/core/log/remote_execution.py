from vistrails.core.log.module_exec import ModuleExec
from vistrails.core.log.remote_task import RemoteTask
from vistrails.core.vistrail.annotation import Annotation
from vistrails.db.domain import DBRemoteExecution


class RemoteExecution(DBRemoteExecution):
    """Describes the execution on remote machine(s).

    These are contained in a ModuleExec to log the fact that the module used
    remote machines. A single ModuleExec can have several RemoteExecution
    objects if it performs different operations, but a single operation that
    touches several machine (ex: an IPython map) will only have one entry.

    The RemoteExecution will contain RemoteTask objects describing what was
    done, or ModuleExec objects when the parallelization layer pushed modules
    to be executed elsewhere.

    There are also Annotations there, to store scheme-specific parameters (for
    instance, IPython has a "profile", other schemes might have destination
    addresses, ...).
    """
    def __init__(self, *args, **kwargs):
        DBRemoteExecution.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRemoteExecution.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = RemoteExecution
        return cp

    @staticmethod
    def convert(remote_execution):
        if remote_execution.__class__ == RemoteExecution:
            return
        remote_execution.__class__ = RemoteExecution
        for annotation in remote_execution.annotations:
            Annotation.convert(annotation)
        for module_exec in remote_execution.module_execs:
            ModuleExec.convert(module_exec)
        for remote_task in remote_execution.remote_tasks:
            RemoteTask.convert(remote_task)

    ###########################################################################
    # Properties

    id = DBRemoteExecution.db_id
    annotations = DBRemoteExecution.db_annotations
    module_execs = DBRemoteExecution.db_module_execs
    remote_tasks = DBRemoteExecution.db_remote_tasks
    scheme = DBRemoteExecution.db_scheme
