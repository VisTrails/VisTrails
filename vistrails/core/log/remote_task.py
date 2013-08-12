from vistrails.core.vistrail.annotation import Annotation
from vistrails.db.domain import DBRemoteTask


class RemoteTask(DBRemoteTask):
    """Log entry for a task that was performed elsewhere.

    These are contained in a RemoteExecution to keep track of what machine was
    used (with a simple description of the task).

    You can also log more info using Annotations.
    """
    def __init__(self, *args, **kwargs):
        DBRemoteTask.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRemoteTask.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = DBRemoteTask
        return cp

    @staticmethod
    def convert(remote_task):
        if remote_task.__class__ == RemoteTask:
            return
        remote_task.__class__ = RemoteTask
        for annotation in remote_task.annotations:
            Annotation.convert(annotation)

    ###########################################################################
    # Properties

    id = DBRemoteTask.db_id
    annotations = DBRemoteTask.db_annotations
    count = DBRemoteTask.db_count
    description = DBRemoteTask.db_description
    function = DBRemoteTask.db_function
    machine_id = DBRemoteTask.db_machine_id
