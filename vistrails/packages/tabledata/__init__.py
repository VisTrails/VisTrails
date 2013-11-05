"""Table data package for VisTrails.

This package contains data extraction and manipulation facilities. It wraps
numpy and csv and allows the use of several file types from VisTrails, with
extraction and conversion routines.

"""

from vistrails.core.packagemanager import get_package_manager

from identifiers import *


def package_dependencies():
    pm = get_package_manager()
    if pm.has_package('org.vistrails.vistrails.spreadsheet'):
        return ['org.vistrails.vistrails.spreadsheet']
    else:
        return []


def package_requirements():
    from vistrails.core.requirements import require_python_module
    require_python_module('csv')
