from vistrails.core.vistrail.annotation import Annotation
from vistrails.db.domain import DBExecutionConfiguration, \
    DBExecutionTarget, DBModuleExecutionPreference


class ExecutionTarget(DBExecutionTarget):
    """Execution target description, for modules to use.
    """
    @staticmethod
    def convert(target):
        if target.__class__ == ExecutionTarget:
            return
        target.__class__ = ExecutionTarget
        for annotation in target.annotations:
            Annotation.convert(annotation)

    id = DBExecutionTarget.db_id
    annotations = DBExecutionTarget.db_annotations
    def get_annotation(self, key):
        try:
            return self.db_get_annotation_by_key(key)
        except KeyError:
            return None
    def set_annotation(self, id_scope, key, value):
        try:
            self.db_get_annotation_by_key(key).value = value
        except KeyError:
            ann_id = id_scope.getNewId(Annotation.vtType)
            self.db_add_annotation(Annotation(id=ann_id, key=key, value=value))
    scheme = DBExecutionTarget.db_scheme


localExecutionTarget = ExecutionTarget(id=-1, scheme='')


class ExecutionConfiguration(DBExecutionConfiguration):
    """Execution preferences for the whole workflow.
    """
    @staticmethod
    def convert(config):
        if config.__class__ == ExecutionConfiguration:
            return
        config.__class__ = ExecutionConfiguration
        for target in config.execution_targets:
            ExecutionTarget.convert(target)

    def get_module_preference(self, ids):
        """get_module_preference(ids: (int,)) -> ExecutionTarget

        Gets the preferred execution target set by the user for the execution
        of the given module.
        ids is a tuple to handle nested modules (i.e. in groups), for example
        (group_id, module_id_in_group).
        """
        ids = ','.join('%d' % i for i in ids)
        try:
            assoc = self.db_get_module_execution_preference_by_module_id(ids)
            if assoc.db_target is None:
                return localExecutionTarget
            r = self.db_get_execution_target_by_id(assoc.db_target)
            return r
        except KeyError:
            return None

    def set_module_preference(self, ids, target):
        """set_module_preference(ids: (int,), ExecutionTarget

        Sets the preferred execution target for the given module.
        ids is a tuple to handle nested modules (i.e. in groups), for example
        (group_id, module_id_in_group).
        """
        ids = ','.join('%d' % i for i in ids)

        if target is None:
            # Unset
            try:
                assoc = self.db_get_module_execution_preference_by_module_id(ids)
            except KeyError:
                pass
            else:
                self.db_delete_module_execution_preference(assoc)
            return

        # Set
        if not target.scheme:
            t_id = None
        else:
            t_id = target.id
        try:
            # Change
            assoc = self.db_get_module_execution_preference_by_module_id(ids)
            assoc.db_target = t_id
        except KeyError:
            # Add
            self.db_add_module_execution_preference(
                    DBModuleExecutionPreference(
                            module_id=ids,
                            target=t_id))

    def __nonzero__(self):
        return (bool(self.db_module_execution_preferences) or
                bool(self.execution_targets))

    execution_targets = DBExecutionConfiguration.db_execution_targets
    add_execution_target = \
            DBExecutionConfiguration.db_add_execution_target
    delete_execution_target = \
            DBExecutionConfiguration.db_delete_execution_target
