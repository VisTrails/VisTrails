from vistrails.core.configuration import ConfigurationObject

from .identifiers import *


configuration = ConfigurationObject(file_store=(None, str))


def package_requirements():
    from vistrails.core.requirements import require_python_module
    require_python_module('file_archive', {
            'pip': 'file_archive'})
