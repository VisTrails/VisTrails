from vistrails.core.vistrail.annotation import Annotation
from vistrails.db.domain import DBExecutionConfiguration, \
    DBExecutionPreference, DBModuleExecutionPreference


class ExecutionPreference(DBExecutionPreference):
    """Execution preference for a given module.
    """
    @staticmethod
    def convert(target):
        if target.__class__ == ExecutionPreference:
            return
        target.__class__ = ExecutionPreference
        for annotation in target.annotations:
            Annotation.convert(annotation)

    id = DBExecutionPreference.db_id
    annotations = DBExecutionPreference.db_annotations
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
    system = DBExecutionPreference.db_system


class ExecutionConfiguration(DBExecutionConfiguration):
    """Execution preferences for the whole workflow.
    """
    _empty_pref = None

    @staticmethod
    def convert(config):
        if config.__class__ == ExecutionConfiguration:
            return
        config.__class__ = ExecutionConfiguration
        for pref in config.execution_preferences:
            ExecutionPreference.convert(pref)

    def get_module_preference(self, ids):
        """get_module_preference(ids: (int,)) -> ExecutionPreference

        Gets the preferences set by the user for the execution of the given
        module.
        ids is a tuple to handle nested modules (i.e. in groups), for example
        (group_id, module_id_in_group).
        """
        ids = ','.join('%d' % i for i in ids)
        try:
            assoc = self.db_get_module_execution_preference_by_module_id(ids)
            r = self.db_get_execution_preference_by_id(assoc.db_preference)
            return r
        except KeyError:
            return None

    def set_module_preference(self, ids, pref):
        """set_module_preference(ids: (int,), ExecutionPreference

        Sets the preferred execution configuration for the given module.
        ids is a tuple to handle nested modules (i.e. in groups), for example
        (group_id, module_id_in_group).
        """
        ids = ','.join('%d' % i for i in ids)
        try:
            assoc = self.db_get_module_execution_preference_by_module_id(ids)
            assoc.execution_preference = pref.id
        except KeyError:
            self.db_add_module_execution_preference(
                    DBModuleExecutionPreference(
                            module_id=ids,
                            preference=pref.id))

    def __nonzero__(self):
        return (bool(self.db_module_execution_preferences) or
                bool(self.execution_preferences))

    execution_preferences = DBExecutionConfiguration.db_execution_preferences
    add_execution_preference = \
            DBExecutionConfiguration.db_add_execution_preference
    delete_execution_preference = \
            DBExecutionConfiguration.db_delete_execution_preference
