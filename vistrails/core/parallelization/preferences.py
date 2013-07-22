from vistrails.db.domain import DBExecutionConfiguration, DBExecutionPreference


class ExecutionPreference(DBExecutionPreference):
    """Execution preference for a given module.
    """
    @staticmethod
    def convert(target):
        target.__class__ = ExecutionPreference


class ExecutionConfiguration(DBExecutionConfiguration):
    """Execution preferences for the whole workflow.
    """
    _empty_pref = None

    @staticmethod
    def convert(pref):
        if pref.__class__ == ExecutionConfiguration:
            return
        pref.__class__ = ExecutionConfiguration
        for mod in pref.modules:
            ExecutionPreference.convert(mod)

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
