from vistrails.core.vistrail.annotation import Annotation
from vistrails.db.domain import DBExecutionConfiguration, DBExecutionPreference


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

    annotations = DBExecutionPreference.db_annotations
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
        try:
            pref = self.db_get_module_execution_preference_by_module_id(ids)
            return ExecutionPreference.convert(pref.db_preference)
        except KeyError:
            return None

    def __nonzero__(self):
        return bool(self.db_module_execution_preferences)

    execution_preferences = DBExecutionConfiguration.db_execution_preferences
