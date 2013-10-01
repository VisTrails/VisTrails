from vistrails.core.configuration import ConfigurationObject

from .identifiers import *


configuration = ConfigurationObject(file_store=(None, str))


def package_requirements():
    import vistrails.core.requirements
    if not vistrails.core.requirements.python_module_exists('file_archive'):
        raise vistrails.core.requirements.MissingRequirement('file_archive')
